from langchain_google_vertexai import VectorSearchVectorStore
from config.settings import settings
from rag.embeddings import get_embeddings
from google.cloud import aiplatform

# Initialize Vertex AI SDK
aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_REGION)

def get_vector_store():

    # Initialize the embedding model (Vertex AI Enterprise versions)
    embeddings = get_embeddings()

    store = VectorSearchVectorStore.from_components(
        project_id=settings.GCP_PROJECT,
        region=settings.GCP_REGION,
        embedding=embeddings,  # NOTE: singular "embedding", not "embeddings"
        index_id=settings.vector_search_index_id,
        endpoint_id=settings.vector_search_index_endpoint_id,
        gcs_bucket_name=settings.GCS_BUCKET_NAME,
        stream_update=True,
    )

    return store

# Create a module-level instance so importers get a ready-to-use object
vector_store = get_vector_store()