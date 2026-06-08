export default function ProgressBar({ progress, status, currentStep }) {
  const getStatusColor = () => {
    switch (status) {
      case 'complete':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'executing':
        return 'bg-blue-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'executing':
        return `Running: ${currentStep}`;
      case 'complete':
        return 'Complete';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="w-full">
      <div className="flex justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">
          {getStatusText()}
        </span>
        <span className="text-sm font-medium text-gray-700">
          {progress}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}