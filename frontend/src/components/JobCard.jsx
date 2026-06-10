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
      executing: 'bg-blue-100 text-blue-800',
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
  );
}