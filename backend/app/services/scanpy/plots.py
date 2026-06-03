"""
Plot generation for Scanpy analysis.
"""
import logging
from pathlib import Path
from typing import List, Dict

import scanpy as sc
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ScanpyPlotGenerator:
    """Generate and save plots for Scanpy analysis."""
    
    def __init__(self, figures_dir: Path):
        self.figures_dir = figures_dir
        self.plot_records = []
    
    def generate_all_plots(self, adata: sc.AnnData, has_celltypist: bool = False) -> List[Dict[str, str]]:
        """Generate all plots for the analysis."""
        logger.info("Generating plots")
        
        # QC plots (pre-filter is not available, so skip or generate post-filter only)
        self._plot_qc_violin_post(adata)
        self._plot_scatter_mt(adata)
        
        # Feature plots
        self._plot_hvg(adata)
        self._plot_pca(adata)
        
        # Clustering plots
        self._plot_umap_leiden(adata)
        
        if has_celltypist:
            self._plot_umap_celltypist(adata)
        
        # Marker plots (if markers available)
        # self._plot_markers(adata)
        
        logger.info(f"Generated {len(self.plot_records)} plots")
        return self.plot_records
    
    def _save_plot(self, plot_type: str, step: str) -> str:
        """Save current plot and record metadata."""
        filename = f"{plot_type}.png"
        filepath = self.figures_dir / filename
        
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        
        self.plot_records.append({
            'plot_type': plot_type,
            'file_path': str(filepath),
            'step': step,
        })
        
        return str(filepath)
    
    def _plot_qc_violin_post(self, adata: sc.AnnData):
        """QC violin plots after filtering."""
        sc.pl.violin(
            adata,
            ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
            jitter=0.4,
            multi_panel=True,
            show=False
        )
        self._save_plot('qc_violin_post', 'qc_filter')
    
    def _plot_scatter_mt(self, adata: sc.AnnData):
        """Scatter plot of counts vs MT percentage."""
        sc.pl.scatter(
            adata,
            x='total_counts',
            y='pct_counts_mt',
            show=False
        )
        self._save_plot('scatter_mt', 'qc_filter')
        
        sc.pl.scatter(
            adata,
            x='total_counts',
            y='n_genes_by_counts',
            show=False
        )
        self._save_plot('scatter_genes', 'qc_filter')
    
    def _plot_hvg(self, adata: sc.AnnData):
        """Highly variable genes plot."""
        sc.pl.highly_variable_genes(adata, show=False)
        self._save_plot('hvg', 'normalization')
    
    def _plot_pca(self, adata: sc.AnnData):
        """PCA plot."""
        sc.pl.pca_variance_ratio(adata, log=True, show=False)
        self._save_plot('pca_variance', 'clustering')
        
        sc.pl.pca(adata, color='leiden', show=False)
        self._save_plot('pca', 'clustering')
    
    def _plot_umap_leiden(self, adata: sc.AnnData):
        """UMAP colored by Leiden clusters."""
        sc.pl.umap(adata, color='leiden', show=False, legend_loc='on data')
        self._save_plot('umap_leiden', 'clustering')
    
    def _plot_umap_celltypist(self, adata: sc.AnnData):
        """UMAP colored by CellTypist predictions."""
        if 'majority_voting' in adata.obs.columns:
            sc.pl.umap(adata, color='majority_voting', show=False)
            self._save_plot('umap_celltypist', 'annotation')
    
    def _plot_markers(self, adata: sc.AnnData):
        """Marker gene plots."""
        # Example markers - customize based on your data
        markers = {
            'T cells': ['CD3D', 'CD3E'],
            'B cells': ['CD79A', 'MS4A1'],
            'Myeloid': ['CD14', 'LYZ'],
        }
        
        # Flatten marker list
        marker_genes = [gene for genes in markers.values() for gene in genes]
        
        # Check if markers exist in data
        available_markers = [gene for gene in marker_genes if gene in adata.var_names]
        
        if available_markers:
            sc.pl.dotplot(adata, available_markers, groupby='leiden', show=False)
            self._save_plot('marker_dotplot', 'annotation')