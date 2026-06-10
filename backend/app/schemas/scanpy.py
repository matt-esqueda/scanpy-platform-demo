from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from uuid import UUID
from app.models.scanpy import JobStatus


# ============================================================================
# Parameter Configuration
# ============================================================================

class ScanpyParameters(BaseModel):
    """Scanpy analysis parameters"""
    
    # Cell/gene filtering
    min_genes: int = Field(default=200, ge=0, description="Minimum genes per cell")
    min_cells: int = Field(default=3, ge=0, description="Minimum cells per gene")
    
    # QC thresholds
    n_genes_lower: int = Field(default=1800, ge=0, description="Lower threshold for gene count")
    n_genes_upper: int = Field(default=6000, ge=0, description="Upper threshold for gene count")
    pct_mt_cutoff: float = Field(default=6.0, ge=0.0, le=100.0, description="Mitochondrial percentage cutoff")
    
    # Clustering parameters
    leiden_resolution: float = Field(default=0.2, ge=0.0, le=2.0, description="Leiden clustering resolution")
    n_neighbors: int = Field(default=50, ge=1, description="Number of neighbors for graph")
    n_pcs: int = Field(default=10, ge=1, description="Number of principal components")
    
    @field_validator('n_genes_upper')
    @classmethod
    def validate_gene_thresholds(cls, v, info):
        """Ensure upper threshold is greater than lower"""
        if 'n_genes_lower' in info.data and v <= info.data['n_genes_lower']:
            raise ValueError('n_genes_upper must be greater than n_genes_lower')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "min_genes": 200,
                "min_cells": 3,
                "n_genes_lower": 1800,
                "n_genes_upper": 6000,
                "pct_mt_cutoff": 6.0,
                "leiden_resolution": 0.2,
                "n_neighbors": 50,
                "n_pcs": 10
            }
        }
    )


# Parameter Presets
PARAMETER_PRESETS = {
    "default": ScanpyParameters(
        min_genes=200,
        min_cells=3,
        n_genes_lower=1800,
        n_genes_upper=6000,
        pct_mt_cutoff=6.0,
        leiden_resolution=0.2,
        n_neighbors=50,
        n_pcs=10
    ),
    "stringent": ScanpyParameters(
        min_genes=500,
        min_cells=10,
        n_genes_lower=2000,
        n_genes_upper=5000,
        pct_mt_cutoff=5.0,
        leiden_resolution=0.3,
        n_neighbors=30,
        n_pcs=15
    ),
}


# ============================================================================
# Request Schemas
# ============================================================================

class JobSubmitRequest(BaseModel):
    """Request schema for submitting a new Scanpy analysis job"""
    
    input_type: Literal["mtx", "h5"] = Field(
        description="Input file format: 'mtx' (Matrix Market) or 'h5' (HDF5)"
    )
    
    input_path: str = Field(
        description="Path to input file(s) on server or upload identifier"
    )
    
    preset: Literal["default", "stringent", "custom"] = Field(
        default="default",
        description="Parameter preset to use"
    )
    
    parameters: Optional[ScanpyParameters] = Field(
        default=None,
        description="Custom parameters (only used if preset='custom')"
    )
    
    @field_validator('parameters')
    @classmethod
    def validate_custom_parameters(cls, v, info):
        """Require parameters if preset is custom"""
        if 'preset' in info.data:
            if info.data['preset'] == 'custom' and v is None:
                raise ValueError("parameters required when preset='custom'")
            if info.data['preset'] != 'custom' and v is not None:
                raise ValueError("parameters only allowed when preset='custom'")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input_type": "mtx",
                "input_path": "/data/test_data/pbmc_10k",
                "preset": "default"
            }
        }
    )


# ============================================================================
# Response Schemas
# ============================================================================

class PlotResponse(BaseModel):
    """Plot metadata response"""
    
    id: UUID
    plot_type: str
    file_path: str
    step: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClusterResponse(BaseModel):
    """Cluster data response"""
    
    id: UUID
    cluster_id: str
    cluster_name: str
    cell_count: int
    celltypist_prediction: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    """Job status and details response"""
    
    id: UUID
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress
    current_step: Optional[str] = None
    progress_percent: int
    
    # Configuration
    input_type: str
    input_path: str
    preset: str
    parameters: Dict[str, Any]
    
    # Results
    output_dir: str
    h5ad_path: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    
    # Error
    error_message: Optional[str] = None
    
    # Relationships - ADDED THESE!
    plots: List[PlotResponse] = Field(default_factory=list)
    clusters: List[ClusterResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """Paginated job list response"""
    
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jobs": [],
                "total": 45,
                "limit": 20,
                "offset": 0
            }
        }
    )


class ResultsResponse(BaseModel):
    """Complete job results with plots and clusters"""
    
    job_id: UUID
    status: JobStatus
    
    # Summary statistics
    stats: Dict[str, Any] = Field(
        description="Cell counts, cluster info, etc."
    )
    
    # Plots
    plots: List[PlotResponse] = Field(
        description="Generated visualization plots"
    )
    
    # Clusters
    clusters: List[ClusterResponse] = Field(
        description="Identified cell clusters"
    )
    
    # Download links
    h5ad_download_url: Optional[str] = None
    clusters_csv_url: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "complete",
                "stats": {
                    "raw_cells": 8957,
                    "filtered_cells": 7543,
                    "final_cells": 7201,
                    "n_clusters": 9
                },
                "plots": [],
                "clusters": []
            }
        }
    )


# ============================================================================
# Preset Query Response
# ============================================================================

class PresetResponse(BaseModel):
    """Parameter preset response"""
    
    name: str
    description: str
    parameters: ScanpyParameters
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "default",
                "description": "Standard QC thresholds for PBMC data",
                "parameters": {
                    "min_genes": 200,
                    "min_cells": 3
                }
            }
        }
    )


class PresetsListResponse(BaseModel):
    """List of available parameter presets"""
    
    presets: List[PresetResponse]