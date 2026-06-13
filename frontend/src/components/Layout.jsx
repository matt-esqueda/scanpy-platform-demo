import Header from './layout/Header';
import Sidebar from './layout/Sidebar';
import { useState } from 'react';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <Header />

      {/* Main Content with Responsive Sidebar */}
      <div className="flex-1 flex relative">
        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:relative z-50 lg:z-auto w-64 h-full transition-transform duration-300 ease-in-out lg:transition-none`}>
          <Sidebar />
        </div>

        {/* Mobile Sidebar Toggle */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-20 left-4 z-30 p-2 bg-white rounded-md shadow-md border border-slate-200"
        >
          <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        
        {/* Main Content Area */}
        <main className="flex-1 py-6 px-4 lg:px-6 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
            <p className="text-sm text-slate-500">
              Scanpy Analysis Platform v0.2.1
            </p>
            <div className="flex items-center space-x-4 text-xs text-slate-400 mt-2 sm:mt-0">
              <span>Built with React + FastAPI</span>
              <span>•</span>
              <span>Real-time WebSocket updates</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}