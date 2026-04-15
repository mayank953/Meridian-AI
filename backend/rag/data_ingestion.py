import os
import tempfile
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google.cloud import storage
from config.settings import settings
from rag.vector_store import vector_store
from logger import GLOBAL_LOGGER as log

def ingest_data_from_gcs():
    """Loads PDFs from a GCS bucket, extracts text, splits it, and stores it."""
    log.info("Connecting to GCS bucket", bucket=settings.GCS_BUCKET_NAME)

    try:
        client = storage.Client(project=settings.GCP_PROJECT)
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blobs = list(bucket.list_blobs(prefix=settings.GCS_PREFIX))
    except Exception as e:
        log.error("Failed to connect to GCS bucket", error=str(e))
        raise

    # Use a temp directory so files are not locked during processing
    tmp_dir = tempfile.mkdtemp()
    documents = []

    try:
        for blob in blobs:
            if blob.name.endswith(".pdf"):
                local_path = os.path.join(tmp_dir, os.path.basename(blob.name))
                blob.download_to_filename(local_path)
                loader = PyPDFLoader(local_path)
                docs = loader.load()
                log.info("Loaded PDF from GCS", blob=blob.name, pages=len(docs))
                # Preserve the original GCS source in metadata
                for doc in docs:
                    doc.metadata["source"] = f"gs://{settings.GCS_BUCKET_NAME}/{blob.name}"
                documents.extend(docs)
    finally:
        # Clean up temp files after all processing is done
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if not documents:
        log.warning("No documents found in the specified bucket/prefix")
        return

    log.info("Successfully loaded pages from GCS", pages=len(documents))

    try:
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
        chunks = text_splitter.split_documents(documents)
        log.info("Split documents into chunks", chunks=len(chunks))
    except Exception as e:
        log.error("Failed to split documents", error=str(e))
        raise

    try:
        # Embed and store in Vertex AI Vector Search
        log.info("Embedding chunks and pushing to Vertex AI Vector Search")
        vector_store.add_documents(chunks)
        log.info("Ingestion complete")
    except Exception as e:
        log.error("Failed to ingest chunks to Vector Search", error=str(e))
        raise

