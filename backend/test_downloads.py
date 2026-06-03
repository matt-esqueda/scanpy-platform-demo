"""
Test file download endpoints.

Prerequisites:
    1. Have a completed job (run test_celery.py first)
    2. API server running: uvicorn app.main:app --reload

Usage:
    python test_downloads.py <job_id>
"""
import sys
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api"


def test_downloads(job_id: str):
    """Test all download endpoints for a job."""
    
    print("=" * 80)
    print(f"Testing File Downloads for Job: {job_id}")
    print("=" * 80)
    
    # Create downloads directory
    download_dir = Path("test_downloads")
    download_dir.mkdir(exist_ok=True)
    
    # 1. Test H5AD download
    print("\n1. Testing H5AD download...")
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}/download/h5ad")
    
    if response.status_code == 200:
        h5ad_file = download_dir / f"results_{job_id}.h5ad"
        h5ad_file.write_bytes(response.content)
        print(f"   ✅ Downloaded H5AD: {h5ad_file} ({len(response.content):,} bytes)")
    else:
        print(f"   ❌ H5AD download failed: {response.status_code}")
        print(f"      {response.json()}")
    
    # 2. Test CSV download
    print("\n2. Testing cluster CSV download...")
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}/download/clusters")
    
    if response.status_code == 200:
        csv_file = download_dir / f"clusters_{job_id}.csv"
        csv_file.write_bytes(response.content)
        print(f"   ✅ Downloaded CSV: {csv_file} ({len(response.content):,} bytes)")
        
        # Show CSV contents
        print(f"\n   CSV Preview:")
        for line in csv_file.read_text().split('\n')[:5]:
            print(f"      {line}")
    else:
        print(f"   ❌ CSV download failed: {response.status_code}")
        print(f"      {response.json()}")
    
    # 3. Test plot downloads
    print("\n3. Testing plot downloads...")
    
    # Get job results to find plot IDs
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}/results")
    
    if response.status_code == 200:
        results = response.json()
        plots = results.get('plots', [])
        
        print(f"   Found {len(plots)} plots")
        
        # Download first 3 plots as examples
        for i, plot in enumerate(plots[:3]):
            plot_id = plot['id']
            plot_type = plot['plot_type']
            
            response = requests.get(f"{API_BASE}/scanpy/plots/{plot_id}")
            
            if response.status_code == 200:
                plot_file = download_dir / f"{plot_type}_{job_id}.png"
                plot_file.write_bytes(response.content)
                print(f"   ✅ Downloaded plot {i+1}/{len(plots[:3])}: {plot_type} ({len(response.content):,} bytes)")
            else:
                print(f"   ❌ Plot download failed: {response.status_code}")
    else:
        print(f"   ❌ Failed to get results: {response.status_code}")
    
    # 4. Test ZIP archive download
    print("\n4. Testing ZIP archive download...")
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}/download/archive")
    
    if response.status_code == 200:
        zip_file = download_dir / f"results_{job_id}.zip"
        zip_file.write_bytes(response.content)
        print(f"   ✅ Downloaded ZIP: {zip_file} ({len(response.content):,} bytes)")
        
        # List ZIP contents
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zf:
            print(f"\n   ZIP Contents:")
            for info in zf.filelist:
                print(f"      - {info.filename} ({info.file_size:,} bytes)")
    else:
        print(f"   ❌ ZIP download failed: {response.status_code}")
        print(f"      {response.json()}")
    
    print("\n" + "=" * 80)
    print(f"Downloads saved to: {download_dir.absolute()}")
    print("=" * 80)


def test_job_deletion(job_id: str):
    """Test job deletion with file cleanup."""
    
    print("\n" + "=" * 80)
    print(f"Testing Job Deletion: {job_id}")
    print("=" * 80)
    
    # Check job exists
    response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}")
    
    if response.status_code != 200:
        print(f"❌ Job not found: {job_id}")
        return
    
    job = response.json()
    print(f"\nJob Status: {job['status']}")
    print(f"Output Dir: {job.get('output_dir', 'N/A')}")
    
    # Confirm deletion
    confirm = input("\n⚠️  Delete this job and all its files? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return
    
    # Delete job
    response = requests.delete(f"{API_BASE}/scanpy/jobs/{job_id}")
    
    if response.status_code == 204:
        print(f"✅ Job {job_id} deleted successfully")
        
        # Verify deletion
        response = requests.get(f"{API_BASE}/scanpy/jobs/{job_id}")
        if response.status_code == 404:
            print("✅ Job confirmed deleted from database")
        else:
            print("⚠️  Job still exists in database")
    else:
        print(f"❌ Deletion failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_downloads.py <job_id>")
        print("\nTo get a job_id, run: python test_celery.py")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    try:
        # Test downloads
        test_downloads(job_id)
        
        # Optionally test deletion
        print("\n")
        test_delete = input("Do you want to test job deletion? (yes/no): ")
        if test_delete.lower() == 'yes':
            test_job_deletion(job_id)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API server")
        print("Make sure the API is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()