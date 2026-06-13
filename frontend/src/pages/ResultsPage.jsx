import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../services/api';

export default function ResultsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalJobs: 0,
    completedJobs: 0,
    totalCells: 0,
    totalPlots: 0,
    successRate: 0,
    avgDuration: 0
  });

  useEffect(() => {
    fetchJobsAndStats();
  }, []);

  const fetchJobsAndStats = async () => {
    try {
      const response = await jobsApi.getJobs({ limit: 100 });
      const allJobs = response.data.jobs;
      setJobs(allJobs);
      
      // Calculate statistics
      const completed = allJobs.filter(job => job.status === 'complete');
      const failed = allJobs.filter(job => job.status === 'failed');
      
      const totalCells = completed.reduce((sum, job) => {
        return sum + (job.stats?.total_cells_analyzed || 0);
      }, 0);
      
      const totalPlots = completed.reduce((sum, job) => {
        return sum + (job.plots?.length || 0);
      }, 0);
      
      const durations = completed
        .filter(job => job.started_at && job.completed_at)
        .map(job => {
          const start = new Date(job.started_at);
          const end = new Date(job.completed_at);
          return (end - start) / 1000; // seconds
        });
      
      const avgDuration = durations.length > 0 
        ? durations.reduce((sum, d) => sum + d, 0) / durations.length 
        : 0;

      setStats({
        totalJobs: allJobs.length,
        completedJobs: completed.length,
        totalCells,
        totalPlots,
        successRate: allJobs.length > 0 ? Math.round((completed.length / (completed.length + failed.length)) * 100) : 0,
        avgDuration: Math.round(avgDuration)
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getRecentActivity = () => {
    return jobs
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 10);
  };

  const getStatusDistribution = () => {
    const distribution = jobs.reduce((acc, job) => {
      acc[job.status] = (acc[job.status] || 0) + 1;
      return acc;
    }, {});
    
    return [
      { status: 'Complete', count: distribution.complete || 0, color: 'bg-green-500', bgColor: 'bg-green-50' },
      { status: 'Executing', count: distribution.executing || 0, color: 'bg-blue-500', bgColor: 'bg-blue-50' },
      { status: 'Pending', count: distribution.pending || 0, color: 'bg-yellow-500', bgColor: 'bg-yellow-50' },
      { status: 'Failed', count: distribution.failed || 0, color: 'bg-red-500', bgColor: 'bg-red-50' },
    ];
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics Dashboard</h1>
          <p className="mt-1 text-slate-600">Overview of your analysis platform performance</p>
        </div>
        <Link
          to="/submit"
          className="bio-button-primary"
        >
          + New Analysis
        </Link>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bio-card p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {stats.totalJobs.toLocaleString()}
          </div>
          <div className="text-sm font-medium text-slate-700">Total Analyses</div>
          <div className="text-xs text-slate-500 mt-1">All time</div>
        </div>

        <div className="bio-card p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {stats.totalCells.toLocaleString()}
          </div>
          <div className="text-sm font-medium text-slate-700">Cells Processed</div>
          <div className="text-xs text-slate-500 mt-1">Across all jobs</div>
        </div>

        <div className="bio-card p-6 text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {stats.successRate}%
          </div>
          <div className="text-sm font-medium text-slate-700">Success Rate</div>
          <div className="text-xs text-slate-500 mt-1">Completed vs failed</div>
        </div>

        <div className="bio-card p-6 text-center">
          <div className="text-3xl font-bold text-orange-600 mb-2">
            {formatDuration(stats.avgDuration)}
          </div>
          <div className="text-sm font-medium text-slate-700">Avg Duration</div>
          <div className="text-xs text-slate-500 mt-1">Per analysis</div>
        </div>
      </div>

      {/* Status Distribution and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Status Distribution */}
        <div className="bio-card p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Job Status Distribution</h3>
          <div className="space-y-3">
            {getStatusDistribution().map((item) => (
              <div key={item.status} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                  <span className="text-sm font-medium text-slate-700">{item.status}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${item.bgColor} text-slate-700`}>
                    {item.count}
                  </div>
                  <div className="text-xs text-slate-500">
                    {stats.totalJobs > 0 ? Math.round((item.count / stats.totalJobs) * 100) : 0}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bio-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Recent Activity</h3>
            <Link to="/" className="text-sm text-blue-600 hover:text-blue-700">View all →</Link>
          </div>
          <div className="space-y-3">
            {getRecentActivity().map((job) => (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="block p-3 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        Job {job.id.slice(0, 8)}...
                      </p>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        job.status === 'complete' ? 'bg-green-100 text-green-800' :
                        job.status === 'executing' ? 'bg-blue-100 text-blue-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(job.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-xs text-slate-400">
                    {job.stats?.total_cells_analyzed ? `${job.stats.total_cells_analyzed.toLocaleString()} cells` : ''}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bio-card p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/submit"
            className="p-4 border-2 border-dashed border-slate-300 rounded-lg hover:border-blue-400 transition-colors text-center group"
          >
            <div className="text-2xl mb-2">🧬</div>
            <div className="font-medium text-slate-900 group-hover:text-blue-600">New Analysis</div>
            <div className="text-sm text-slate-500">Start a Scanpy workflow</div>
          </Link>
          
          <Link
            to="/"
            className="p-4 border-2 border-dashed border-slate-300 rounded-lg hover:border-green-400 transition-colors text-center group"
          >
            <div className="text-2xl mb-2">📊</div>
            <div className="font-medium text-slate-900 group-hover:text-green-600">Browse Jobs</div>
            <div className="text-sm text-slate-500">View all analyses</div>
          </Link>
          
          <div className="p-4 border-2 border-dashed border-slate-300 rounded-lg opacity-50 text-center">
            <div className="text-2xl mb-2">⚡</div>
            <div className="font-medium text-slate-900">Bulk RNA-seq</div>
            <div className="text-sm text-slate-500">Coming soon</div>
          </div>
        </div>
      </div>
    </div>
  );
}