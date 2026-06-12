import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google.cloud import storage
from config.settings import settings
from rag.vector_store import vector_store
from logger import GLOBAL_LOGGER as log

def ingest_data_from_gcs():
    """Loads PDFs from a GCS bucket, extracts text, splits it, and stores it."""
    log.info("Connecting to GCS bucket", bucket=settings.GCS_BUCKET_NAME)

    client = storage.Client(project=settings.GCP_PROJECT)
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=settings.GCS_PREFIX))

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
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if not documents:
        log.warning("No documents found in the specified bucket/prefix")
        return

    log.info("Successfully loaded pages from GCS", pages=len(documents))

    # Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(docs)

    # DEBUG START
    from rag.embeddings import get_embeddings

    emb = get_embeddings()

    texts = [c.page_content for c in chunks]

    vectors = emb.embed_documents(texts)

    print("=" * 80)
    print(f"CHUNKS COUNT: {len(chunks)}")
    print(f"TEXTS COUNT: {len(texts)}")
    print(f"EMBEDDINGS COUNT: {len(vectors)}")
    print("=" * 80)
    # DEBUG END

    log.info("Split documents into chunks", chunks=len(chunks))

    # Embed and store in Vertex AI Vector Search
    log.info("Embedding chunks and pushing to Vertex AI Vector Search")
    try:
        vector_store.add_documents(chunks)
    except Exception as e:
        import traceback

        print("=" * 100)
        print("VECTOR STORE FAILURE")
        print("ERROR:", str(e))
        print(traceback.format_exc())
        print("=" * 100)

    raise    
    log.info("Ingestion complete")

