"""Test API endpoints"""
import sys
from app.main import app
from app.core.database import Base, engine
from app.models import ScanpyJob

# For testing, we'll use requests directly instead of TestClient
import requests
import subprocess
import time
import atexit


def start_test_server():
    """Start uvicorn server for testing"""
    import uvicorn
    import threading
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    return server_thread


def test_api():
    """Test API endpoints"""
    
    print("=" * 60)
    print("API ENDPOINT TESTS")
    print("=" * 60)
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Start test server
    print("\nStarting test server on http://127.0.0.1:8001...")
    start_test_server()
    
    BASE_URL = "http://127.0.0.1:8001"
    
    try:
        # Test 1: Health check
        print("\n[1/6] Testing health check...")
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed")
        print(f"  Version: {data['version']}")
        
        # Test 2: Root endpoint
        print("\n[2/6] Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "Scanpy" in data["message"]
        print(f"✓ Root endpoint working")
        
        # Test 3: List presets
        print("\n[3/6] Testing list presets...")
        response = requests.get(f"{BASE_URL}/api/scanpy/presets")
        assert response.status_code == 200
        data = response.json()
        assert len(data["presets"]) == 2
        assert data["presets"][0]["name"] == "default"
        print(f"✓ Presets endpoint working")
        print(f"  Available: {[p['name'] for p in data['presets']]}")
        
        # Test 4: Submit job with default preset
        print("\n[4/6] Testing job submission (default preset)...")
        response = requests.post(
            f"{BASE_URL}/api/scanpy/jobs/submit",
            json={
                "input_type": "mtx",
                "input_path": "/data/test_data/pbmc_10k",
                "preset": "default"
            }
        )
        assert response.status_code == 201
        job_data = response.json()
        job_id = job_data["id"]
        assert job_data["status"] == "pending"
        assert job_data["preset"] == "default"
        print(f"✓ Job submitted successfully")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {job_data['status']}")
        
        # Test 5: Get job details
        print("\n[5/6] Testing get job...")
        response = requests.get(f"{BASE_URL}/api/scanpy/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["input_type"] == "mtx"
        print(f"✓ Get job working")
        print(f"  Input type: {data['input_type']}")
        print(f"  Progress: {data['progress_percent']}%")
        
        # Test 6: List jobs
        print("\n[6/6] Testing list jobs...")
        response = requests.get(f"{BASE_URL}/api/scanpy/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["jobs"]) >= 1
        print(f"✓ List jobs working")
        print(f"  Total jobs: {data['total']}")
        
        # Cleanup test job
        requests.delete(f"{BASE_URL}/api/scanpy/jobs/{job_id}")
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL API TESTS PASSED ✓✓✓")
        print("=" * 60)
        print("\nAPI server ready!")
        print("Start with: uvicorn app.main:app --reload")
        print("Docs at: http://localhost:8000/docs")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        print("Make sure the test server started correctly")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)