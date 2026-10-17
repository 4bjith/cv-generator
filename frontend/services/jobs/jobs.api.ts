import { apiClient } from "@/lib/api/axios";
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

/**
 * Job Target API Service.
 * Encapsulates all job target, intelligence extraction, and candidate matching operations.
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
};
