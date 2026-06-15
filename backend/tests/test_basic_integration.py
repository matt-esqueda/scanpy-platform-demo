"""Basic integration tests for critical user flows"""
import pytest
from app.models.scanpy import JobStatus


class TestJobSubmissionFlow:
    """Test complete job submission and retrieval flow"""
    
    def test_submit_and_retrieve_job(self, client, sample_job_data, mock_celery_task):
        """Test full job submission and retrieval cycle"""
        # 1. Submit job
        submit_response = client.post("/api/jobs", json=sample_job_data)
        assert submit_response.status_code == 201
        
        job_data = submit_response.json()
        job_id = job_data["id"]
        
        # 2. Retrieve the job
        get_response = client.get(f"/api/jobs/{job_id}")
        assert get_response.status_code == 200
        
        retrieved_job = get_response.json()
        assert retrieved_job["id"] == job_id
        assert retrieved_job["status"] == "pending"
        
        # 3. Verify job appears in list
        list_response = client.get("/api/jobs")
        assert list_response.status_code == 200
        
        job_list = list_response.json()
        job_ids = [job["id"] for job in job_list["jobs"]]
        assert job_id in job_ids
        
        # 4. Verify Celery task was queued
        assert len(mock_celery_task) == 1
        assert mock_celery_task[0]['kwargs']['job_id'] == job_id


class TestPresetFlow:
    """Test preset-related functionality"""
    
    def test_preset_list_and_usage(self, client, mock_celery_task):
        """Test getting presets and using them"""
        # 1. Get available presets
        presets_response = client.get("/api/presets")
        assert presets_response.status_code == 200
        
        presets_data = presets_response.json()
        assert "presets" in presets_data
        assert len(presets_data["presets"]) >= 2
        
        # 2. Use a specific preset
        job_data = {
            "input_type": "h5",
            "input_path": "/test/data/test.h5",
            "preset": "stringent"
        }
        
        submit_response = client.post("/api/jobs", json=job_data)
        assert submit_response.status_code == 201
        
        job = submit_response.json()
        assert job["preset"] == "stringent"
        # Verify stringent parameters were applied
        assert job["parameters"]["min_genes"] == 500
        assert job["parameters"]["pct_mt_cutoff"] == 5.0


class TestErrorScenarios:
    """Test how the system handles error scenarios"""
    
    def test_database_constraint_handling(self, client, db_session):
        """Test database constraints are properly enforced"""
        from app.models.scanpy import ScanpyJob
        
        # This should work fine
        valid_job_data = {
            "input_type": "h5",
            "input_path": "/test/data/test.h5", 
            "preset": "default"
        }
        
        response = client.post("/api/jobs", json=valid_job_data)
        assert response.status_code == 201
        
        # Test database handles required fields
        job = ScanpyJob(
            status=JobStatus.PENDING,
            # Missing required fields should be caught by Pydantic/SQLAlchemy
        )
        
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            db_session.add(job)
            db_session.commit()