import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { jobKeys } from "@/lib/query-keys";
import { jobsApi } from "@/services/jobs/jobs.api";
import { CVVersionListResponse } from "@/types/cv";
import {
  JobAnalysisResponse,
  JobExtractionResult,
  JobTarget,
  JobTargetCreate,
  JobTargetFilters,
  JobTargetListResponse,
  JobTargetUpdate,
} from "@/types/job";
import { ApiClientError } from "@/lib/api/errors";

export function useJobList(filters?: JobTargetFilters) {
  return useQuery<JobTargetListResponse, ApiClientError>({
    queryKey: jobKeys.list(filters),
    queryFn: () => jobsApi.listJobs(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useJobDetail(id?: string) {
  return useQuery<JobTarget, ApiClientError>({
    queryKey: jobKeys.detail(id || ""),
    queryFn: () => jobsApi.getJob(id!),
    enabled: Boolean(id),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateJob() {
  const queryClient = useQueryClient();

  return useMutation<JobTarget, ApiClientError, JobTargetCreate>({
    mutationFn: (payload) => jobsApi.createJob(payload),
    onSuccess: (newJob) => {
      queryClient.invalidateQueries({ queryKey: jobKeys.all });
      queryClient.setQueryData(jobKeys.detail(newJob.id), newJob);
    },
  });
}

export function useUpdateJob() {
  const queryClient = useQueryClient();

  return useMutation<JobTarget, ApiClientError, { id: string; payload: JobTargetUpdate }>({
    mutationFn: ({ id, payload }) => jobsApi.updateJob(id, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: jobKeys.all });
      queryClient.setQueryData(jobKeys.detail(updated.id), updated);
    },
  });
}

export function useDeleteJob() {
  const queryClient = useQueryClient();

  return useMutation<void, ApiClientError, string>({
    mutationFn: (id) => jobsApi.deleteJob(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: jobKeys.all });
      queryClient.removeQueries({ queryKey: jobKeys.detail(id) });
    },
  });
}

export function useJobAnalysis(jobId?: string) {
  return useQuery<JobAnalysisResponse, ApiClientError>({
    queryKey: jobKeys.analysis(jobId || ""),
    queryFn: () => jobsApi.getJobAnalysis(jobId!),
    enabled: Boolean(jobId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useAnalyzeJob() {
  const queryClient = useQueryClient();

  return useMutation<JobAnalysisResponse, ApiClientError, string>({
    mutationFn: (jobId) => jobsApi.analyzeJob(jobId),
    onSuccess: (data, jobId) => {
      queryClient.setQueryData(jobKeys.analysis(jobId), data);
      queryClient.invalidateQueries({ queryKey: jobKeys.detail(jobId) });
      queryClient.invalidateQueries({ queryKey: jobKeys.lists() });
    },
  });
}

export function useExtractRequirements() {
  return useMutation<
    JobExtractionResult,
    ApiClientError,
    { job_description: string; title?: string; company_name?: string }
  >({
    mutationFn: (payload) => jobsApi.extractRequirements(payload),
  });
}

export function useJobCvVersions(jobId?: string) {
  return useQuery<CVVersionListResponse, ApiClientError>({
    queryKey: jobKeys.versions(jobId || ""),
    queryFn: () => jobsApi.getJobCvVersions(jobId!),
    enabled: Boolean(jobId),
    staleTime: 1000 * 60 * 2,
  });
}
