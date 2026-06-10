import { useState } from 'react';
import Plot from 'react-plotly.js';

const PlotPreview = ({ plotId, plotType, thumbnailUrl, plotData = null }) => {
  const [showModal, setShowModal] = useState(false);
  const [plotLoading, setPlotLoading] = useState(false);

  // For now, we'll show static images, but prepare for interactive plots
  const handleViewFullPlot = () => {
    setShowModal(true);
  };

  return (
    <>
      {/* Plot Thumbnail */}
      <div className="bio-card overflow-hidden">
        <div className="aspect-w-16 aspect-h-12 bg-slate-50">
          {thumbnailUrl ? (
            <img 
              src={thumbnailUrl}
              alt={plotType}
              className="w-full h-32 object-cover hover:opacity-75 transition-opacity cursor-pointer"
              onClick={handleViewFullPlot}
            />
          ) : (
            <div className="flex items-center justify-center h-32 bg-slate-100">
              <div className="text-center">
                <div className="w-8 h-8 mx-auto mb-2 bg-slate-300 rounded animate-pulse"></div>
                <p className="text-xs text-slate-500">Generating plot...</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="p-3">
          <h4 className="text-sm font-medium text-slate-900 capitalize">
            {plotType.replace(/_/g, ' ')}
          </h4>
          <button 
            onClick={handleViewFullPlot}
            className="mt-2 text-xs text-blue-600 hover:text-blue-700 transition-colors"
          >
            View Full Plot →
          </button>
        </div>
      </div>

      {/* Modal for Full Plot View */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 capitalize">
                {plotType.replace(/_/g, ' ')}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold"
              >
                ×
              </button>
            </div>
            
            <div className="p-4">
              {plotData ? (
                // Future: Interactive Plotly plot
                <Plot 
                  data={plotData.data}
                  layout={{
                    ...plotData.layout,
                    autosize: true,
                    margin: { t: 50, r: 50, b: 50, l: 50 }
                  }}
                  style={{ width: '100%', height: '500px' }}
                  config={{ 
                    displayModeBar: true,
                    toImageButtonOptions: {
                      format: 'png',
                      filename: plotType,
                      height: 500,
                      width: 700,
                      scale: 1
                    }
                  }}
                />
              ) : (
                // Current: Static image in modal
                <div className="text-center">
                  <img 
                    src={thumbnailUrl}
                    alt={plotType}
                    className="max-w-full max-h-96 mx-auto"
                  />
                  <p className="mt-4 text-sm text-slate-600">
                    Interactive plot visualization coming soon
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PlotPreview;