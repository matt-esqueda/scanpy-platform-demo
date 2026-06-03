"""
Scanpy analysis pipeline implementation.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import scanpy as sc
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from app.schemas.scanpy import ScanpyParameters

logger = logging.getLogger(__name__)


class ScanpyPipeline:
    """Scanpy analysis pipeline."""
    
    def __init__(self, output_dir: Path, parameters: ScanpyParameters):
        self.output_dir = output_dir
        self.params = parameters
        self.figures_dir = output_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure scanpy
        sc.settings.verbosity = 1
        sc.settings.figdir = self.figures_dir
        sc.set_figure_params(dpi=150, facecolor='white', format='png')
    
    def load_data(self, input_path: str, input_type: str) -> sc.AnnData:
        """Load 10x data."""
        logger.info(f"Loading {input_type} data from {input_path}")
        
        if input_type == "mtx":
            adata = sc.read_10x_mtx(input_path, var_names='gene_symbols', cache=True)
        elif input_type == "h5":
            adata = sc.read_10x_h5(input_path, genome=None)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
        
        # Make variable names unique
        adata.var_names_make_unique()
        
        logger.info(f"Loaded {adata.n_obs} cells, {adata.n_vars} genes")
        return adata
    
    def quality_control(self, adata: sc.AnnData) -> Tuple[sc.AnnData, Dict[str, Any]]:
        """Perform QC filtering."""
        logger.info("Running quality control")

        # Identify mitochondrial genes
        adata.var['mt'] = adata.var_names.str.startswith('MT-')
        
        # Calculate QC metrics
        sc.pp.calculate_qc_metrics(
            adata,
            qc_vars=['mt'],
            percent_top=None,
            log1p=False,
            inplace=True
        )
        
        # Store pre-filter stats
        pre_filter_cells = adata.n_obs
        pre_filter_genes = adata.n_vars
        
        # Filter cells
        sc.pp.filter_cells(adata, min_genes=self.params.min_genes)
        
        # Filter genes
        sc.pp.filter_genes(adata, min_cells=self.params.min_cells)
        
        # Filter by gene counts and MT percentage
        adata = adata[adata.obs.n_genes_by_counts < self.params.n_genes_upper, :]
        adata = adata[adata.obs.n_genes_by_counts > self.params.n_genes_lower, :]
        adata = adata[adata.obs.pct_counts_mt < self.params.pct_mt_cutoff, :]
        
        stats = {
            "pre_filter_cells": pre_filter_cells,
            "pre_filter_genes": pre_filter_genes,
            "post_filter_cells": adata.n_obs,
            "post_filter_genes": adata.n_vars,
        }
        
        logger.info(f"Filtered to {adata.n_obs} cells, {adata.n_vars} genes")
        return adata, stats
    
    def normalize(self, adata: sc.AnnData) -> sc.AnnData:
        """Normalize and identify highly variable genes."""
        logger.info("Normalizing data")
        
        # Normalize
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        
        # Identify highly variable genes
        sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
        
        # Regress out unwanted variation
        sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])
        sc.pp.scale(adata, max_value=10)
        
        return adata
    
    def cluster(self, adata: sc.AnnData) -> sc.AnnData:
        """Perform PCA, neighbors, UMAP, and clustering."""
        logger.info("Clustering cells")
        
        # PCA
        sc.tl.pca(adata, svd_solver='arpack', n_comps=self.params.n_pcs)
        
        # Neighbors and UMAP
        sc.pp.neighbors(adata, n_neighbors=self.params.n_neighbors, n_pcs=self.params.n_pcs)
        sc.tl.umap(adata)
        
        # Leiden clustering
        sc.tl.leiden(adata, resolution=self.params.leiden_resolution)
        
        return adata
    
    def annotate(self, adata: sc.AnnData) -> sc.AnnData:
        """Annotate cell types using CellTypist."""
        logger.info("Annotating cell types")
        
        try:
            import celltypist
            from celltypist import models
            
            # Download model if needed
            model = models.Model.load(model='Immune_All_Low.pkl')
            
            # Predict cell types
            predictions = celltypist.annotate(adata, model=model, majority_voting=True)
            adata = predictions.to_adata()
            
            logger.info("Cell type annotation complete")
        except Exception as e:
            logger.warning(f"CellTypist annotation failed: {e}. Continuing without annotation.")
        
        return adata
    
    def get_cluster_data(self, adata: sc.AnnData) -> pd.DataFrame:
        """Extract cluster assignments."""
        cluster_counts = adata.obs['leiden'].value_counts().sort_index()
        
        data = []
        for cluster_id, count in cluster_counts.items():
            cluster_cells = adata.obs[adata.obs['leiden'] == cluster_id]
            
            # Get majority celltypist prediction if available
            celltypist_pred = None
            if 'majority_voting' in cluster_cells.columns:
                celltypist_pred = cluster_cells['majority_voting'].mode()[0]
            
            data.append({
                'cluster_id': int(cluster_id),
                'cluster_name': f'Cluster_{cluster_id}',
                'cell_count': int(count),
                'celltypist_prediction': celltypist_pred,
            })
        
        return pd.DataFrame(data)