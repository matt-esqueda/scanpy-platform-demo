from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
import enum


class JobStatus(str, enum.Enum):
    """Job execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETE = "complete"
    FAILED = "failed"


class ScanpyJob(Base, UUIDMixin, TimestampMixin):
    """Main job tracking table for Scanpy analysis pipeline"""
    __tablename__ = "scanpy_jobs"
    
    # Status tracking
    status = Column(
        SQLEnum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        index=True
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    current_step = Column(String(50), nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)
    
    # Input configuration
    input_type = Column(String(10), nullable=False)  # "mtx" or "h5"
    input_path = Column(Text, nullable=False)
    preset = Column(String(50), nullable=False)  # "default", "stringent", "custom"
    parameters = Column(JSONB, nullable=False)  # Analysis parameters
    
    # Output paths
    output_dir = Column(Text, nullable=False)
    h5ad_path = Column(Text, nullable=True)
    
    # Results metadata
    stats = Column(JSONB, nullable=True)  # Cell counts, cluster info, etc.
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Relationships
    plots = relationship(
        "ScanpyPlot",
        back_populates="job",
        cascade="all, delete-orphan"
    )
    clusters = relationship(
        "ScanpyCluster",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class ScanpyPlot(Base, UUIDMixin, TimestampMixin):
    """Stores metadata for generated plots"""
    __tablename__ = "scanpy_plots"
    
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scanpy_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plot_type = Column(String(100), nullable=False)
    file_path = Column(Text, nullable=False)
    step = Column(String(50), nullable=False)  # Pipeline step that generated this
    
    # Relationship
    job = relationship("ScanpyJob", back_populates="plots")


class ScanpyCluster(Base, UUIDMixin, TimestampMixin):
    """Stores cluster assignment results"""
    __tablename__ = "scanpy_clusters"
    
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scanpy_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    cluster_id = Column(String(10), nullable=False)
    cluster_name = Column(String(100), nullable=False)
    cell_count = Column(Integer, nullable=False)
    celltypist_prediction = Column(String(100), nullable=True)
    
    # Relationship
    job = relationship("ScanpyJob", back_populates="clusters")