import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Job endpoints
export const jobsApi = {
  // Submit a new job
  submitJob: (data) => api.post('/scanpy/jobs/submit', data),
  
  // Get all jobs
  getJobs: (params = {}) => api.get('/scanpy/jobs', { params }),
  
  // Get specific job
  getJob: (jobId) => api.get(`/scanpy/jobs/${jobId}`),
  
  // Delete job
  deleteJob: (jobId) => api.delete(`/scanpy/jobs/${jobId}`),
  
  // Get job results
  getResults: (jobId) => api.get(`/scanpy/jobs/${jobId}/results`),
  
  // Get presets
  getPresets: () => api.get('/scanpy/presets'),
};

// Download endpoints
export const downloadApi = {
  getH5adUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/h5ad`,
  getCsvUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/clusters`,
  getArchiveUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/archive`,
  getPlotUrl: (plotId) => `${API_BASE_URL}/scanpy/plots/${plotId}`,
};

export default api;