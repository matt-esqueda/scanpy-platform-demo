import { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import { jobsApi } from '../services/api';

const JobDetailsPage = () => {
  const { jobId } = useParams();
  const location = useLocation();
  const [jobData, setJobData] = useState(location.state?.job || null);
  const [loading, setLoading] = useState(!location.state?.job);
  const [error, setError] = useState(null);
  
  const { jobUpdate, isConnected } = useWebSocket(jobId);

  // Fetch current job state using the correct API
  const fetchJobState = async () => {
    try {
      const response = await jobsApi.getJob(jobId);
      setJobData(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  // Fetch initial state if we don't have it
  useEffect(() => {
    if (!jobData) {
      fetchJobState();
    }
  }, [jobId, jobData]);

  // Fetch current state when WebSocket connects (in case we missed updates)
  useEffect(() => {
    if (isConnected && jobData && jobData.status === 'pending') {
      console.log('[JobDetails] WebSocket connected, fetching latest job state...');
      fetchJobState();
    }
  }, [isConnected]);

  // Update job data when WebSocket sends updates
  useEffect(() => {
    if (jobUpdate && jobUpdate.type !== 'initial' && jobUpdate.type !== 'connected') {
      setJobData(prevData => ({
        ...prevData,
        status: jobUpdate.status,
        progress_percent: jobUpdate.progress_percent,
        current_step: jobUpdate.current_step,
        completed_at: jobUpdate.completed_at,
        error_message: jobUpdate.error_message,
        plots: jobUpdate.plots || prevData?.plots,
        clusters: jobUpdate.clusters || prevData?.clusters,
      }));
    }
  }, [jobUpdate]);

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
          badges[jobData?.status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {jobData?.status || 'unknown'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="px-4 sm:px-0">
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Job</h3>
          <p className="text-red-700">{error}</p>
          <button 
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchJobState();
            }}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!jobData) {
    return (
      <div className="px-4 sm:px-0">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <p className="text-gray-600">Job not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <h1 className="text-3xl font-bold text-gray-900">
            Job {jobData.id.slice(0, 8)}...
          </h1>
          {getStatusBadge()}
        </div>
        <p className="text-gray-600">
          Created: {formatDate(jobData.created_at)}
        </p>
      </div>

      {/* Status and Progress */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Progress</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">WebSocket:</span>
            <span className={`text-xs px-2 py-1 rounded ${isConnected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{jobData.current_step || 'Initializing...'}</span>
            <span>{jobData.progress_percent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ${
                jobData.status === 'complete' ? 'bg-green-500' : 
                jobData.status === 'failed' ? 'bg-red-500' : 
                jobData.status === 'executing' ? 'bg-blue-500' : 'bg-gray-400'
              }`}
              style={{ width: `${jobData.progress_percent}%` }}
            />
          </div>
        </div>

        {/* Status Details */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Started:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatDate(jobData.started_at)}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Completed:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatDate(jobData.completed_at)}
            </span>
          </div>
        </div>

        {/* Error Message */}
        {jobData.status === 'failed' && jobData.error_message && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="text-sm font-semibold text-red-800 mb-2">Error Details</h4>
            <p className="text-sm text-red-700">{jobData.error_message}</p>
          </div>
        )}
      </div>

      {/* Configuration */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Input Type:</span>
            <span className="ml-2 font-medium text-gray-900">
              {jobData.input_type?.toUpperCase()}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Preset:</span>
            <span className="ml-2 font-medium text-gray-900">
              {jobData.preset || 'Custom'}
            </span>
          </div>
          <div className="col-span-2">
            <span className="text-gray-500">Input Path:</span>
            <span className="ml-2 font-medium text-gray-900 font-mono text-xs">
              {jobData.input_path}
            </span>
          </div>
        </div>
      </div>

      {/* Results (only show if complete) */}
      {jobData.status === 'complete' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Results</h2>
          
          {/* Statistics */}
          {jobData.stats && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Statistics</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center p-3 bg-blue-50 rounded">
                  <div className="text-2xl font-bold text-blue-600">
                    {jobData.stats.total_cells_analyzed || 0}
                  </div>
                  <div className="text-blue-700">Cells Analyzed</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded">
                  <div className="text-2xl font-bold text-green-600">
                    {jobData.stats.total_genes || 0}
                  </div>
                  <div className="text-green-700">Total Genes</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded">
                  <div className="text-2xl font-bold text-purple-600">
                    {jobData.stats.n_clusters || 0}
                  </div>
                  <div className="text-purple-700">Clusters</div>
                </div>
              </div>
            </div>
          )}

          {/* Download Links */}
          <div className="flex flex-wrap gap-3">
            <a
              href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/h5ad`}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              download
            >
              Download H5AD
            </a>
            <a
              href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/clusters`}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
              download
            >
              Download Clusters CSV
            </a>
            <a
              href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/archive`}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
              download
            >
              Download All Results
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetailsPage;