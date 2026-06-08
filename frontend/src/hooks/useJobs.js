import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '../services/api';

// Query keys
export const jobKeys = {
  all: ['jobs'],
  lists: () => [...jobKeys.all, 'list'],
  list: (filters) => [...jobKeys.lists(), filters],
  details: () => [...jobKeys.all, 'detail'],
  detail: (id) => [...jobKeys.details(), id],
  results: (id) => [...jobKeys.all, 'results', id],
  presets: ['presets'],
};

// Get all jobs
export function useJobs(filters = {}) {
  return useQuery({
    queryKey: jobKeys.list(filters),
    queryFn: () => jobsApi.getJobs(filters).then((res) => res.data),
    refetchInterval: 5000, // Refetch every 5 seconds for job list
  });
}

// Get single job
export function useJob(jobId, options = {}) {
  return useQuery({
    queryKey: jobKeys.detail(jobId),
    queryFn: () => jobsApi.getJob(jobId).then((res) => res.data),
    enabled: !!jobId,
    ...options,
  });
}

// Get job results
export function useJobResults(jobId) {
  return useQuery({
    queryKey: jobKeys.results(jobId),
    queryFn: () => jobsApi.getResults(jobId).then((res) => res.data),
    enabled: !!jobId,
  });
}

// Get presets
export function usePresets() {
  return useQuery({
    queryKey: jobKeys.presets,
    queryFn: () => jobsApi.getPresets().then((res) => res.data),
  });
}

// Submit job mutation
export function useSubmitJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => jobsApi.submitJob(data).then((res) => res.data),
    onSuccess: () => {
      // Invalidate and refetch jobs list
      queryClient.invalidateQueries({ queryKey: jobKeys.lists() });
    },
  });
}

// Delete job mutation
export function useDeleteJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId) => jobsApi.deleteJob(jobId),
    onSuccess: () => {
      // Invalidate jobs list
      queryClient.invalidateQueries({ queryKey: jobKeys.lists() });
    },
  });
}