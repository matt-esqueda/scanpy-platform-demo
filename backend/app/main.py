"""FastAPI application entry point"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import scanpy, websocket

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Start WebSocket Redis listener
    from app.core.websocket import manager

    print("🚀 STARTING WebSocket manager Redis listener...")
    
    # Create background task for Redis pub/sub listener
    listener_task = asyncio.create_task(manager.listen_for_updates())
    
    print("✅ WebSocket manager listener task created")
    logger.info("WebSocket manager started")

    yield

    # Shutdown: Cancel listener and close Redis
    print("🛑 STOPPING WebSocket manager...")
    listener_task.cancel()
    await manager.close()
    print("✅ WebSocket manager stopped")
    logger.info("Websocket manager stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Web-based single-cell RNA-seq analysis platform using Scanpy",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware (for frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],       # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scanpy.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router)


# Health check endpoint
@app.get("/health")
def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Scanpy Analysis Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }