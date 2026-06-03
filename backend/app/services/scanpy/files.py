"""
File operations service for Scanpy jobs.
"""
import logging
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID
import zipfile
import io

from app.core.config import settings

logger = logging.getLogger(__name__)


class ScanpyFileService:
    """Service for managing Scanpy job files."""
    
    @staticmethod
    def get_job_directory(job_id: UUID) -> Path:
        """Get the output directory for a job."""
        return settings.JOBS_DIR / str(job_id)
    
    @staticmethod
    def get_h5ad_path(job_id: UUID) -> Optional[Path]:
        """Get path to H5AD results file."""
        h5ad_path = ScanpyFileService.get_job_directory(job_id) / "results.h5ad"
        return h5ad_path if h5ad_path.exists() else None
    
    @staticmethod
    def get_clusters_csv_path(job_id: UUID) -> Optional[Path]:
        """Get path to cluster assignments CSV."""
        csv_path = ScanpyFileService.get_job_directory(job_id) / "cluster_assignments.csv"
        return csv_path if csv_path.exists() else None
    
    @staticmethod
    def get_plot_path(plot_file_path: str) -> Optional[Path]:
        """
        Get path to plot file.
        
        Args:
            plot_file_path: Path stored in database (absolute or relative)
        
        Returns:
            Path object if file exists, None otherwise
        """
        plot_path = Path(plot_file_path)
        
        # Handle both absolute and relative paths
        if not plot_path.is_absolute():
            plot_path = settings.BASE_DIR / plot_path
        
        return plot_path if plot_path.exists() else None
    
    @staticmethod
    def create_results_zip(job_id: UUID) -> Optional[io.BytesIO]:
        """
        Create a ZIP archive of all job results.
        
        Args:
            job_id: Job UUID
        
        Returns:
            BytesIO containing ZIP data, or None if no files found
        """
        job_dir = ScanpyFileService.get_job_directory(job_id)
        
        if not job_dir.exists():
            logger.warning(f"Job directory not found: {job_dir}")
            return None
        
        # Create in-memory ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add H5AD file
            h5ad_path = job_dir / "results.h5ad"
            if h5ad_path.exists():
                zip_file.write(h5ad_path, "results.h5ad")
            
            # Add cluster CSV
            csv_path = job_dir / "cluster_assignments.csv"
            if csv_path.exists():
                zip_file.write(csv_path, "cluster_assignments.csv")
            
            # Add all plots
            figures_dir = job_dir / "figures"
            if figures_dir.exists():
                for plot_file in figures_dir.glob("*.png"):
                    zip_file.write(plot_file, f"figures/{plot_file.name}")
        
        # Check if ZIP has any content
        zip_buffer.seek(0)
        if zip_buffer.getbuffer().nbytes == 0:
            logger.warning(f"No files found for job {job_id}")
            return None
        
        return zip_buffer
    
    @staticmethod
    def delete_job_files(job_id: UUID) -> bool:
        """
        Delete all files associated with a job.
        
        Args:
            job_id: Job UUID
        
        Returns:
            True if deletion successful, False otherwise
        """
        job_dir = ScanpyFileService.get_job_directory(job_id)
        
        if not job_dir.exists():
            logger.info(f"Job directory does not exist: {job_dir}")
            return True
        
        try:
            shutil.rmtree(job_dir)
            logger.info(f"Deleted job directory: {job_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job directory {job_dir}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes."""
        return file_path.stat().st_size if file_path.exists() else 0
    
    @staticmethod
    def validate_path_safety(file_path: Path, base_dir: Path) -> bool:
        """
        Validate that file_path is within base_dir (prevent path traversal).
        
        Args:
            file_path: Path to validate
            base_dir: Base directory that should contain the file
        
        Returns:
            True if path is safe, False otherwise
        """
        try:
            file_path.resolve().relative_to(base_dir.resolve())
            return True
        except ValueError:
            logger.warning(f"Path traversal attempt detected: {file_path}")
            return False