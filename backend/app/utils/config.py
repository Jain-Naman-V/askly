from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_uri: str = "mongodb://localhost:27017"  # Alternative env var name
    mongodb_db_name: str = "ai_data_agent"
    mongodb_collection_name: str = "structured_data"
    
    def get_mongodb_url(self) -> str:
        """Get MongoDB URL, preferring mongodb_uri over mongodb_url"""
        return self.mongodb_uri if self.mongodb_uri != "mongodb://localhost:27017" else self.mongodb_url
    
    # Groq API Configuration
    groq_api_key: str = ""
    groq_model: str = "llama3-70b-8192"
    
    # FastAPI Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Search Configuration
    vector_dimension: int = 1536
    search_limit: int = 50
    similarity_threshold: float = 0.7
    max_search_results: int = 100
    
    # Security
    secret_key: str = "your_secret_key_here_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # Cache Configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields instead of raising errors

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()