from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.session import init_db
from app.core.rabbitmq import rabbitmq
from app.core.middleware import ReplicationMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    init_db()
    logger.info("Database initialized")
    
    # Try to connect to RabbitMQ (optional - will work without it)
    if rabbitmq.connect():
        logger.info("Connected to RabbitMQ")
    else:
        logger.warning("Could not connect to RabbitMQ - events will not be published")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    rabbitmq.disconnect()

app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Server {settings.SERVER_ID}",
    version=settings.VERSION,
    description=f"{settings.DESCRIPTION} - Event-driven logistic system with RabbitMQ (Server {settings.SERVER_ID})",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(ReplicationMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
