"""Test database models and data integrity"""
import pytest
from app.models.scanpy import ScanpyJob, JobStatus, ScanpyPlot, ScanpyCluster
from app.schemas.scanpy import ScanpyParameters


class TestScanpyJobModel:
    """Test the core ScanpyJob model"""
    
    def test_create_basic_job(self, db_session):
        """Test creating a basic job record"""
        params = ScanpyParameters()
        
        job = ScanpyJob(
            status=JobStatus.PENDING,
            input_type="h5",
            input_path="/test/data/test.h5",
            preset="default",
            parameters=params.model_dump(),
            output_dir="/test/output",
            progress_percent=0
        )
        
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        
        # Verify job was created with proper defaults
        assert job.id is not None
        assert job.status == JobStatus.PENDING
        assert job.progress_percent == 0
        assert job.started_at is None
        assert job.completed_at is None
        assert job.error_message is None
    
    def test_job_status_transitions(self, db_session, sample_job):
        """Test job status can be updated properly"""
        # Start as pending
        assert sample_job.status == JobStatus.PENDING
        
        # Update to executing
        sample_job.status = JobStatus.EXECUTING
        sample_job.progress_percent = 50
        sample_job.current_step = "clustering"
        
        db_session.commit()
        db_session.refresh(sample_job)
        
        assert sample_job.status == JobStatus.EXECUTING
        assert sample_job.progress_percent == 50
        assert sample_job.current_step == "clustering"
    
    def test_job_completion_with_results(self, db_session, sample_job):
        """Test completing a job with results"""
        # Complete the job
        sample_job.status = JobStatus.COMPLETE
        sample_job.progress_percent = 100
        sample_job.h5ad_path = "/test/output/results.h5ad"
        sample_job.stats = {
            "total_cells": 1000,
            "n_clusters": 8,
            "final_cells": 950
        }
        
        db_session.commit()
        db_session.refresh(sample_job)
        
        assert sample_job.status == JobStatus.COMPLETE
        assert sample_job.h5ad_path is not None
        assert sample_job.stats["total_cells"] == 1000
    
    def test_job_failure_with_error(self, db_session, sample_job):
        """Test job failure handling"""
        sample_job.status = JobStatus.FAILED
        sample_job.error_message = "Analysis failed: insufficient memory"
        
        db_session.commit()
        db_session.refresh(sample_job)
        
        assert sample_job.status == JobStatus.FAILED
        assert "insufficient memory" in sample_job.error_message


class TestJobRelationships:
    """Test relationships between job, plots, and clusters"""
    
    def test_job_with_plots(self, db_session, sample_job):
        """Test adding plots to a job"""
        plot1 = ScanpyPlot(
            job_id=sample_job.id,
            plot_type="qc_violin",
            file_path="/test/output/qc_violin.png",
            step="quality_control"
        )
        
        plot2 = ScanpyPlot(
            job_id=sample_job.id,
            plot_type="umap",
            file_path="/test/output/umap.png",
            step="clustering"
        )
        
        db_session.add_all([plot1, plot2])
        db_session.commit()
        
        # Refresh and check relationship
        db_session.refresh(sample_job)
        assert len(sample_job.plots) == 2
        assert sample_job.plots[0].plot_type in ["qc_violin", "umap"]
    
    def test_job_with_clusters(self, db_session, sample_job):
        """Test adding cluster results to a job"""
        clusters = [
            ScanpyCluster(
                job_id=sample_job.id,
                cluster_id="0",
                cluster_name="T cells",
                cell_count=250,
                celltypist_prediction="CD4+ T cells"
            ),
            ScanpyCluster(
                job_id=sample_job.id,
                cluster_id="1", 
                cluster_name="B cells",
                cell_count=180,
                celltypist_prediction="B cells"
            )
        ]
        
        db_session.add_all(clusters)
        db_session.commit()
        
        # Refresh and check relationship
        db_session.refresh(sample_job)
        assert len(sample_job.clusters) == 2
        assert sample_job.clusters[0].cell_count > 0
    
    def test_cascade_delete(self, db_session, sample_job):
        """Test that deleting job cascades to plots and clusters"""
        # Add some related data
        plot = ScanpyPlot(
            job_id=sample_job.id,
            plot_type="test_plot",
            file_path="/test/plot.png",
            step="test"
        )
        cluster = ScanpyCluster(
            job_id=sample_job.id,
            cluster_id="0",
            cluster_name="Test cluster",
            cell_count=100
        )
        
        db_session.add_all([plot, cluster])
        db_session.commit()
        
        plot_id = plot.id
        cluster_id = cluster.id
        
        # Delete the job
        db_session.delete(sample_job)
        db_session.commit()
        
        # Verify cascade delete worked
        assert db_session.get(ScanpyPlot, plot_id) is None
        assert db_session.get(ScanpyCluster, cluster_id) is None


class TestParameterValidation:
    """Test parameter schema validation"""
    
    def test_valid_parameters(self):
        """Test creating valid parameters"""
        params = ScanpyParameters(
            min_genes=200,
            min_cells=3,
            n_genes_lower=1800,
            n_genes_upper=6000,
            pct_mt_cutoff=6.0,
            leiden_resolution=0.2,
            n_neighbors=50,
            n_pcs=10
        )
        
        assert params.min_genes == 200
        assert params.leiden_resolution == 0.2
    
    def test_parameter_validation_fails(self):
        """Test parameter validation catches invalid values"""
        with pytest.raises(ValueError):
            ScanpyParameters(
                min_genes=200,
                min_cells=3,
                n_genes_lower=6000,  # Higher than upper
                n_genes_upper=1800,  # Lower than lower - should fail
                pct_mt_cutoff=6.0,
                leiden_resolution=0.2,
                n_neighbors=50,
                n_pcs=10
            )