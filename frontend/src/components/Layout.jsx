// src/components/Layout.jsx
import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path
      ? 'bg-purple-100 text-purple-700'
      : 'text-gray-700 hover:bg-gray-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col"> {/* Added flex flex-col */}
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            
            {/* This is the line that changed */}
            <div className="flex items-center"> {/* <-- ADDED items-center here */}
              
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-purple-600">
                  Scanpy Platform
                </h1>
              </div>
              <div className="ml-10 flex space-x-4"> {/* Adjusted spacing for better balance */}
                <Link
                  to="/"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
                >
                  Jobs
                </Link>
                <Link
                  to="/submit"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/submit')}`}
                >
                  Submit Job
                </Link>
              </div>
            </div>
            
            <div className="flex items-center">
              <span className="text-sm text-gray-500">
                Single-cell RNA-seq Analysis
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 w-full"> {/* Added w-full */}
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Scanpy Analysis Platform v0.1.0
          </p>
        </div>
      </footer>
    </div>
  );
}