import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with retry logic
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding retry count
api.interceptors.request.use(
  (config) => {
    config.retryCount = config.retryCount || 0;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for retry logic and error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Don't retry if we've already retried too many times
    if (!config || config.retryCount >= 3) {
      return Promise.reject(enhanceError(error));
    }

    // Only retry on network errors or 5xx server errors
    const shouldRetry = !error.response || 
                       error.response.status >= 500 || 
                       error.code === 'NETWORK_ERROR' ||
                       error.code === 'ECONNABORTED';
    
    if (shouldRetry) {
      config.retryCount += 1;
      
      // Exponential backoff: wait 1s, 2s, 4s
      const delay = Math.pow(2, config.retryCount - 1) * 1000;
      
      console.log(`Retrying request (attempt ${config.retryCount}/3) after ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return api(config);
    }

    return Promise.reject(enhanceError(error));
  }
);

// Enhanced error object with user-friendly messages
function enhanceError(error) {
  const enhancedError = {
    ...error,
    isNetworkError: !error.response,
    isServerError: error.response?.status >= 500,
    isClientError: error.response?.status >= 400 && error.response?.status < 500,
    userMessage: getUserFriendlyMessage(error),
    originalError: error
  };

  return enhancedError;
}

function getUserFriendlyMessage(error) {
  // Network errors
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please check your internet connection and try again.';
    }
    return 'Unable to connect to the server. Please check your internet connection.';
  }

  // Server errors
  if (error.response.status >= 500) {
    return 'Server error occurred. Our team has been notified. Please try again later.';
  }

  // Client errors
  if (error.response.status === 404) {
    return 'The requested resource was not found.';
  }
  
  if (error.response.status === 403) {
    return 'You do not have permission to access this resource.';
  }
  
  if (error.response.status === 401) {
    return 'Authentication required. Please log in and try again.';
  }

  // Use server message if available, otherwise generic
  return error.response?.data?.detail || 
         error.response?.data?.message || 
         `Request failed with status ${error.response.status}`;
}

// Job endpoints with enhanced error handling
export const jobsApi = {
  // Submit a new job
  submitJob: async (data) => {
    try {
      return await api.post('/scanpy/jobs/submit', data);
    } catch (error) {
      console.error('Failed to submit job:', error);
      throw error;
    }
  },
  
  // Get all jobs
  getJobs: async (params = {}) => {
    try {
      return await api.get('/scanpy/jobs', { params });
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      throw error;
    }
  },
  
  // Get specific job
  getJob: async (jobId) => {
    try {
      return await api.get(`/scanpy/jobs/${jobId}`);
    } catch (error) {
      console.error(`Failed to fetch job ${jobId}:`, error);
      throw error;
    }
  },
  
  // Delete job
  deleteJob: async (jobId) => {
    try {
      return await api.delete(`/scanpy/jobs/${jobId}`);
    } catch (error) {
      console.error(`Failed to delete job ${jobId}:`, error);
      throw error;
    }
  },
  
  // Get job results
  getResults: async (jobId) => {
    try {
      return await api.get(`/scanpy/jobs/${jobId}/results`);
    } catch (error) {
      console.error(`Failed to fetch results for job ${jobId}:`, error);
      throw error;
    }
  },
  
  // Get presets
  getPresets: async () => {
    try {
      return await api.get('/scanpy/presets');
    } catch (error) {
      console.error('Failed to fetch presets:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      return await fetch('/health', { timeout: 5000 });
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

// Download endpoints (same as before but with better error handling)
export const downloadApi = {
  getH5adUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/h5ad`,
  getCsvUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/clusters`,
  getArchiveUrl: (jobId) => `${API_BASE_URL}/scanpy/jobs/${jobId}/download/archive`,
  getPlotUrl: (plotId) => `${API_BASE_URL}/scanpy/plots/${plotId}`,
};

export default api;