"""Scanpy analysis API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List, Optional
from uuid import UUID
import logging

from app.api.deps import get_db
from app.models.scanpy import ScanpyJob, ScanpyPlot, ScanpyCluster, JobStatus
from app.schemas.scanpy import (
    JobSubmitRequest,
    JobResponse,
    JobListResponse,
    ResultsResponse,
    PlotResponse,
    ClusterResponse,
    PresetResponse,
    PresetsListResponse,
    PARAMETER_PRESETS,
)
from app.services.scanpy import ScanpyFileService
from app.core.config import settings

router = APIRouter(prefix="/scanpy", tags=["scanpy"])

logger = logging.getLogger(__name__)


# ============================================================================
# Job Management Endpoints
# ============================================================================

@router.post("/jobs/submit", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_job(
    request: JobSubmitRequest,
    db: Session = Depends(get_db),
) -> JobResponse:
    """
    Submit a new Scanpy analysis job.
    
    Validates parameters, creates job record, and dispatches to Celery.
    """
    # Get parameters (from preset or custom)
    if request.preset:
        if request.preset not in PARAMETER_PRESETS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown preset: {request.preset}. Available: {list(PARAMETER_PRESETS.keys())}"
            )
        params = PARAMETER_PRESETS[request.preset]
    elif request.parameters:
        params = request.parameters
    else:
        # Default preset
        params = PARAMETER_PRESETS["default"]
    
    # Validate input path exists (basic check)
    input_path = Path(request.input_path)
    if not input_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input path does not exist: {request.input_path}"
        )
    
    # Create job record
    from app.services.scanpy import ScanpyJobService
    import uuid

    # Generate UUID first
    job_id = uuid.uuid4()

    # Get output directory path
    output_dir = str(ScanpyJobService.get_job_output_dir(job_id))

    # Create job with all required fields
    job = ScanpyJob(
        id=job_id,
        status=JobStatus.PENDING,
        progress_percent=0,
        current_step="pending",
        input_type=request.input_type,
        input_path=request.input_path,
        preset=request.preset,
        parameters=params.model_dump(),
        output_dir=output_dir,
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Dispatch Celery task
    from app.tasks.scanpy_tasks import run_scanpy_analysis
    
    task = run_scanpy_analysis.delay(
        job_id=str(job.id),
        input_type=request.input_type,
        input_path=request.input_path,
        parameters_dict=params.model_dump(),
    )
    
    logger.info(f"Submitted job {job.id} with task {task.id}")
    
    return job


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    status: Optional[JobStatus] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> JobListResponse:
    """
    List all jobs with optional filtering
    
    - **status**: Filter by job status (pending, executing, complete, failed)
    - **limit**: Number of results per page (default 20)
    - **offset**: Number of results to skip (default 0)
    """
    query = db.query(ScanpyJob)
    
    # Apply status filter if provided
    if status:
        query = query.filter(ScanpyJob.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    jobs = query.order_by(ScanpyJob.created_at.desc()).limit(limit).offset(offset).all()
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> JobResponse:
    """
    Get detailed information about a specific job
    
    Returns job status, progress, parameters, and results (if complete)
    """
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a job and all associated data
    
    This will cascade delete:
    - Plot metadata
    - Cluster data
    - Output files from filesystem
    """
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    # Delete files from filesystem
    file_deletion_success = ScanpyFileService.delete_job_files(job_id)
    
    if not file_deletion_success:
        logger.warning(f"Failed to delete files for job {job_id}, but continuing with DB deletion")
    
    # Delete from database (cascades to plots and clusters)
    db.delete(job)
    db.commit()
    
    logger.info(f"Deleted job {job_id}")
    
    return None


# ============================================================================
# Results Endpoints
# ============================================================================

@router.get("/jobs/{job_id}/results", response_model=ResultsResponse)
def get_results(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> ResultsResponse:
    """
    Get complete analysis results for a job
    
    Only available for jobs with status="complete"
    
    Returns:
    - Summary statistics
    - Plot metadata
    - Cluster assignments
    - Download URLs
    """
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not complete (status: {job.status.value})"
        )
    
    return ResultsResponse(
        job_id=job.id,
        status=job.status,
        stats=job.stats or {},
        plots=[PlotResponse.model_validate(plot) for plot in job.plots],
        clusters=[ClusterResponse.model_validate(cluster) for cluster in job.clusters],
        h5ad_download_url=f"/api/scanpy/jobs/{job_id}/download/h5ad" if job.h5ad_path else None,
        clusters_csv_url=f"/api/scanpy/jobs/{job_id}/download/clusters"
    )


# ============================================================================
# Configuration Endpoints
# ============================================================================

@router.get("/presets", response_model=PresetsListResponse)
def list_presets() -> PresetsListResponse:
    """
    Get available parameter presets
    
    Returns predefined configurations:
    - **default**: Standard QC thresholds for PBMC data
    - **stringent**: Strict filtering for high-quality analysis
    """
    presets = [
        PresetResponse(
            name="default",
            description="Standard QC thresholds for PBMC data",
            parameters=PARAMETER_PRESETS["default"]
        ),
        PresetResponse(
            name="stringent",
            description="Strict filtering for high-quality analysis",
            parameters=PARAMETER_PRESETS["stringent"]
        )
    ]
    
    return PresetsListResponse(presets=presets)


# ============================================================================
# Download Endpoints
# ============================================================================

@router.get("/jobs/{job_id}/download/h5ad")
def download_h5ad(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Download H5AD results file"""
    # Verify job exists and is complete
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not complete (status: {job.status.value})"
        )
    
    # Get file path
    h5ad_path = ScanpyFileService.get_h5ad_path(job_id)
    
    if not h5ad_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="H5AD file not found"
        )
    
    # Validate path safety
    if not ScanpyFileService.validate_path_safety(h5ad_path, settings.JOBS_DIR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        path=h5ad_path,
        filename=f"scanpy_results_{job_id}.h5ad",
        media_type="application/octet-stream"
    )


@router.get("/jobs/{job_id}/download/clusters")
def download_clusters_csv(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Download cluster assignments as CSV"""
    # Verify job exists and is complete
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not complete (status: {job.status.value})"
        )
    
    # Get file path
    csv_path = ScanpyFileService.get_clusters_csv_path(job_id)
    
    if not csv_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster CSV file not found"
        )
    
    # Validate path safety
    if not ScanpyFileService.validate_path_safety(csv_path, settings.JOBS_DIR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        path=csv_path,
        filename=f"cluster_assignments_{job_id}.csv",
        media_type="text/csv"
    )


@router.get("/plots/{plot_id}")
def get_plot(
    plot_id: UUID,
    db: Session = Depends(get_db)
):
    """Get plot image file"""
    # Get plot record
    plot = db.query(ScanpyPlot).filter(ScanpyPlot.id == plot_id).first()
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot {plot_id} not found"
        )
    
    # Get file path
    plot_path = ScanpyFileService.get_plot_path(plot.file_path)
    
    if not plot_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot file not found on disk"
        )
    
    # Validate path safety
    if not ScanpyFileService.validate_path_safety(plot_path, settings.JOBS_DIR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        path=plot_path,
        media_type="image/png"
    )


@router.get("/jobs/{job_id}/download/archive")
def download_results_archive(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Download all results as ZIP archive"""
    # Verify job exists and is complete
    job = db.query(ScanpyJob).filter(ScanpyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not complete (status: {job.status.value})"
        )
    
    # Create ZIP archive
    zip_buffer = ScanpyFileService.create_results_zip(job_id)
    
    if not zip_buffer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No result files found"
        )
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=scanpy_results_{job_id}.zip"}
    )