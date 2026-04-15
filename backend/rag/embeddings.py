from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import settings

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        task_type="retrieval_document",
        output_dimensionality=768
    )
