import { apiClient } from "@/lib/api/axios";
import {
  CoverLetterListResponse,
  CoverLetterResponse,
  GenerateCoverLetterRequest,
  RegenerateCoverLetterRequest,
  UpdateCoverLetterRequest,
} from "@/types/cover-letter";

export interface CoverLetterFilters {
  status?: string;
  job_id?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

/**
 * Cover Letter API Service.
 * Handles AI-powered evidence-grounded generation, editing, version preservation,
 * duplication, and multi-format PDF/DOCX exports.
 */
export const coverLetterApi = {
  async generateCoverLetter(
    payload: GenerateCoverLetterRequest
  ): Promise<CoverLetterResponse> {
    const response = await apiClient.post<CoverLetterResponse>(
      "/cover-letters/generate",
      payload
    );
    return response.data;
  },

  async listCoverLetters(
    filters?: CoverLetterFilters
  ): Promise<CoverLetterListResponse> {
    const params: Record<string, string | number> = {};
    if (filters?.status) params.status = filters.status;
    if (filters?.job_id) params.job_id = filters.job_id;
    if (filters?.search) params.search = filters.search;
    if (filters?.limit !== undefined) params.limit = filters.limit;
    if (filters?.offset !== undefined) params.offset = filters.offset;

    const response = await apiClient.get<CoverLetterListResponse>(
      "/cover-letters",
      { params }
    );
    return response.data;
  },

  async getCoverLetter(id: string): Promise<CoverLetterResponse> {
    const response = await apiClient.get<CoverLetterResponse>(
      `/cover-letters/${id}`
    );
    return response.data;
  },

  async updateCoverLetter(
    id: string,
    payload: UpdateCoverLetterRequest
  ): Promise<CoverLetterResponse> {
    const response = await apiClient.put<CoverLetterResponse>(
      `/cover-letters/${id}`,
      payload
    );
    return response.data;
  },

  async regenerateCoverLetter(
    id: string,
    payload: RegenerateCoverLetterRequest
  ): Promise<CoverLetterResponse> {
    const response = await apiClient.post<CoverLetterResponse>(
      `/cover-letters/${id}/regenerate`,
      payload
    );
    return response.data;
  },

  async duplicateCoverLetter(
    id: string,
    payload?: { new_name?: string }
  ): Promise<CoverLetterResponse> {
    const response = await apiClient.post<CoverLetterResponse>(
      `/cover-letters/${id}/duplicate`,
      payload || {}
    );
    return response.data;
  },

  async deleteCoverLetter(id: string): Promise<void> {
    await apiClient.delete(`/cover-letters/${id}`);
  },

  async exportPdf(
    id: string
  ): Promise<{ blob: Blob; filename: string }> {
    const response = await apiClient.get(`/cover-letters/${id}/export/pdf`, {
      responseType: "blob",
    });
    const disposition =
      (response.headers && response.headers["content-disposition"]) || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : "Cover_Letter.pdf";
    return { blob: response.data, filename };
  },

  async exportDocx(
    id: string
  ): Promise<{ blob: Blob; filename: string }> {
    const response = await apiClient.get(`/cover-letters/${id}/export/docx`, {
      responseType: "blob",
    });
    const disposition =
      (response.headers && response.headers["content-disposition"]) || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : "Cover_Letter.docx";
    return { blob: response.data, filename };
  },
};
