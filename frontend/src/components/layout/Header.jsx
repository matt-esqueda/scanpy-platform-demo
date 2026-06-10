import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const [analysesOpen, setAnalysesOpen] = useState(false);
  const location = useLocation();

  const isActiveRoute = (href) => {
    if (href === '/' && location.pathname === '/') return true;
    if (href !== '/' && location.pathname.startsWith(href)) return true;
    return false;
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">SC</span>
            </div>
            <div>
              <h1 className="text-white text-lg font-semibold">Scanpy Platform</h1>
              <p className="text-slate-400 text-xs">Single-cell analysis</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-2">
            <Link 
              to="/" 
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActiveRoute('/') 
                  ? 'text-white bg-slate-800' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              Jobs
            </Link>
            
            <div className="relative">
              <button
                onClick={() => setAnalysesOpen(!analysesOpen)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center ${
                  analysesOpen || location.pathname === '/submit'
                    ? 'text-white bg-slate-800'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                Analyses ↓
              </button>
              
              {analysesOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50">
                  <Link 
                    to="/submit" 
                    className="block px-4 py-3 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                    onClick={() => setAnalysesOpen(false)}
                  >
                    <div className="font-medium">Scanpy Analysis</div>
                    <div className="text-xs text-slate-500">Single-cell RNA-seq analysis</div>
                  </Link>
                  <div className="block px-4 py-3 text-sm text-slate-400 cursor-not-allowed">
                    <div className="font-medium">Bulk RNA-seq</div>
                    <div className="text-xs text-slate-400">Coming soon</div>
                  </div>
                  <div className="block px-4 py-3 text-sm text-slate-400 cursor-not-allowed">
                    <div className="font-medium">ATAC-seq</div>
                    <div className="text-xs text-slate-400">Coming soon</div>
                  </div>
                </div>
              )}
            </div>

            <Link 
              to="/results" 
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActiveRoute('/results') 
                  ? 'text-white bg-slate-800' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              Results
            </Link>

            <Link
              to="/submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium ml-4 transition-colors"
            >
              New Analysis
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;