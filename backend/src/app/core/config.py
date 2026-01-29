"""
Application Configuration
"""

from typing import List, Any
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "JARVIS"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/jarvis"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://jarvis.vercel.app"]
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Email (IMAP)
    IMAP_HOST: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = ""
    
    # Job Matching
    MIN_SKILL_MATCH_THRESHOLD: float = 0.6
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> List[str]:
        try:
            if isinstance(v, str):
                v = v.strip()
                # Try JSON parsing
                if v.startswith("[") and v.endswith("]"):
                    try:
                         # Handle common user error: single quotes
                        v_fixed = v.replace("'", '"') 
                        return json.loads(v_fixed)
                    except json.JSONDecodeError:
                        pass
                # Fallback to comma separation
                return [i.strip() for i in v.split(",") if i.strip()]
            elif isinstance(v, list):
                return v
        except Exception as e:
            print(f"CORS CONFIG ERROR: {e}. Fallback to wildcard.")
        
        # Absolute fallback to prevent crash
        return ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
