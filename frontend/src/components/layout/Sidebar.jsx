import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { jobsApi } from '../../services/api';
import StatusIndicator from '../ui/StatusIndicator';

const Sidebar = () => {
  const location = useLocation();
  const [recentJobs, setRecentJobs] = useState([]);
  const [systemStatus, setSystemStatus] = useState({ online: true, activeJobs: 0 });

  // Fetch recent jobs for quick access
  useEffect(() => {
    const fetchRecentJobs = async () => {
      try {
        const response = await jobsApi.getJobs({ limit: 5 });
        setRecentJobs(response.data.jobs);
        
        // Count active jobs
        const activeCount = response.data.jobs.filter(
          job => job.status === 'executing' || job.status === 'pending'
        ).length;
        setSystemStatus(prev => ({ ...prev, activeJobs: activeCount }));
      } catch (error) {
        setSystemStatus(prev => ({ ...prev, online: false }));
      }
    };

    fetchRecentJobs();
    const interval = setInterval(fetchRecentJobs, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const isActivePath = (path) => location.pathname === path;

  return (
    <div className="w-64 bg-white border-r border-slate-200 h-full flex flex-col">
      
      {/* Quick Actions */}
      <div className="p-4 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Quick Actions</h3>
        <div className="space-y-2">
          <Link
            to="/submit"
            className="w-full bio-button-primary flex items-center justify-center text-sm"
          >
            + New Analysis
          </Link>
          <Link
            to="/results"
            className="w-full bio-button-secondary flex items-center justify-center text-sm"
          >
            📊 View Results
          </Link>
        </div>
      </div>

      {/* System Status - REPLACE THIS SECTION */}
      <div className="p-4 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">System Status</h3>
        <StatusIndicator />
        
        <div className="mt-3 space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Active Jobs</span>
            <span className="font-medium text-slate-900">{systemStatus.activeJobs}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Queue Status</span>
            <span className="font-medium text-slate-900">
              {systemStatus.online ? 'Processing' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="p-4 flex-1">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Recent Jobs</h3>
        <div className="space-y-2">
          {recentJobs.length > 0 ? (
            recentJobs.map((job) => (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="block p-2 rounded-md hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-900 truncate">
                      {job.id.slice(0, 8)}...
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${
                    job.status === 'complete' ? 'bg-green-500' :
                    job.status === 'executing' ? 'bg-blue-500' :
                    job.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                </div>
              </Link>
            ))
          ) : (
            <p className="text-xs text-slate-500 italic">No recent jobs</p>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-200">
        <p className="text-xs text-slate-500">
          Platform v0.2.1
        </p>
      </div>
    </div>
  );
};

export default Sidebar;