"""AI core configuration."""

from typing import Literal, Optional
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """AI-specific settings."""

    # LLM Configuration
    LLM_PROVIDER: Literal["openai", "anthropic", "ollama", "custom"] = "ollama"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "llama2"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    # Embedding Configuration
    EMBEDDING_PROVIDER: Literal["openai", "huggingface", "ollama"] = "ollama"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Vector Database
    VECTOR_DB_PROVIDER: Literal["chroma", "pinecone", "faiss"] = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None

    # RAG Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    MIN_SIMILARITY: float = 0.7

    # Caching
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_TOKENS_PER_MINUTE: int = 100000

    # Cost Control
    DAILY_TOKEN_BUDGET: int = 1000000
    ENABLE_COST_TRACKING: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
