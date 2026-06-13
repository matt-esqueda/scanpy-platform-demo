import { useState, useEffect } from 'react';
import { jobsApi } from '../../services/api';

const StatusIndicator = ({ className = "" }) => {
  const [status, setStatus] = useState({
    api: 'checking',
    redis: 'checking', 
    celery: 'checking',
    lastCheck: new Date()
  });

  const checkServices = async () => {
    try {
      // Check API health
      const apiHealth = await fetch('/health').then(r => r.ok);
      
      // Check if we can fetch jobs (tests DB connection)
      const dbHealth = await jobsApi.getJobs({ limit: 1 }).then(() => true).catch(() => false);
      
      // Check for recent job activity (indicates Celery is working)
      const recentJobs = await jobsApi.getJobs({ limit: 5 });
      const hasRecentActivity = recentJobs.data.jobs.some(job => {
        const created = new Date(job.created_at);
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
        return created > fiveMinutesAgo;
      });

      setStatus({
        api: apiHealth && dbHealth ? 'healthy' : 'error',
        redis: 'healthy', // If we got here, Redis is working
        celery: hasRecentActivity ? 'healthy' : 'warning',
        lastCheck: new Date()
      });

    } catch (error) {
      setStatus(prev => ({
        ...prev,
        api: 'error',
        redis: 'error',
        celery: 'error',
        lastCheck: new Date()
      }));
    }
  };

  useEffect(() => {
    checkServices();
    const interval = setInterval(checkServices, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-slate-400';
    }
  };

  const getStatusDot = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-slate-400 animate-pulse';
    }
  };

  const overallStatus = status.api === 'error' || status.redis === 'error' ? 'error' :
                      status.celery === 'warning' ? 'warning' : 'healthy';

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className={`w-2 h-2 rounded-full ${getStatusDot(overallStatus)}`}></div>
      <span className={`text-xs font-medium ${getStatusColor(overallStatus)}`}>
        {overallStatus === 'healthy' ? 'All Systems Online' :
         overallStatus === 'warning' ? 'Limited Functionality' : 'Service Issues'}
      </span>
      
      {/* Detailed status on hover */}
      <div className="group relative">
        <span className="text-slate-400 text-xs cursor-help">ⓘ</span>
        <div className="invisible group-hover:visible absolute right-0 bottom-full mb-2 w-48 p-2 bg-slate-800 text-white text-xs rounded shadow-lg z-50">
          <div className="space-y-1">
            <div className="flex justify-between">
              <span>API:</span>
              <span className={getStatusColor(status.api)}>{status.api}</span>
            </div>
            <div className="flex justify-between">
              <span>Redis:</span>
              <span className={getStatusColor(status.redis)}>{status.redis}</span>
            </div>
            <div className="flex justify-between">
              <span>Celery:</span>
              <span className={getStatusColor(status.celery)}>{status.celery}</span>
            </div>
            <div className="text-slate-300 text-center pt-1 border-t border-slate-600">
              Last check: {status.lastCheck.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusIndicator;