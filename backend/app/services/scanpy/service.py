"""
Service layer for Scanpy job management.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scanpy import ScanpyJob, ScanpyPlot, ScanpyCluster, JobStatus
from app.core.config import settings


class ScanpyJobService:
    """Service for managing Scanpy analysis jobs."""
    
    @staticmethod
    def update_progress(
        db: Session,
        job_id: UUID,
        status: JobStatus,
        progress_percent: int,
        current_step: str,
    ) -> ScanpyJob:
        """Update job progress."""
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
        return job
    
    @staticmethod
    def mark_complete(
        db: Session,
        job_id: UUID,
        h5ad_path: str,
        stats: dict,
    ) -> ScanpyJob:
        """Mark job as complete."""
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
        return job
    
    @staticmethod
    def mark_failed(
        db: Session,
        job_id: UUID,
        error_message: str,
    ) -> ScanpyJob:
        """Mark job as failed."""
        job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def add_plot(
        db: Session,
        job_id: UUID,
        plot_type: str,
        file_path: str,
        step: str,
    ) -> ScanpyPlot:
        """Add a plot record."""
        plot = ScanpyPlot(
            job_id=job_id,
            plot_type=plot_type,
            file_path=file_path,
            step=step,
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        return plot
    
    @staticmethod
    def add_cluster(
        db: Session,
        job_id: UUID,
        cluster_id: int,
        cluster_name: str,
        cell_count: int,
        celltypist_prediction: Optional[str] = None,
    ) -> ScanpyCluster:
        """Add a cluster record."""
        cluster = ScanpyCluster(
            job_id=job_id,
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            cell_count=cell_count,
            celltypist_prediction=celltypist_prediction,
        )
        db.add(cluster)
        db.commit()
        db.refresh(cluster)
        return cluster
    
    @staticmethod
    def get_job_output_dir(job_id: UUID) -> Path:
        """Get output directory for a job."""
        job_dir = settings.JOBS_DIR / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir