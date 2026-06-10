import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobsApi } from '../services/api';

export default function SubmitJobPage() {
  const [formData, setFormData] = useState({
    input_type: 'mtx',
    input_path: 'data/test_data/pbmc3k',
    preset: 'default',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('Submitting job. Form data:', formData);
      const response = await jobsApi.submitJob(formData);
      console.log('Submitting job. API result received:', response.data);
      console.log('Navigating to details page with job state...');
      
      navigate(`/jobs/${response.data.id}`, {
        state: { job: response.data }
      });
    } catch (err) {
      console.error('Job submission failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to submit job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="px-4 sm:px-0">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">New Scanpy Analysis</h1>
        <p className="mt-2 text-slate-600">
          Configure and submit a single-cell RNA-seq analysis job
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bio-card p-6 space-y-6">
            
            {/* Input Configuration */}
            <div>
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Input Configuration</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Input Type */}
                <div>
                  <label htmlFor="input_type" className="block text-sm font-medium text-slate-700 mb-2">
                    Input Format
                  </label>
                  <select
                    id="input_type"
                    name="input_type"
                    value={formData.input_type}
                    onChange={handleInputChange}
                    className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="mtx">Matrix Market (.mtx)</option>
                    <option value="h5">HDF5 (.h5)</option>
                  </select>
                </div>

                {/* Preset */}
                <div>
                  <label htmlFor="preset" className="block text-sm font-medium text-slate-700 mb-2">
                    Analysis Preset
                  </label>
                  <select
                    id="preset"
                    name="preset"
                    value={formData.preset}
                    onChange={handleInputChange}
                    className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="default">Default (Standard QC)</option>
                    <option value="stringent">Stringent (Strict filtering)</option>
                  </select>
                </div>
              </div>

              {/* Input Path */}
              <div className="mt-6">
                <label htmlFor="input_path" className="block text-sm font-medium text-slate-700 mb-2">
                  Input Path
                </label>
                <input
                  type="text"
                  id="input_path"
                  name="input_path"
                  value={formData.input_path}
                  onChange={handleInputChange}
                  placeholder="data/test_data/pbmc3k"
                  className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-red-800 mb-1">Submission Failed</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end pt-4">
              <button
                type="submit"
                disabled={isSubmitting}
                className={`px-6 py-3 rounded-md text-sm font-medium transition-colors ${
                  isSubmitting
                    ? 'bg-slate-400 text-white cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isSubmitting ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Starting Analysis...</span>
                  </div>
                ) : (
                  'Start Analysis'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Info Sidebar */}
        <div className="space-y-6">
          
          {/* Analysis Info */}
          <div className="bio-card p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Analysis Pipeline</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Data loading and validation</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Quality control filtering</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Normalization and scaling</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Leiden clustering</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Cell type annotation</span>
              </li>
            </ul>
          </div>

          {/* Preset Info */}
          <div className="bio-card p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Preset Details</h3>
            {formData.preset === 'default' ? (
              <div className="text-sm text-slate-600 space-y-2">
                <p><strong>Target:</strong> Standard PBMC data</p>
                <p><strong>Min genes:</strong> 200 per cell</p>
                <p><strong>Gene range:</strong> 1,800-6,000 per cell</p>
                <p><strong>MT cutoff:</strong> 6%</p>
                <p><strong>Resolution:</strong> 0.2</p>
              </div>
            ) : (
              <div className="text-sm text-slate-600 space-y-2">
                <p><strong>Target:</strong> High-quality analysis</p>
                <p><strong>Min genes:</strong> 500 per cell</p>
                <p><strong>Gene range:</strong> 2,000-5,000 per cell</p>
                <p><strong>MT cutoff:</strong> 5%</p>
                <p><strong>Resolution:</strong> 0.3</p>
              </div>
            )}
          </div>

          {/* Expected Results */}
          <div className="bio-card p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Expected Results</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>• Quality control plots</li>
              <li>• UMAP visualization</li>
              <li>• Cluster assignments</li>
              <li>• Cell type predictions</li>
              <li>• Downloadable H5AD file</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}