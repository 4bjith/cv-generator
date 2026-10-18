import { apiClient } from "@/lib/api/axios";
import {
  ClarificationAnswerRequest,
  ClarificationBulkAnswerRequest,
  ClarificationPromoteRequest,
  ClarificationSessionResponse,
} from "@/types/clarification";
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
import { CVTailorRequest, CVTailoringResponse } from "@/types/tailoring";

/**
 * Job Target API Service.
 * Encapsulates all job target, intelligence extraction, candidate matching,
 * clarification engine, and evidence-grounded AI tailoring operations.
 */
export const jobsApi = {
  async listJobs(filters?: JobTargetFilters): Promise<JobTargetListResponse> {
    const params: Record<string, string | number> = {};
    if (filters?.status) params.status = filters.status;
    if (filters?.search) params.search = filters.search;
    if (filters?.limit !== undefined) params.limit = filters.limit;
    if (filters?.offset !== undefined) params.offset = filters.offset;

    const response = await apiClient.get<JobTargetListResponse>("/jobs", { params });
    return response.data;
  },

  async getJob(id: string): Promise<JobTarget> {
    const response = await apiClient.get<JobTarget>(`/jobs/${id}`);
    return response.data;
  },

  async createJob(payload: JobTargetCreate): Promise<JobTarget> {
    const response = await apiClient.post<JobTarget>("/jobs", payload);
    return response.data;
  },

  async updateJob(id: string, payload: JobTargetUpdate): Promise<JobTarget> {
    const response = await apiClient.patch<JobTarget>(`/jobs/${id}`, payload);
    return response.data;
  },

  async deleteJob(id: string): Promise<void> {
    await apiClient.delete(`/jobs/${id}`);
  },

  async analyzeJob(id: string): Promise<JobAnalysisResponse> {
    const response = await apiClient.post<JobAnalysisResponse>(`/jobs/${id}/analyze`);
    return response.data;
  },

  async getJobAnalysis(id: string): Promise<JobAnalysisResponse> {
    const response = await apiClient.get<JobAnalysisResponse>(`/jobs/${id}/analysis`);
    return response.data;
  },

  async extractRequirements(payload: {
    job_description: string;
    title?: string;
    company_name?: string;
  }): Promise<JobExtractionResult> {
    const response = await apiClient.post<JobExtractionResult>("/jobs/extract", payload);
    return response.data;
  },

  async getJobCvVersions(id: string, limit = 50, offset = 0): Promise<CVVersionListResponse> {
    const response = await apiClient.get<CVVersionListResponse>(`/jobs/${id}/versions`, {
      params: { limit, offset },
    });
    return response.data;
  },

  // Clarification Engine Operations
  async getClarifications(jobId: string): Promise<ClarificationSessionResponse> {
    const response = await apiClient.get<ClarificationSessionResponse>(`/jobs/${jobId}/clarifications`);
    return response.data;
  },

  async answerClarificationQuestion(
    jobId: string,
    questionId: string,
    payload: ClarificationAnswerRequest
  ): Promise<ClarificationSessionResponse> {
    const response = await apiClient.post<ClarificationSessionResponse>(
      `/jobs/${jobId}/clarifications/${questionId}/answer`,
      payload
    );
    return response.data;
  },

  async skipClarificationQuestion(
    jobId: string,
    questionId: string
  ): Promise<ClarificationSessionResponse> {
    const response = await apiClient.post<ClarificationSessionResponse>(
      `/jobs/${jobId}/clarifications/${questionId}/skip`
    );
    return response.data;
  },

  async promoteClarificationAnswer(
    jobId: string,
    questionId: string,
    payload: ClarificationPromoteRequest
  ): Promise<{ status: string; requirement: string }> {
    const response = await apiClient.post<{ status: string; requirement: string }>(
      `/jobs/${jobId}/clarifications/${questionId}/promote`,
      payload
    );
    return response.data;
  },

  async bulkAnswerClarifications(
    jobId: string,
    payload: ClarificationBulkAnswerRequest
  ): Promise<ClarificationSessionResponse> {
    const response = await apiClient.post<ClarificationSessionResponse>(
      `/jobs/${jobId}/clarifications/bulk`,
      payload
    );
    return response.data;
  },

  // Evidence-Grounded AI CV Tailoring Operations
  async tailorCv(jobId: string, payload?: CVTailorRequest): Promise<CVTailoringResponse> {
    const response = await apiClient.post<CVTailoringResponse>(
      `/jobs/${jobId}/tailor-cv`,
      payload || {}
    );
    return response.data;
  },
};
