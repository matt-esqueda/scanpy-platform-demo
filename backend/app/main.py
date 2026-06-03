"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import scanpy

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Web-based single-cell RNA-seq analysis platform using Scanpy",
    docs_url="/docs",
    redoc_url="/redoc"
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