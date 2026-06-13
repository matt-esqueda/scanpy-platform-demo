import { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import { jobsApi } from '../services/api';
import PlotPreview from '../components/plots/PlotPreview';
import PlotGallery from '../components/plots/PlotGallery';

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

  const formatDuration = () => {
    if (!jobData.started_at || !jobData.completed_at) return 'N/A';
    const start = new Date(jobData.started_at);
    const end = new Date(jobData.completed_at);
    const duration = Math.round((end - start) / 1000); // seconds
    return duration < 60 ? `${duration}s` : `${Math.round(duration/60)}m ${duration%60}s`;
  };

  const getStatusBadge = () => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      executing: 'bg-blue-100 text-blue-800 animate-pulse',
      complete: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    
    return (
      <span className={`bio-status-badge ${badges[jobData?.status] || 'bg-slate-100 text-slate-800'}`}>
        {jobData?.status || 'unknown'}
      </span>
    );
  };

  const getProgressSteps = () => {
    const steps = [
      { name: 'Queued', key: 'pending', progress: 0 },
      { name: 'Loading Data', key: 'loading', progress: 10 },
      { name: 'Quality Control', key: 'qc_filter', progress: 30 },
      { name: 'Normalization', key: 'normalization', progress: 50 },
      { name: 'Clustering', key: 'clustering', progress: 70 },
      { name: 'Annotation', key: 'annotation', progress: 90 },
      { name: 'Complete', key: 'complete', progress: 100 }
    ];

    const currentProgress = jobData?.progress_percent || 0;
    
    return steps.map((step, index) => {
      const isCompleted = currentProgress > step.progress;
      const isCurrent = jobData?.current_step === step.key;
      
      return (
        <div key={step.key} className="flex items-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            isCompleted ? 'bg-green-500 text-white' :
            isCurrent ? 'bg-blue-500 text-white animate-pulse' :
            'bg-slate-200 text-slate-500'
          }`}>
            {isCompleted ? '✓' : index + 1}
          </div>
          <div className="ml-3 flex-1">
            <p className={`text-sm font-medium ${isCurrent ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-slate-500'}`}>
              {step.name}
            </p>
          </div>
          {index < steps.length - 1 && (
            <div className={`w-16 h-0.5 ${isCompleted ? 'bg-green-500' : 'bg-slate-200'}`}></div>
          )}
        </div>
      );
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-slate-600">Loading job details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bio-card p-6 max-w-2xl mx-auto">
        <div className="text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-red-600 text-xl">⚠️</span>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Error Loading Job</h3>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchJobState();
            }}
            className="bio-button-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!jobData) {
    return (
      <div className="bio-card p-6 max-w-2xl mx-auto">
        <div className="text-center">
          <p className="text-slate-600">Job not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bio-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Analysis Job
            </h1>
            <p className="text-slate-600">ID: {jobData.id}</p>
          </div>
          <div className="flex items-center space-x-3">
            {getStatusBadge()}
            <div className="flex items-center space-x-2 text-sm text-slate-500">
              <span>WebSocket:</span>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-slate-400'}`}></div>
            </div>
          </div>
        </div>

        {/* Timeline Progress */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-slate-900 mb-4">Progress Timeline</h3>
          <div className="space-y-4">
            {getProgressSteps()}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-slate-600 mb-2">
            <span>{jobData.current_step?.replace('_', ' ') || 'Initializing...'}</span>
            <span>{jobData.progress_percent}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ${
                jobData.status === 'complete' ? 'bg-green-500' : 
                jobData.status === 'failed' ? 'bg-red-500' : 
                jobData.status === 'executing' ? 'bg-blue-500' : 'bg-slate-400'
              }`}
              style={{ width: `${jobData.progress_percent}%` }}
            />
          </div>
        </div>

        {/* Job Metrics */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center p-3 bg-slate-50 rounded-lg">
            <div className="font-semibold text-slate-900">
              {formatDate(jobData.created_at)}
            </div>
            <div className="text-slate-500">Created</div>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-lg">
            <div className="font-semibold text-slate-900">
              {formatDuration()}
            </div>
            <div className="text-slate-500">Duration</div>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-lg">
            <div className="font-semibold text-slate-900">
              {jobData.preset || 'Custom'}
            </div>
            <div className="text-slate-500">Preset</div>
          </div>
        </div>

        {/* Error Message */}
        {jobData.status === 'failed' && jobData.error_message && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="text-sm font-semibold text-red-800 mb-2">Error Details</h4>
            <p className="text-sm text-red-700">{jobData.error_message}</p>
          </div>
        )}
      </div>

      {/* Configuration */}
      <div className="bio-card p-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Configuration</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="font-medium text-slate-900">Input Format</div>
            <div className="text-slate-600">{jobData.input_type?.toUpperCase()}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="font-medium text-slate-900">Min Genes</div>
            <div className="text-slate-600">{jobData.parameters?.min_genes || 'N/A'}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="font-medium text-slate-900">Resolution</div>
            <div className="text-slate-600">{jobData.parameters?.leiden_resolution || 'N/A'}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="font-medium text-slate-900">MT Cutoff</div>
            <div className="text-slate-600">{jobData.parameters?.pct_mt_cutoff || 'N/A'}%</div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-slate-50 rounded-lg">
          <div className="font-medium text-slate-900 mb-1">Input Path</div>
          <div className="text-slate-600 font-mono text-xs">{jobData.input_path}</div>
        </div>
      </div>
      {/* Results Section - Only show if complete */}
      {jobData.status === 'complete' && (
        <>
          {/* Statistics */}
          {jobData.stats && (
            <div className="bio-card p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Analysis Results</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {jobData.stats.total_cells_analyzed?.toLocaleString() || 0}
                  </div>
                  <div className="text-blue-700 text-sm font-medium">Cells Analyzed</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {jobData.stats.total_genes?.toLocaleString() || 0}
                  </div>
                  <div className="text-green-700 text-sm font-medium">Total Genes</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {jobData.stats.n_clusters || 0}
                  </div>
                  <div className="text-purple-700 text-sm font-medium">Clusters Found</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {Math.round(((jobData.stats.post_filter_cells || 0) / (jobData.stats.pre_filter_cells || 1)) * 100)}%
                  </div>
                  <div className="text-orange-700 text-sm font-medium">Cells Retained</div>
                </div>
              </div>
            </div>
          )}

          {/* Plot Gallery */}
                    {jobData.plots && jobData.plots.length > 0 && (
                      <PlotGallery plots={jobData.plots} jobId={jobData.id} />
                    )}

          {/* Download Section */}
          <div className="bio-card p-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">Download Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-slate-200 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-blue-600 font-bold">H5</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">Analysis Data</h3>
                    <p className="text-sm text-slate-500">H5AD format</p>
                  </div>
                </div>
                <a
                  href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/h5ad`}
                  className="w-full bio-button-primary text-center block"
                  download
                >
                  Download H5AD
                </a>
              </div>

              <div className="p-4 border border-slate-200 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <span className="text-green-600 font-bold">CSV</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">Cluster Data</h3>
                    <p className="text-sm text-slate-500">Cell assignments</p>
                  </div>
                </div>
                <a
                  href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/clusters`}
                  className="w-full bio-button-secondary text-center block"
                  download
                >
                  Download CSV
                </a>
              </div>

              <div className="p-4 border border-slate-200 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <span className="text-purple-600 font-bold">ZIP</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">Complete Archive</h3>
                    <p className="text-sm text-slate-500">All files</p>
                  </div>
                </div>
                <a
                  href={`http://localhost:8000/api/scanpy/jobs/${jobData.id}/download/archive`}
                  className="w-full bio-button-primary text-center block"
                  download
                >
                  Download All
                </a>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default JobDetailsPage;