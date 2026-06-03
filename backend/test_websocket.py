"""
Test WebSocket real-time updates.

Usage:
    Terminal 1: celery -A app.core.celery_app worker --loglevel=info --pool=solo
    Terminal 2: uvicorn app.main:app --reload
    Terminal 3: python test_websocket.py <job_id>
    Terminal 4: python test_celery.py (to submit a job)
"""
import asyncio
import sys
import websockets
import json


async def listen_to_job(job_id: str):
    """Connect to WebSocket and listen for job updates."""
    
    uri = f"ws://localhost:8000/ws/jobs/{job_id}"
    
    print("=" * 80)
    print(f"Connecting to WebSocket for job: {job_id}")
    print(f"URI: {uri}")
    print("=" * 80)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            print("\nWaiting for updates...\n")
            
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                
                msg_type = data.get("type", "update")
                status = data.get("status")
                progress = data.get("progress_percent")
                step = data.get("current_step")
                
                # Format output
                if msg_type == "initial":
                    print(f"📊 Initial State:")
                else:
                    print(f"🔄 Update:")
                
                print(f"   Status: {status}")
                print(f"   Progress: {progress}%")
                print(f"   Step: {step}")
                print()
                
                # Exit if job is complete or failed
                if status in ["complete", "failed"]:
                    print("=" * 80)
                    if status == "complete":
                        print("✅ Job completed!")
                    else:
                        print("❌ Job failed!")
                    print("=" * 80)
                    break
    
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_websocket.py <job_id>")
        print("\nTo get a job_id:")
        print("1. Start API: uvicorn app.main:app --reload")
        print("2. Submit job: python test_celery.py")
        print("3. Copy the job_id from the output")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    asyncio.run(listen_to_job(job_id))