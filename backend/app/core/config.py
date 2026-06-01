from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # App
    PROJECT_NAME: str = "Scanpy Analysis Platform"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    POSTGRES_USER: str = "scanpy_user"
    POSTGRES_PASSWORD: str = "scanpy_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "scanpy_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis (for Celery)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    JOBS_DIR: Path = DATA_DIR / "jobs"
    TEST_DATA_DIR: Path = DATA_DIR / "test_data"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instantiate settings
settings = Settings()

# Ensure directories exist
settings.JOBS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)