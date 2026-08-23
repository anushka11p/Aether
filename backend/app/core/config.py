from pathlib import Path
from pydantic_settings import BaseSettings

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    PROJECT_NAME: str = "Aether"
    AETHER_API_KEY: str = ""

    class Config:
        env_file = str(ENV_PATH)

settings = Settings()
