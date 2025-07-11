from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Layer Sync API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI backend following best practices."
    API_V1_STR: str = "/api/v1"

settings = Settings()
