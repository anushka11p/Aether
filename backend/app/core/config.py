from pathlib import Path
from pydantic_settings import BaseSettings

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    PROJECT_NAME: str = "Aether"
    AETHER_API_KEY: str = ""

    class Config:
        env_file = str(ENV_PATH)

settings = Settings()
