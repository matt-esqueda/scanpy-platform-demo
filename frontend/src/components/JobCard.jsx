import { Link } from 'react-router-dom';
import ProgressBar from './ProgressBar';

export default function JobCard({ job }) {
  // ❌ Remove this line - no WebSocket in job cards
  // const { jobUpdate } = useWebSocket(job.id);
  
  // ✅ Just use the job data directly
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
        className={`px-3 py-1 rounded-full text-xs font-semibold ${
          badges[job?.status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {job?.status || 'unknown'}
      </span>
    );
  };

  if (!job) {
    return null;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-semibold text-gray-900">
            Job {job.id?.slice(0, 8)}...
          </h3>
          {getStatusBadge()}
        </div>
        <Link
          to={`/jobs/${job.id}`}
          className="text-purple-600 hover:text-purple-800 text-sm font-medium"
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
          <span className="text-gray-500">Input Type:</span>
          <span className="ml-2 font-medium text-gray-900">
            {job.input_type?.toUpperCase()}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Preset:</span>
          <span className="ml-2 font-medium text-gray-900">
            {job.preset || 'Custom'}
          </span>
        </div>
        <div className="col-span-2">
          <span className="text-gray-500">Created:</span>
          <span className="ml-2 font-medium text-gray-900">
            {formatDate(job.created_at)}
          </span>
        </div>
      </div>
    </div>
  );
}