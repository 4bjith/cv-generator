import { apiClient } from "@/lib/api/axios";
import {
  ApplyATSSuggestionsRequest,
  ApplyATSSuggestionsResponse,
  ATSAnalysisRequest,
  ATSAnalysisResponse,
} from "@/types/ats";

/**
 * ATS Analysis & Keyword Optimization API Service.
 * Evaluates CV versions against applicant tracking systems and target jobs,
 * audits keyword frequency and formatting risks, and applies grounded optimizations.
 */
export const atsApi = {
  async analyzeCvAts(payload: ATSAnalysisRequest): Promise<ATSAnalysisResponse> {
    const response = await apiClient.post<ATSAnalysisResponse>("/ats/analyze", payload);
    return response.data;
  },

  async getCvAtsAnalysis(versionId: string, jobId?: string): Promise<ATSAnalysisResponse> {
    const params: Record<string, string> = {};
    if (jobId) params.job_id = jobId;

    const response = await apiClient.get<ATSAnalysisResponse>(`/ats/cv/${versionId}`, {
      params,
    });
    return response.data;
  },

  async applyAtsSuggestions(
    payload: ApplyATSSuggestionsRequest
  ): Promise<ApplyATSSuggestionsResponse> {
    const response = await apiClient.post<ApplyATSSuggestionsResponse>(
      "/ats/apply-suggestions",
      payload
    );
    return response.data;
  },
};
