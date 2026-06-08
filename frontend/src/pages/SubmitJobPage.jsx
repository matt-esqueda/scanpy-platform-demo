import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePresets, useSubmitJob } from '../hooks/useJobs';

export default function SubmitJobPage() {
  const navigate = useNavigate();
  const { data: presetsData, isLoading: presetsLoading } = usePresets();
  const submitJobMutation = useSubmitJob();

  const [formData, setFormData] = useState({
    input_type: 'mtx',
    input_path: 'data/test_data/pbmc3k',
    preset: 'default',
  });

  const [selectedPreset, setSelectedPreset] = useState(null);

  useEffect(() => {
    if (presetsData?.presets && formData.preset) {
      const preset = presetsData.presets.find((p) => p.name === formData.preset);
      setSelectedPreset(preset);
    }
  }, [presetsData, formData.preset]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      input_type: formData.input_type,
      input_path: formData.input_path,
      preset: formData.preset,
    };

    if (formData.preset === 'custom' && selectedPreset) {
      payload.parameters = selectedPreset.parameters;
    }

    try {
      const result = await submitJobMutation.mutateAsync(payload);
      
      // --- DEBUGGING LOG ---
      // Log the object we are about to pass in the navigation state.
      console.log("Submitting job. API result received:", result);
      console.log("Navigating to details page with job state...");
      
      navigate(`/jobs/${result.id}`, { state: { job: result } });

    } catch (error) {
      console.error('Failed to submit job:', error);
    }
  };

  // ... (The rest of the file is unchanged)
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="px-4 sm:px-0">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Submit New Job</h2>
      <div className="bg-white shadow rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* ... (rest of the form is unchanged) ... */}
           {/* Input Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Input Type
            </label>
            <select
              name="input_type"
              value={formData.input_type}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            >
              <option value="mtx">Matrix Market (MTX)</option>
              <option value="h5">HDF5 (H5)</option>
            </select>
            <p className="mt-1 text-sm text-gray-500">
              Format of your input data files
            </p>
          </div>

          {/* Input Path */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Input Path
            </label>
            <input
              type="text"
              name="input_path"
              value={formData.input_path}
              onChange={handleChange}
              placeholder="/path/to/your/data"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              Full path to your 10x Genomics data directory
            </p>
          </div>

          {/* Preset Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Preset
            </label>
            {presetsLoading ? (
              <div className="text-sm text-gray-500">Loading presets...</div>
            ) : (
              <select
                name="preset"
                value={formData.preset}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {presetsData?.presets.map((preset) => (
                  <option key={preset.name} value={preset.name}>
                    {preset.name} - {preset.description}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Preset Parameters Display */}
          {selectedPreset && formData.preset !== 'custom' && (
            <div className="bg-gray-50 rounded-md p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                Preset Parameters
              </h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-600">Min Genes:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.min_genes}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Min Cells:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.min_cells}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Gene Count Range:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.n_genes_lower} -{' '}
                    {selectedPreset.parameters.n_genes_upper}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">MT % Cutoff:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.pct_mt_cutoff}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Leiden Resolution:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.leiden_resolution}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">N Neighbors:</span>
                  <span className="ml-2 font-medium">
                    {selectedPreset.parameters.n_neighbors}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {submitJobMutation.isError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-800 text-sm">
                Failed to submit job: {submitJobMutation.error.message}
              </p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitJobMutation.isPending}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-purple-400 disabled:cursor-not-allowed"
            >
              {submitJobMutation.isPending ? 'Submitting...' : 'Submit Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}