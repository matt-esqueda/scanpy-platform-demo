"""
Service layer for Scanpy job management.
"""
import json
import redis
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scanpy import ScanpyJob, ScanpyPlot, ScanpyCluster, JobStatus
from app.core.config import settings

# No more schema imports needed here, simplifying the file.

class ScanpyJobService:
    """Service for managing Scanpy analysis jobs."""

    @staticmethod
    def _publish_update(job: ScanpyJob):
        """Helper method to connect to Redis and publish a job update."""
        r = None
        try:
            print(f"DEBUG: Publishing update for job {job.id}, status: {job.status.value}, progress: {job.progress_percent}")
            
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            channel = f"job:{job.id}:progress"
            
            # Build a simple, safe dictionary manually
            update_data = {
                "id": str(job.id),
                "status": job.status.value,
                "progress_percent": job.progress_percent,
                "current_step": job.current_step,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
                "preset": job.preset,
            }

            # If the job is complete, explicitly fetch and add the results
            if job.status == JobStatus.COMPLETE:
                update_data["plots"] = [
                    {"id": str(p.id), "plot_type": p.plot_type} for p in job.plots
                ]
                update_data["clusters"] = [
                    {"id": str(c.id), "cluster_name": c.cluster_name} for c in job.clusters
                ]

            message = json.dumps(update_data)
            result = r.publish(channel, message)
            print(f"SUCCESS: Published to {channel}, {result} subscribers received message")

        except Exception as e:
            print(f"!!! CRITICAL: FAILED TO PUBLISH REDIS UPDATE FOR JOB {job.id}: {e} !!!")
            import traceback
            print(f"!!! FULL TRACEBACK: {traceback.format_exc()} !!!")
            # Don't re-raise - let the job continue
        finally:
            if r:
                r.close()
    
    @staticmethod
    def update_progress(
        db: Session,
        job_id: UUID,
        status: JobStatus,
        progress_percent: int,
        current_step: str,
    ) -> ScanpyJob:
        job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = status
        job.progress_percent = progress_percent
        job.current_step = current_step
        
        if status == JobStatus.EXECUTING and not job.started_at:
            job.started_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        ScanpyJobService._publish_update(job)
        return job
    
    @staticmethod
    def mark_complete(
        db: Session,
        job_id: UUID,
        h5ad_path: str,
        stats: dict,
    ) -> ScanpyJob:
        job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.COMPLETE
        job.progress_percent = 100
        job.current_step = "complete"
        job.completed_at = datetime.utcnow()
        job.h5ad_path = h5ad_path
        job.stats = stats
        
        db.commit()
        db.refresh(job)

        ScanpyJobService._publish_update(job)
        return job
    
    @staticmethod
    def mark_failed(
        db: Session,
        job_id: UUID,
        error_message: str,
    ) -> ScanpyJob:
        job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        
        db.commit()
        db.refresh(job)

        ScanpyJobService._publish_update(job)
        return job
    
    # ... (add_plot, add_cluster, get_job_output_dir remain unchanged)
    @staticmethod
    def add_plot(db: Session, job_id: UUID, plot_type: str, file_path: str, step: str) -> ScanpyPlot:
        plot = ScanpyPlot(job_id=job_id, plot_type=plot_type, file_path=file_path, step=step)
        db.add(plot)
        db.commit()
        db.refresh(plot)
        return plot
    
    @staticmethod
    def add_cluster(db: Session, job_id: UUID, cluster_id: int, cluster_name: str, cell_count: int, celltypist_prediction: Optional[str] = None) -> ScanpyCluster:
        cluster = ScanpyCluster(job_id=job_id, cluster_id=cluster_id, cluster_name=cluster_name, cell_count=cell_count, celltypist_prediction=celltypist_prediction)
        db.add(cluster)
        db.commit()
        db.refresh(cluster)
        return cluster
    
    @staticmethod
    def get_job_output_dir(job_id: UUID) -> Path:
        job_dir = settings.JOBS_DIR / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir