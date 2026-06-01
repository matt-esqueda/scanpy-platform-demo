"""Initialize database tables"""
from app.core.database import engine, Base
from app.models import ScanpyJob, ScanpyPlot, ScanpyCluster


def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    print("\nCreated tables:")
    print("  - scanpy_jobs")
    print("  - scanpy_plots")
    print("  - scanpy_clusters")


if __name__ == "__main__":
    init_db()