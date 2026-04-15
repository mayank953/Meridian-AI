from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.llm_model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )
