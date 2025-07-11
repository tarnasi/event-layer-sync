from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Layer Sync API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI backend following best practices."
    API_V1_STR: str = "/api/v1"
    
    # Server identification
    SERVER_ID: str = "A"  # A, B, C, D etc.
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    
    # Other servers to sync with
    ALLOWED_SERVERS: List[str] = ["B", "C", "D"]  # Servers this instance should consume from
    
    # Server endpoints for cross-server communication
    SERVER_ENDPOINTS: dict = {
        "A": "http://localhost:8000",
        "B": "http://localhost:8001", 
        "C": "http://localhost:8002",
        "D": "http://localhost:8003"
    }
    
    class Config:
        env_file = ".env"

settings = Settings()
