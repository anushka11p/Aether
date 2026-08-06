from langchain_groq import ChatGroq
from app.core.config import settings

def get_llm(temperature: float = 0.3):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=temperature,
    )