import { useState } from 'react';
import { useJobs } from '../hooks/useJobs';
import JobCard from '../components/JobCard';

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState('');
  
  const { data, isLoading, error } = useJobs({
    status: statusFilter || undefined,
    limit: 20,
  });

  if (isLoading) {
    return (
      <div className="px-4 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Analysis Jobs</h2>
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Analysis Jobs</h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">Error loading jobs: {error.message}</p>
          <p className="text-sm text-red-600 mt-2">
            Make sure the backend API is running on http://localhost:8000
          </p>
        </div>
      </div>
    );
  }

  const jobs = data?.jobs || [];
  const total = data?.total || 0;

  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Analysis Jobs
          <span className="ml-3 text-lg font-normal text-gray-500">
            ({total} total)
          </span>
        </h2>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Jobs</option>
          <option value="pending">Pending</option>
          <option value="executing">Executing</option>
          <option value="complete">Complete</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Jobs List */}
      {jobs.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg">No jobs found</p>
          <p className="text-gray-500 text-sm mt-2">
            Submit a new analysis job to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}