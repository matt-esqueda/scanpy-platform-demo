import { useState } from 'react';
import PlotPreview from './PlotPreview';

const PlotGallery = ({ plots = [], jobId }) => {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('step');

  const plotTypeLabels = {
    qc_violin_post: 'QC Violin',
    scatter_mt: 'MT Scatter', 
    scatter_genes: 'Gene Scatter',
    hvg: 'Highly Variable Genes',
    pca_variance: 'PCA Variance',
    pca: 'PCA Plot',
    umap_leiden: 'UMAP Clustering'
  };

  const stepOrder = {
    'qc_filter': 1,
    'normalization': 2, 
    'clustering': 3,
    'annotation': 4
  };

  const getFilteredAndSortedPlots = () => {
    let filteredPlots = plots;

    // Filter by step
    if (filter !== 'all') {
      filteredPlots = plots.filter(plot => plot.step === filter);
    }

    // Sort plots
    filteredPlots.sort((a, b) => {
      if (sortBy === 'step') {
        return (stepOrder[a.step] || 999) - (stepOrder[b.step] || 999);
      } else if (sortBy === 'type') {
        return a.plot_type.localeCompare(b.plot_type);
      } else if (sortBy === 'created') {
        return new Date(b.created_at) - new Date(a.created_at);
      }
      return 0;
    });

    return filteredPlots;
  };

  const getUniqueSteps = () => {
    const steps = [...new Set(plots.map(plot => plot.step))];
    return steps.sort((a, b) => (stepOrder[a] || 999) - (stepOrder[b] || 999));
  };

  if (!plots || plots.length === 0) {
    return (
      <div className="bio-card p-8 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-slate-400 text-2xl">📊</span>
        </div>
        <h3 className="text-lg font-medium text-slate-900 mb-2">No Plots Generated</h3>
        <p className="text-slate-500">Plots will appear here once the analysis completes.</p>
      </div>
    );
  }

  const filteredPlots = getFilteredAndSortedPlots();

  return (
    <div className="bio-card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Generated Plots</h2>
          <p className="text-sm text-slate-600 mt-1">
            {filteredPlots.length} of {plots.length} plots
            {filter !== 'all' && ` in ${filter.replace('_', ' ')} step`}
          </p>
        </div>

        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          {/* Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-slate-600">Filter:</span>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="all">All Steps</option>
              {getUniqueSteps().map(step => (
                <option key={step} value={step}>
                  {step.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-slate-600">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="step">By Step</option>
              <option value="type">By Type</option>
              <option value="created">By Date</option>
            </select>
          </div>
        </div>
      </div>

      {/* Plot Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredPlots.map((plot) => (
          <div key={plot.id} className="group">
            <PlotPreview
              plotId={plot.id}
              plotType={plot.plot_type}
              thumbnailUrl={`http://localhost:8000/api/scanpy/plots/${plot.id}`}
            />
            <div className="mt-2 px-2">
              <h4 className="text-sm font-medium text-slate-900 truncate">
                {plotTypeLabels[plot.plot_type] || plot.plot_type.replace(/_/g, ' ')}
              </h4>
              <div className="flex items-center justify-between text-xs text-slate-500 mt-1">
                <span className="capitalize">
                  {plot.step.replace('_', ' ')}
                </span>
                <span>
                  {new Date(plot.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredPlots.length === 0 && filter !== 'all' && (
        <div className="text-center py-8">
          <p className="text-slate-500">No plots found for the selected filter.</p>
          <button
            onClick={() => setFilter('all')}
            className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
          >
            Show all plots
          </button>
        </div>
      )}
    </div>
  );
};

export default PlotGallery;