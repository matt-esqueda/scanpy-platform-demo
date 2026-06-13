from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # App
    PROJECT_NAME: str = "Scanpy Analysis Platform"
    VERSION: str = "0.2.1"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "scanpy_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "scanpy_pass")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "scanpy_db")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis (for Celery)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
    JOBS_DIR: Path = DATA_DIR / "jobs"
    TEST_DATA_DIR: Path = DATA_DIR / "test_data"
    
    # Performance
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))
    JOB_TIMEOUT_SECONDS: int = int(os.getenv("JOB_TIMEOUT_SECONDS", "3600"))  # 1 hour
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instantiate settings
settings = Settings()

# Ensure directories exist
settings.JOBS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Production warnings
if settings.ENVIRONMENT == "production":
    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set for production")
    if settings.DEBUG:
        raise ValueError("DEBUG must be False for production")