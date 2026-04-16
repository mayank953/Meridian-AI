from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from config.settings import settings
from datetime import datetime 
from agent.agents import ProcurementSupervisor
from api.schemas import (AuditRequest,AuditResponse,QueryRequest,QueryResponse)
from rag.data_ingestion import ingest_data_from_gcs
from rag.vector_store import vector_store
from rag.llm import get_llm
from logger import GLOBAL_LOGGER as log

rag_llm = get_llm()
import sys, platform, traceback, tempfile, os, shutil

# LangChain / Pipeline Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from google.cloud import storage


health_router = APIRouter(prefix="/api",tags=["Health"])
status_router = APIRouter(prefix="/api",tags=["Status"])
agent_router  = APIRouter(prefix="/api/agent",tags=["Agent"])
rag_router = APIRouter(prefix="/api/rag",tags=["RAG"])

# In-memory upload tracker (reset on restart)
_upload_history: list[dict] = []
_server_start_time = datetime.utcnow()

supervisor = ProcurementSupervisor()

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@health_router.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# System Status
# ---------------------------------------------------------------------------

@status_router.get("/status")
def system_status():
    """Return real-time system configuration and health information."""
    

    uptime_seconds = int((datetime.utcnow() - _server_start_time).total_seconds())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Try to pull index / endpoint IDs from the vector_store internals
    try:
        index_id = vector_store._searcher._index.resource_name
    except Exception:
        index_id = "NA"

    try:
        endpoint_id = vector_store._searcher._index_endpoint.resource_name
    except Exception:
        endpoint_id = "NA"

    return {
        "backend": {
            "status": "healthy",
            "uptime": f"{hours:02d}h {minutes:02d}m {seconds:02d}s",
            "python_version": sys.version.split()[0],
            "platform": platform.system(),
        },
        "gcp": {
            "project_id": settings.GCP_PROJECT,
            "region": settings.GCP_REGION,
        },
        "storage": {
            "gcs_bucket": settings.GCS_BUCKET_NAME,
            "gcs_prefix": settings.GCS_PREFIX,
        },
        "vector_search": {
            "index_id": index_id,
            "endpoint_id": endpoint_id,
            "stream_update": True,
        },
        "models": {
            "embedding": settings.embedding_model_name,
            "llm": settings.llm_model_name,
            "llm_framework": "Vertex AI / LangChain",
        },
        "ingestion": {
            "uploads_this_session": len(_upload_history),
        },
    }

# ============================================================
# AGENT  endpoints
# ============================================================

@agent_router.post("/audit", response_model=AuditResponse)
def run_audit(payload: AuditRequest):
    """Run the full multi-agent procurement audit and return all phase results."""
    try:
        result = supervisor.run_audit(payload.request_text)
        return AuditResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# ============================================================
# RAG  endpoints
# ============================================================


@rag_router.post("/ask", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    """Query the RAG pipeline (Vertex AI Vector Search + Gemini)."""
    try:
        # Configure Base Retriever
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # Route Selection
        if payload.retriever_type == "contextual":
            # Using Contextual Compression as a high-quality retrieval strategy
            # This fetches k=10 and uses Gemini to 'refine' / 'compress' the documents
            compressor = LLMChainExtractor.from_llm(rag_llm)
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=vector_store.as_retriever(search_kwargs={"k": 10})
            )
        elif payload.retriever_type == "multiquery":
            
            log.info("Using MultiQuery retriever strategy")
            retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=rag_llm)
        else:
            retriever = base_retriever

        # Note: 'mmr' requested but falling back to similarity if backend lacks implementation
        # The UI still shows MMR, but it will use similarity search for stability.

        system_prompt = (
            "You are a helpful assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer based on the context, say that you don't know. "
            "Keep the answer concise and accurate."
            "\n\n"
            "Context: {context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(rag_llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        response = rag_chain.invoke({"input": payload.query})

        return QueryResponse(answer=response["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DOCUMENT UPLOAD  endpoint  (local PDF → Vector Search)
# ============================================================

@rag_router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Accept one or more PDF uploads, chunk them, embed with Vertex AI,
    and push into the existing Vector Search index.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    results = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for upload in files:
            if not upload.filename.lower().endswith(".pdf"):
                results.append({
                    "filename": upload.filename,
                    "status": "skipped",
                    "reason": "Only PDF files are supported.",
                })
                continue

            # Save to temp location (must use await to read async UploadFile correctly)
            local_path = os.path.join(tmp_dir, upload.filename)
            contents = await upload.read()
            with open(local_path, "wb") as f:
                f.write(contents)

            # Upload original PDF to GCS under uploads/ so it's persisted in the bucket
            try:
                
                
                gcs_client = storage.Client(project=settings.GCP_PROJECT)
                bucket = gcs_client.bucket(settings.GCS_BUCKET_NAME)
                gcs_path = f"{settings.GCS_PREFIX}{upload.filename}"
                blob = bucket.blob(gcs_path)
                blob.upload_from_filename(local_path, content_type="application/pdf")
                log.info("File saved to GCS", filename=upload.filename, gcs_path=f"gs://{settings.GCS_BUCKET_NAME}/{gcs_path}")
            except Exception as gcs_err:
                log.warning("Could not save to GCS", error=str(gcs_err))

            # Load & split
            loader = PyPDFLoader(local_path)
            docs = loader.load()
            log.info("PDF pages loaded", filename=upload.filename, pages=len(docs))

            for doc in docs:
                doc.metadata["source"] = f"upload://{upload.filename}"

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
            )
            chunks = text_splitter.split_documents(docs)
            log.info("Chunks created", filename=upload.filename, chunks=len(chunks))

            if not chunks:
                log.warning("No chunks extracted, skipping indexing", filename=upload.filename)
                results.append({
                    "filename": upload.filename,
                    "status": "skipped",
                    "reason": "No extractable text found in PDF (may be a scanned/image-based PDF).",
                })
                continue

            # Embed & store
            log.info("Ingesting chunks into Vector Search", filename=upload.filename, chunks=len(chunks))
            vector_store.add_documents(chunks)
            log.info("Successfully ingested chunks", filename=upload.filename, chunks=len(chunks))

            results.append({
                "filename": upload.filename,
                "status": "ingested",
                "pages": len(docs),
                "chunks": len(chunks),
            })
    except Exception as e:
        tb = traceback.format_exc()
        log.error("Upload failed", traceback=tb)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    _upload_history.extend(results)
    return {"results": results}


@rag_router.get("/uploads")
def list_uploads():
    """Return the history of uploaded documents (in-memory, resets on restart)."""
    return {"uploads": _upload_history}


@rag_router.post("/ingest-gcs")
def trigger_gcs_ingestion():
    """Trigger the original GCS-based ingestion from rag.py."""
    try:
        ingest_data_from_gcs()
        return {"status": "GCS ingestion complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
