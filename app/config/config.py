from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    api_title: str = "RAG Document Analysis API"
    api_version: str = "1.0.0"
    
    # File Upload Settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".doc"]
    upload_dir: str = "app/uploads"
    
    # Session Settings
    session_timeout_minutes: int = 60
    
    # API Keys
    gemini_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    hf_token: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()