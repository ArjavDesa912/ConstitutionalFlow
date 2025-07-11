import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/constitutional_flow")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")
    
    # Application Settings
    APP_NAME: str = "ConstitutionalFlow"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # API Rate Limits
    OPENAI_RATE_LIMIT: int = int(os.getenv("OPENAI_RATE_LIMIT", "100"))
    ANTHROPIC_RATE_LIMIT: int = int(os.getenv("ANTHROPIC_RATE_LIMIT", "100"))
    COHERE_RATE_LIMIT: int = int(os.getenv("COHERE_RATE_LIMIT", "100"))
    
    # Cost Control
    DAILY_BUDGET_LIMIT: float = float(os.getenv("DAILY_BUDGET_LIMIT", "100.0"))
    MONTHLY_BUDGET_LIMIT: float = float(os.getenv("MONTHLY_BUDGET_LIMIT", "1000.0"))
    
    # Performance Settings
    MAX_CONCURRENT_TASKS: int = int(os.getenv("MAX_CONCURRENT_TASKS", "1000"))
    TASK_TIMEOUT_SECONDS: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "300"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings() 