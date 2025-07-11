from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Database
    PROJECT_NAME: str = "Logistic Distributed System"
    PROJECT_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./logistic.db"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Distributed Logistic System for Event Consumption"
    API_V1_STR: str = "/api/v1"
    
    # RabbitMQ Configuration
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = "shahriyar"
    RABBITMQ_PASSWORD: str = "tarnasi"
    RABBITMQ_VIRTUAL_HOST: str = "/"
    
    # Server Configuration
    SERVER_ID: str = "A"  
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    
    # Distributed System Configuration
    ALLOWED_SERVERS: List[str] = ["B", "C", "D"]  
    
    # Server Endpoints
    SERVER_ENDPOINTS: dict = {
        "A": "http://localhost:8000",
        "B": "http://localhost:8001", 
        "C": "http://localhost:8002",
        "D": "http://localhost:8003"
    }
    
    model_config = SettingsConfigDict(env_file=".env.server_a")

settings = Settings()