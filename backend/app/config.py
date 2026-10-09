from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartLib - Library Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "smartlib-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    DATABASE_URL: str = "sqlite:///./smartlib.db"
    
    # Library Rules
    FINE_RATE_PER_DAY: float = 5.0  # Rs. 5 per day
    LOAN_PERIOD_DAYS: int = 14
    MAX_RENEWALS: int = 2
    DEFAULT_BORROW_LIMIT: int = 5
    
    # Smart Features
    ENABLE_AI_FEATURES: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
