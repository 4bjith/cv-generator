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
import {
  ClarificationAnswerRequest,
  ClarificationBulkAnswerRequest,
  ClarificationPromoteRequest,
  ClarificationSessionResponse,
} from "@/types/clarification";
import { CVTailorRequest, CVTailoringResponse } from "@/types/tailoring";
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

// ==========================================
// Clarification Engine Hooks
// ==========================================

export function useClarificationSession(jobId?: string) {
  return useQuery<ClarificationSessionResponse, ApiClientError>({
    queryKey: jobKeys.clarifications(jobId || ""),
    queryFn: () => jobsApi.getClarifications(jobId!),
    enabled: Boolean(jobId),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useAnswerClarificationQuestion() {
  const queryClient = useQueryClient();

  return useMutation<
    ClarificationSessionResponse,
    ApiClientError,
    { jobId: string; questionId: string; payload: ClarificationAnswerRequest }
  >({
    mutationFn: ({ jobId, questionId, payload }) =>
      jobsApi.answerClarificationQuestion(jobId, questionId, payload),
    onSuccess: (data, { jobId }) => {
      queryClient.setQueryData(jobKeys.clarifications(jobId), data);
      queryClient.invalidateQueries({ queryKey: jobKeys.detail(jobId) });
    },
  });
}

export function useSkipClarificationQuestion() {
  const queryClient = useQueryClient();

  return useMutation<
    ClarificationSessionResponse,
    ApiClientError,
    { jobId: string; questionId: string }
  >({
    mutationFn: ({ jobId, questionId }) =>
      jobsApi.skipClarificationQuestion(jobId, questionId),
    onSuccess: (data, { jobId }) => {
      queryClient.setQueryData(jobKeys.clarifications(jobId), data);
    },
  });
}

export function usePromoteClarification() {
  const queryClient = useQueryClient();

  return useMutation<
    { status: string; requirement: string },
    ApiClientError,
    { jobId: string; questionId: string; payload: ClarificationPromoteRequest }
  >({
    mutationFn: ({ jobId, questionId, payload }) =>
      jobsApi.promoteClarificationAnswer(jobId, questionId, payload),
    onSuccess: (_, { jobId }) => {
      queryClient.invalidateQueries({ queryKey: jobKeys.clarifications(jobId) });
    },
  });
}

export function useBulkAnswerClarifications() {
  const queryClient = useQueryClient();

  return useMutation<
    ClarificationSessionResponse,
    ApiClientError,
    { jobId: string; payload: ClarificationBulkAnswerRequest }
  >({
    mutationFn: ({ jobId, payload }) =>
      jobsApi.bulkAnswerClarifications(jobId, payload),
    onSuccess: (data, { jobId }) => {
      queryClient.setQueryData(jobKeys.clarifications(jobId), data);
    },
  });
}

// ==========================================
// Evidence-Grounded AI CV Tailoring Hooks
// ==========================================

export function useTailorCv() {
  const queryClient = useQueryClient();

  return useMutation<
    CVTailoringResponse,
    ApiClientError,
    { jobId: string; payload?: CVTailorRequest }
  >({
    mutationFn: ({ jobId, payload }) => jobsApi.tailorCv(jobId, payload),
    onSuccess: (data, { jobId }) => {
      queryClient.invalidateQueries({ queryKey: jobKeys.versions(jobId) });
      queryClient.invalidateQueries({ queryKey: ["cv"] });
    },
  });
}

