"""
Scanpy analysis Celery tasks.
"""
import logging
from pathlib import Path
from uuid import UUID
import redis
import json

from celery import Task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.scanpy import JobStatus
from app.services.scanpy import ScanpyJobService, ScanpyPipeline, ScanpyPlotGenerator
from app.schemas.scanpy import ScanpyParameters

logger = logging.getLogger(__name__)

# Progress checkpoints
PROGRESS_STEPS = [
    ("loading", 10),
    ("qc_filter", 30),
    ("normalization", 50),
    ("clustering", 70),
    ("annotation", 90),
]


def publish_progress_update(job_id: str, status: str, progress: int, step: str):
    """Publish job progress update to Redis for WebSocket broadcasting."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        message = json.dumps({
            "status": status,
            "progress_percent": progress,
            "current_step": step,
            "type": "update"
        })
        channel = f"job:{job_id}:progress"
        r.publish(channel, message)
        logger.debug(f"Published progress update for job {job_id}: {progress}%")
    except Exception as e:
        logger.error(f"Failed to publish progress update: {e}")


class ScanpyTask(Task):
    """Base task with database session."""
    
    _db: Session = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=ScanpyTask, bind=True, name="app.tasks.scanpy_tasks.run_scanpy_analysis")
def run_scanpy_analysis(
    self,
    job_id: str,
    input_type: str,
    input_path: str,
    parameters_dict: dict,
) -> dict:
    """
    Run Scanpy analysis pipeline.
    
    Args:
        job_id: UUID of the job
        input_type: 'mtx' or 'h5'
        input_path: Path to input data
        parameters_dict: Analysis parameters
    
    Returns:
        dict with results summary
    """
    job_uuid = UUID(job_id)
    db = self.db
    service = ScanpyJobService()
    
    try:
        # Parse parameters
        params = ScanpyParameters(**parameters_dict)
        
        # Setup output directory
        output_dir = service.get_job_output_dir(job_uuid)
        
        # Initialize pipeline
        pipeline = ScanpyPipeline(output_dir, params)
        plot_gen = ScanpyPlotGenerator(output_dir / "figures")
        
        # Step 1: Load data
        logger.info(f"Job {job_id}: Loading data")
        service.update_progress(db, job_uuid, JobStatus.EXECUTING, 10, "loading")
        publish_progress_update(job_id, "executing", 10, "loading")
        adata = pipeline.load_data(input_path, input_type)
        
        # Step 2: Quality control
        logger.info(f"Job {job_id}: Running QC")
        service.update_progress(db, job_uuid, JobStatus.EXECUTING, 30, "qc_filter")
        publish_progress_update(job_id, "executing", 30, "qc_filter")
        adata, qc_stats = pipeline.quality_control(adata)
        
        # Step 3: Normalization
        logger.info(f"Job {job_id}: Normalizing")
        service.update_progress(db, job_uuid, JobStatus.EXECUTING, 50, "normalization")
        publish_progress_update(job_id, "executing", 50, "normalization")
        adata = pipeline.normalize(adata)
        
        # Step 4: Clustering
        logger.info(f"Job {job_id}: Clustering")
        service.update_progress(db, job_uuid, JobStatus.EXECUTING, 70, "clustering")
        publish_progress_update(job_id, "executing", 70, "clustering")
        adata = pipeline.cluster(adata)
        
        # Step 5: Annotation
        logger.info(f"Job {job_id}: Annotating")
        service.update_progress(db, job_uuid, JobStatus.EXECUTING, 90, "annotation")
        publish_progress_update(job_id, "executing", 90, "annotation")
        adata = pipeline.annotate(adata)
        
        # Generate plots
        logger.info(f"Job {job_id}: Generating plots")
        has_celltypist = 'majority_voting' in adata.obs.columns
        plot_records = plot_gen.generate_all_plots(adata, has_celltypist)
        
        # Save plots to database
        for plot_rec in plot_records:
            service.add_plot(
                db,
                job_uuid,
                plot_rec['plot_type'],
                plot_rec['file_path'],
                plot_rec['step'],
            )
        
        # Save H5AD
        h5ad_path = output_dir / "results.h5ad"
        adata.write(h5ad_path)
        logger.info(f"Job {job_id}: Saved H5AD to {h5ad_path}")
        
        # Save cluster data
        cluster_df = pipeline.get_cluster_data(adata)
        csv_path = output_dir / "cluster_assignments.csv"
        cluster_df.to_csv(csv_path, index=False)
        
        # Save cluster records to database
        for _, row in cluster_df.iterrows():
            service.add_cluster(
                db,
                job_uuid,
                row['cluster_id'],
                row['cluster_name'],
                row['cell_count'],
                row['celltypist_prediction'],
            )
        
        # Compile final stats
        final_stats = {
            **qc_stats,
            "n_clusters": len(cluster_df),
            "total_cells_analyzed": adata.n_obs,
            "total_genes": adata.n_vars,
        }
        
        # Mark job complete
        service.mark_complete(db, job_uuid, str(h5ad_path), final_stats)
        publish_progress_update(job_id, "complete", 100, "complete")
        
        logger.info(f"Job {job_id}: Complete")
        return {
            "status": "success",
            "job_id": job_id,
            "stats": final_stats,
        }
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        service.mark_failed(db, job_uuid, str(e))
        publish_progress_update(job_id, "failed", 0, "failed")
        raise