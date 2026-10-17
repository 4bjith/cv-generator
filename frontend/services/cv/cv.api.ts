import { apiClient } from "@/lib/api/axios";
import {
  CVVersion,
  CVVersionCreate,
  CVVersionDuplicate,
  CVVersionFilters,
  CVVersionListResponse,
  CVVersionUpdate,
} from "@/types/cv";

/**
 * CV Version Management API Client.
 * Handles lifecycle operations, point-in-time snapshotting, and metadata updates.
 */
export const cvApi = {
  async listVersions(filters?: CVVersionFilters): Promise<CVVersionListResponse> {
    const params: Record<string, string | number> = {};
    if (filters?.status) params.status = filters.status;
    if (filters?.job_target_id) params.job_target_id = filters.job_target_id;
    if (filters?.search) params.search = filters.search;
    if (filters?.limit !== undefined) params.limit = filters.limit;
    if (filters?.offset !== undefined) params.offset = filters.offset;

    const response = await apiClient.get<CVVersionListResponse>("/cv/versions", { params });
    return response.data;
  },

  async getVersion(id: string): Promise<CVVersion> {
    const response = await apiClient.get<CVVersion>(`/cv/versions/${id}`);
    return response.data;
  },

  async createVersion(payload: CVVersionCreate): Promise<CVVersion> {
    const response = await apiClient.post<CVVersion>("/cv/versions", payload);
    return response.data;
  },

  async updateVersion(id: string, payload: CVVersionUpdate): Promise<CVVersion> {
    const response = await apiClient.patch<CVVersion>(`/cv/versions/${id}`, payload);
    return response.data;
  },

  async duplicateVersion(id: string, payload?: CVVersionDuplicate): Promise<CVVersion> {
    const response = await apiClient.post<CVVersion>(`/cv/versions/${id}/duplicate`, payload || {});
    return response.data;
  },

  async archiveVersion(id: string): Promise<CVVersion> {
    const response = await apiClient.post<CVVersion>(`/cv/versions/${id}/archive`);
    return response.data;
  },

  async restoreVersion(id: string): Promise<CVVersion> {
    const response = await apiClient.post<CVVersion>(`/cv/versions/${id}/restore`);
    return response.data;
  },

  async deleteVersion(id: string): Promise<void> {
    await apiClient.delete(`/cv/versions/${id}`);
  },

  async exportJsonResume(id: string, applyVisibility = false): Promise<Record<string, any>> {
    const response = await apiClient.get<Record<string, any>>(`/cv/versions/${id}/json-resume`, {
      params: { apply_visibility: applyVisibility },
    });
    return response.data;
  },

  async exportPdf(id: string, overrides?: Record<string, string>): Promise<{ blob: Blob; filename: string }> {
    const response = await apiClient.get(`/cv/versions/${id}/export/pdf`, {
      params: overrides,
      responseType: "blob",
    });
    const disposition = (response.headers && response.headers["content-disposition"]) || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : "CV_Document.pdf";
    return { blob: response.data, filename };
  },

  async exportDocx(id: string, overrides?: Record<string, string>): Promise<{ blob: Blob; filename: string }> {
    const response = await apiClient.get(`/cv/versions/${id}/export/docx`, {
      params: overrides,
      responseType: "blob",
    });
    const disposition = (response.headers && response.headers["content-disposition"]) || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : "CV_Document.docx";
    return { blob: response.data, filename };
  },
};
