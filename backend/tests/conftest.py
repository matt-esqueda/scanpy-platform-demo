import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.models.scanpy import ScanpyJob, JobStatus
from app.core.config import settings

# Use PostgreSQL test database (Docker)
SQLALCHEMY_TEST_DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/test_scanpy_db"
)

# Create test engine
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database tables before any tests run"""
    print("🔧 Setting up test database tables...")
    Base.metadata.create_all(bind=engine)
    yield
    print("🧹 Cleaning up test database...")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Clean database after each test"""
    yield
    # Clean up all data after each test
    db_session.query(ScanpyJob).delete()
    db_session.commit()


@pytest.fixture
def sample_job(db_session):
    """Create a sample job for testing."""
    job = ScanpyJob(
        status=JobStatus.PENDING,
        progress_percent=0,
        current_step="pending",
        input_type="mtx",
        input_path="test/data/path",
        preset="default",
        parameters={"min_genes": 200, "min_cells": 3},
        output_dir="/tmp/test",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def sample_job_data():
    """Standard job submission data"""
    return {
        "input_type": "h5",
        "input_path": "/test/data/pbmc3k.h5",
        "preset": "default"
    }


@pytest.fixture
def mock_celery_task(monkeypatch):
    """Mock Celery task execution to avoid running real analysis"""
    executed_tasks = []
    
    def mock_apply_async(*args, **kwargs):
        task_id = f"test-task-{len(executed_tasks)}"
        executed_tasks.append({
            'task_id': task_id,
            'args': args,
            'kwargs': kwargs
        })
        
        class MockResult:
            def __init__(self, task_id):
                self.id = task_id
                self.state = "PENDING"
            
            def get(self, timeout=None):
                return "SUCCESS"
        
        return MockResult(task_id)
    
    from app.tasks.scanpy_tasks import run_scanpy_analysis
    monkeypatch.setattr(run_scanpy_analysis, 'apply_async', mock_apply_async)
    
    return executed_tasks