"""Test database operations and business logic directly"""
import pytest
from app.models.scanpy import ScanpyJob, JobStatus
from app.schemas.scanpy import ScanpyParameters, JobSubmitRequest


class TestDatabaseBasics:
    """Test basic database operations"""
    
    def test_create_job(self, db_session):
        """Test creating a job in the database"""
        job = ScanpyJob(
            status=JobStatus.PENDING,
            input_type="h5",
            input_path="/test/data/test.h5",
            preset="default",
            parameters={"min_genes": 200, "min_cells": 3},
            output_dir="/test/output",
            progress_percent=0
        )
        
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        
        # Test job was created successfully
        assert job.id is not None
        assert job.status == JobStatus.PENDING
        assert job.progress_percent == 0
        
        print(f"✅ Created job with ID: {job.id}")
    
    def test_job_status_updates(self, db_session, sample_job):
        """Test updating job status"""
        # Start as pending
        assert sample_job.status == JobStatus.PENDING
        
        # Update to executing
        sample_job.status = JobStatus.EXECUTING
        sample_job.progress_percent = 50
        
        db_session.commit()
        db_session.refresh(sample_job)
        
        assert sample_job.status == JobStatus.EXECUTING
        assert sample_job.progress_percent == 50
        
        print(f"✅ Updated job status to: {sample_job.status}")


class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_valid_job_request(self, sample_job_data):
        """Test valid job request validation"""
        request = JobSubmitRequest(**sample_job_data)
        
        assert request.input_type == "h5"
        assert request.preset == "default"
        
        print("✅ Valid job request validated successfully")
    
    def test_invalid_parameter_ranges(self):
        """Test parameter validation catches invalid ranges"""
        with pytest.raises(ValueError):
            ScanpyParameters(
                min_genes=200,
                min_cells=3,
                n_genes_lower=6000,  # Higher than upper
                n_genes_upper=1800,  # Lower than lower - should fail
                pct_mt_cutoff=6.0,
                leiden_resolution=0.2,
                n_neighbors=50,
                n_pcs=10
            )
        
        print("✅ Invalid parameter ranges properly rejected")
    
    def test_create_multiple_jobs(self, db_session):
        """Test creating multiple jobs"""
        jobs = []
        for i in range(3):
            job = ScanpyJob(
                status=JobStatus.PENDING,
                input_type="h5",
                input_path=f"/test/data/test_{i}.h5",
                preset="default",
                parameters={"min_genes": 200},
                output_dir=f"/test/output_{i}",
                progress_percent=i * 10
            )
            db_session.add(job)
            jobs.append(job)
        
        db_session.commit()
        
        # Query all jobs
        all_jobs = db_session.query(ScanpyJob).all()
        assert len(all_jobs) == 3
        
        print(f"✅ Successfully created {len(all_jobs)} jobs")