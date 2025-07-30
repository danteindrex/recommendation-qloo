from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/culturaldb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"
    
    # Passkey/WebAuthn
    RP_ID: str = "localhost"  # Relying Party ID
    RP_NAME: str = "CulturalOS"
    RP_ORIGIN: str = "http://localhost:3000"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"]
    
    # External APIs
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Social Media APIs
    INSTAGRAM_CLIENT_ID: str = ""
    INSTAGRAM_CLIENT_SECRET: str = ""
    TIKTOK_CLIENT_ID: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    
    # AI Services - Gemini is REQUIRED
    QLOO_API_KEY: str = ""
    QLOO_CLIENT_ID: str = ""
    GEMINI_API_KEY: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    @field_validator('GEMINI_API_KEY')
    @classmethod
    def validate_gemini_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("GEMINI_API_KEY is required and cannot be empty. Please set your Gemini API key in the .env file.")
        return v.strip()
    
    # For backward compatibility
    @property
    def GOOGLE_GEMINI_API_KEY(self) -> str:
        return self.GEMINI_API_KEY
    
    class Config:
        env_file = "../.env"


settings = Settings()