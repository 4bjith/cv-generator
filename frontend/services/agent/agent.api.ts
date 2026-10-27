import { apiClient } from "@/lib/api/axios";
import {
  AgentDailyReport,
  AgentRunResult,
  ApplicationRecord,
  DiscoveredJob,
  JobSearchProfile,
  QAMemoryBankItem,
  RecruiterOutreach,
} from "@/types/agent";

export const agentApi = {
  async getProfile(): Promise<JobSearchProfile> {
    const response = await apiClient.get<JobSearchProfile>("/agent/profile");
    return response.data;
  },

  async updateProfile(payload: Partial<JobSearchProfile>): Promise<JobSearchProfile> {
    const response = await apiClient.put<JobSearchProfile>("/agent/profile", payload);
    return response.data;
  },

  async emergencyStop(): Promise<JobSearchProfile> {
    const response = await apiClient.post<JobSearchProfile>("/agent/emergency-stop");
    return response.data;
  },

  async resume(): Promise<JobSearchProfile> {
    const response = await apiClient.post<JobSearchProfile>("/agent/resume");
    return response.data;
  },

  async runNow(maxApplications: number = 3): Promise<AgentRunResult> {
    const response = await apiClient.post<AgentRunResult>("/agent/run-now", null, {
      params: { max_applications: maxApplications },
    });
    return response.data;
  },

  async listJobs(status?: string, eligibility?: string): Promise<DiscoveredJob[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (eligibility) params.eligibility = eligibility;
    const response = await apiClient.get<DiscoveredJob[]>("/agent/jobs", { params });
    return response.data;
  },

  async applyToJob(jobId: string): Promise<ApplicationRecord> {
    const response = await apiClient.post<ApplicationRecord>(`/agent/jobs/${jobId}/apply`);
    return response.data;
  },

  async listApplications(status?: string): Promise<ApplicationRecord[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    const response = await apiClient.get<ApplicationRecord[]>("/agent/applications", { params });
    return response.data;
  },

  async listOutreach(status?: string): Promise<RecruiterOutreach[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    const response = await apiClient.get<RecruiterOutreach[]>("/agent/outreach", { params });
    return response.data;
  },

  async updateOutreach(id: string, payload: { status?: string; reply_notes?: string }): Promise<RecruiterOutreach> {
    const response = await apiClient.patch<RecruiterOutreach>(`/agent/outreach/${id}`, payload);
    return response.data;
  },

  async listQABank(category?: string): Promise<QAMemoryBankItem[]> {
    const params: Record<string, string> = {};
    if (category) params.category = category;
    const response = await apiClient.get<QAMemoryBankItem[]>("/agent/qa-bank", { params });
    return response.data;
  },

  async createQAItem(payload: { category: string; question_pattern: string; answer_value: string }): Promise<QAMemoryBankItem> {
    const response = await apiClient.post<QAMemoryBankItem>("/agent/qa-bank", payload);
    return response.data;
  },

  async deleteQAItem(id: string): Promise<void> {
    await apiClient.delete(`/agent/qa-bank/${id}`);
  },

  async getLatestReport(): Promise<AgentDailyReport | null> {
    const response = await apiClient.get<AgentDailyReport | null>("/agent/reports/latest");
    return response.data;
  },

  async listReports(): Promise<AgentDailyReport[]> {
    const response = await apiClient.get<AgentDailyReport[]>("/agent/reports");
    return response.data;
  },
};
