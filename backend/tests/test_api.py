"""Essential API endpoint tests - focusing on critical functionality"""
import pytest
from uuid import uuid4
from app.models.scanpy import JobStatus


class TestCriticalEndpoints:
    """Test the most critical API functionality"""
    
    def test_health_endpoint(self, client):
        """Ensure API is responsive"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_job_submission_default_preset(self, client, sample_job_data, mock_celery_task):
        """Test core job submission functionality"""
        response = client.post("/api/jobs", json=sample_job_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Critical fields present
        assert "id" in data
        assert data["status"] == "pending"
        assert data["input_type"] == sample_job_data["input_type"]
        assert data["preset"] == "default"
        
        # Verify task was queued
        assert len(mock_celery_task) == 1
        assert mock_celery_task[0]['kwargs']['job_id'] == data["id"]
    
    def test_job_retrieval(self, client, sample_job):
        """Test retrieving submitted jobs"""
        response = client.get(f"/api/jobs/{sample_job.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_job.id)
        assert data["status"] == sample_job.status.value
    
    def test_job_list(self, client, sample_job):
        """Test job listing functionality"""
        response = client.get("/api/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert data["total"] >= 1


class TestJobValidation:
    """Test critical validation to prevent bad data"""
    
    def test_invalid_input_type_rejected(self, client):
        """Ensure invalid input types are rejected"""
        invalid_data = {
            "input_type": "invalid",
            "input_path": "/test/data/test.h5",
            "preset": "default"
        }
        response = client.post("/api/jobs", json=invalid_data)
        assert response.status_code == 422
    
    def test_custom_preset_requires_parameters(self, client):
        """Ensure custom preset validation works"""
        invalid_data = {
            "input_type": "h5",
            "input_path": "/test/data/test.h5",
            "preset": "custom"
            # Missing parameters
        }
        response = client.post("/api/jobs", json=invalid_data)
        assert response.status_code == 422
    
    def test_parameter_range_validation(self, client):
        """Test parameter value validation"""
        invalid_data = {
            "input_type": "h5",
            "input_path": "/test/data/test.h5",
            "preset": "custom",
            "parameters": {
                "min_genes": -100,  # Invalid negative value
                "min_cells": 3,
                "n_genes_lower": 1800,
                "n_genes_upper": 6000,
                "pct_mt_cutoff": 6.0,
                "leiden_resolution": 0.2,
                "n_neighbors": 50,
                "n_pcs": 10
            }
        }
        response = client.post("/api/jobs", json=invalid_data)
        assert response.status_code == 422


class TestErrorHandling:
    """Test error cases that could break the system"""
    
    def test_nonexistent_job_returns_404(self, client):
        """Ensure proper 404 for missing jobs"""
        fake_id = uuid4()
        response = client.get(f"/api/jobs/{fake_id}")
        assert response.status_code == 404
    
    def test_malformed_job_id_handled(self, client):
        """Test malformed UUID handling"""
        response = client.get("/api/jobs/invalid-uuid")
        assert response.status_code == 422  # Pydantic validation error