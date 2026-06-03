"""
Test Celery task integration.

Usage:
    1. Start Redis: docker-compose up -d
    2. Start Celery worker: celery -A app.core.celery_app worker --loglevel=info
    3. Start API: uvicorn app.main:app --reload
    4. Run this script: python test_celery.py
"""
import time
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api"

def test_job_submission():
    """Test submitting a job and monitoring progress."""

    from app.core.config import settings
    
    # Use path from settings
    test_data_path = str(settings.TEST_DATA_DIR / "pbmc3k")
    
    print("=" * 80)
    print("Testing Celery Task Integration")
    print("=" * 80)
    
    # Check if test data exists
    if not Path(test_data_path).exists():
        print(f"\n⚠️  Test data not found at: {test_data_path}")
        print("Please update the path in this script or create test data directory")
        return
    
    # Submit job
    print("\n1. Submitting job...")
    payload = {
        "input_type": "mtx",
        "input_path": test_data_path,
        "preset": "default"
    }
    
    response = requests.post(f"{API_BASE}/scanpy/jobs/submit", json=payload)
    
    if response.status_code != 201:
        print(f"❌ Job submission failed: {response.status_code}")
        print(response.json())
        return
    
    job_data = response.json()
    job_id = job_data["id"]
    print(f"✅ Job submitted: {job_id}")
    print(f"   Status: {job_data['status']}")
    
    # Monitor progress
    print("\n2. Monitoring progress...")
    max_checks = 60  # Wait up to 5 minutes
    check_interval = 5  # seconds
    
    for i in range(max_checks):
        time.sleep(check_interval)
        
        response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}")
        job_data = response.json()
        
        status = job_data["status"]
        progress = job_data["progress_percent"]
        step = job_data["current_step"]
        
        print(f"   [{i*check_interval}s] Status: {status}, Progress: {progress}%, Step: {step}")
        
        if status == "complete":
            print(f"\n✅ Job completed successfully!")
            break
        elif status == "failed":
            print(f"\n❌ Job failed!")
            print(f"   Error: {job_data.get('error_message')}")
            return
    else:
        print(f"\n⚠️  Job still running after {max_checks * check_interval} seconds")
        return
    
    # Get results
    print("\n3. Fetching results...")
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}/results")
    
    if response.status_code != 200:
        print(f"❌ Failed to get results: {response.status_code}")
        print(response.json())
        return
    
    results = response.json()
    
    print(f"\n✅ Results retrieved:")
    print(f"   Stats: {results['stats']}")
    print(f"   Plots: {len(results['plots'])} generated")
    print(f"   Clusters: {len(results['clusters'])} identified")
    
    # List plots
    print("\n4. Generated plots:")
    for plot in results['plots']:
        print(f"   - {plot['plot_type']} ({plot['step']})")
        print(f"     Path: {plot['file_path']}")
    
    # List clusters
    print("\n5. Cluster summary:")
    for cluster in results['clusters']:
        print(f"   - {cluster['cluster_name']}: {cluster['cell_count']} cells")
        if cluster['celltypist_prediction']:
            print(f"     Predicted type: {cluster['celltypist_prediction']}")
    
    print("\n" + "=" * 80)
    print("Test completed successfully! ✅")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_job_submission()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API server")
        print("Make sure the API is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()