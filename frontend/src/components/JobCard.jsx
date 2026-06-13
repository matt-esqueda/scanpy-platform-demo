import { Link } from 'react-router-dom';
import ProgressBar from './ProgressBar';

export default function JobCard({ job }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = () => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      executing: 'bg-blue-100 text-blue-800 animate-pulse',
      complete: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return (
      <span
        className={`bio-status-badge ${badges[job?.status] || 'bg-slate-100 text-slate-800'}`}
      >
        {job?.status || 'unknown'}
      </span>
    );
  };

  const getJobStats = () => {
    if (!job.stats) return null;
    
    return (
      <div className="grid grid-cols-3 gap-2 text-xs text-slate-600 mt-2">
        <div className="text-center">
          <div className="font-medium text-slate-900">
            {job.stats.total_cells_analyzed?.toLocaleString() || 0}
          </div>
          <div>Cells</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-slate-900">
            {job.stats.n_clusters || 0}
          </div>
          <div>Clusters</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-slate-900">
            {job.plots?.length || 0}
          </div>
          <div>Plots</div>
        </div>
      </div>
    );
  };

  const getPlotPreviews = () => {
    if (!job.plots || job.plots.length === 0) return null;
    
    // Show up to 3 plot thumbnails
    const previewPlots = job.plots.slice(0, 3);
    const remainingCount = Math.max(0, job.plots.length - 3);
    
    return (
      <div className="mt-3">
        <div className="text-xs font-medium text-slate-700 mb-2">Generated Plots</div>
        <div className="flex space-x-2">
          {previewPlots.map((plot, index) => (
            <div key={plot.id} className="relative">
              <img
                src={`http://localhost:8000/api/scanpy/plots/${plot.id}`}
                alt={plot.plot_type}
                className="w-16 h-12 object-cover rounded border border-slate-200 hover:border-blue-300 transition-colors"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA2NCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjRjFGNUY5Ii8+CjxwYXRoIGQ9Ik0yOCAyNEwyMCAzMkgzNkwyOCAyNFoiIGZpbGw9IiM5Q0E4QjQiLz4KPC9zdmc+';
                }}
              />
              <div className="absolute -bottom-1 -right-1 bg-slate-800 text-white text-xs px-1 rounded text-center" style={{fontSize: '8px'}}>
                {plot.plot_type.split('_')[0]}
              </div>
            </div>
          ))}
          {remainingCount > 0 && (
            <div className="w-16 h-12 bg-slate-100 border border-slate-200 rounded flex items-center justify-center">
              <span className="text-xs text-slate-500">+{remainingCount}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (!job) {
    return null;
  }

  return (
    <div className="bio-card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-semibold text-slate-900">
            Job {job.id?.slice(0, 8)}...
          </h3>
          {getStatusBadge()}
        </div>
        <Link
          to={`/jobs/${job.id}`}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
        >
          View Details →
        </Link>
      </div>

      <div className="mb-4">
        <ProgressBar
          progress={job.progress_percent}
          status={job.status}
          currentStep={job.current_step}
        />
      </div>

      {/* Job Stats */}
      {job.status === 'complete' && getJobStats()}

      {/* Plot Previews */}
      {job.status === 'complete' && getPlotPreviews()}

      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Input Type:</span>
            <span className="ml-2 font-medium text-slate-900">
              {job.input_type?.toUpperCase()}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Preset:</span>
            <span className="ml-2 font-medium text-slate-900">
              {job.preset || 'Custom'}
            </span>
          </div>
          <div className="col-span-2">
            <span className="text-slate-500">Created:</span>
            <span className="ml-2 font-medium text-slate-900">
              {formatDate(job.created_at)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}