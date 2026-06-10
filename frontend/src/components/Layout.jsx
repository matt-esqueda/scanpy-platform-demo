import Header from './layout/Header';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* New Professional Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 w-full">
        {children}
      </main>

      {/* Updated Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-500">
              Scanpy Analysis Platform v0.2.1
            </p>
            <div className="flex items-center space-x-4 text-xs text-slate-400">
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