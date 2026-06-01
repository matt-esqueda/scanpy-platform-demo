"""Test database connection and CRUD operations"""
from app.core.database import SessionLocal, engine
from app.models import ScanpyJob, JobStatus
from sqlalchemy import text
import sys


def test_connection():
    """Test database connection and basic operations"""
    
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Test 1: Raw connection
    print("\n[1/4] Testing raw database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version[:50]}...")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    
    # Test 2: Create tables
    print("\n[2/4] Creating tables...")
    try:
        from app.core.database import Base
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False
    
    # Test 3: Insert test record
    print("\n[3/4] Testing INSERT operation...")
    try:
        db = SessionLocal()
        
        test_job = ScanpyJob(
            input_type="mtx",
            input_path="/test/path",
            preset="default",
            parameters={"min_genes": 200, "min_cells": 3},
            output_dir="/test/output"
        )
        db.add(test_job)
        db.commit()
        db.refresh(test_job)
        
        job_id = test_job.id
        print(f"✓ Created test job")
        print(f"  ID: {job_id}")
        print(f"  Status: {test_job.status.value}")
        print(f"  Created: {test_job.created_at}")
        
    except Exception as e:
        print(f"✗ Insert failed: {e}")
        db.close()
        return False
    
    # Test 4: Query and delete
    print("\n[4/4] Testing SELECT and DELETE operations...")
    try:
        # Query
        retrieved = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if retrieved is None:
            print("✗ Failed to retrieve test job")
            return False
        
        print(f"✓ Retrieved job {retrieved.id}")
        print(f"  Parameters: {retrieved.parameters}")
        
        # Delete
        db.delete(retrieved)
        db.commit()
        print(f"✓ Deleted test job")
        
        # Verify deletion
        check = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if check is not None:
            print("✗ Job still exists after deletion")
            return False
        
        print("✓ Verified deletion")
        
    except Exception as e:
        print(f"✗ Query/Delete failed: {e}")
        return False
    finally:
        db.close()
    
    # Success
    print("\n" + "=" * 60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 60)
    print("\nDatabase is ready for development!")
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)