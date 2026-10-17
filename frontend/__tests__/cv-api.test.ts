import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { cvApi } from "@/services/cv/cv.api";
import {
  CVVersion,
  CVVersionCreate,
  CVVersionDuplicate,
  CVVersionListResponse,
  CVVersionUpdate,
} from "@/types/cv";

describe("CV Versions API Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("calls GET /cv/versions with pagination, search, and status filters", async () => {
    const mockResponse: CVVersionListResponse = {
      items: [
        {
          id: "cv-1",
          user_id: "user-1",
          job_target_id: "job-1",
          job_target_title: "Staff Engineer",
          job_target_company: "Stripe",
          name: "Stripe Targeted CV",
          status: "draft",
          created_at: "2026-10-10T10:00:00Z",
          updated_at: "2026-10-10T10:00:00Z",
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockResponse });

    const result = await cvApi.listVersions({
      status: "draft",
      job_target_id: "job-1",
      search: "Stripe",
      limit: 20,
      offset: 0,
    });

    expect(getSpy).toHaveBeenCalledWith("/cv/versions", {
      params: {
        status: "draft",
        job_target_id: "job-1",
        search: "Stripe",
        limit: 20,
        offset: 0,
      },
    });
    expect(result.total).toBe(1);
    expect(result.items[0].name).toBe("Stripe Targeted CV");
  });

  it("calls GET /cv/versions/:id and returns full CV version with snapshot", async () => {
    const mockVersion: CVVersion = {
      id: "cv-100",
      user_id: "user-1",
      job_target_id: null,
      job_target_title: null,
      job_target_company: null,
      name: "General Master Snapshot",
      status: "ready",
      content_snapshot: {
        basics: {
          first_name: "Aarav",
          last_name: "Mehta",
          professional_headline: "Staff Engineer",
        },
        experiences: [],
        skills: [],
      },
      created_at: "2026-10-10T11:00:00Z",
      updated_at: "2026-10-10T11:00:00Z",
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockVersion });

    const result = await cvApi.getVersion("cv-100");

    expect(getSpy).toHaveBeenCalledWith("/cv/versions/cv-100");
    expect(result.name).toBe("General Master Snapshot");
    expect(result.content_snapshot.basics?.first_name).toBe("Aarav");
  });

  it("calls POST /cv/versions with creation payload", async () => {
    const payload: CVVersionCreate = {
      name: "Vercel Platform CV",
      job_target_id: "job-99",
    };

    const mockCreated: CVVersion = {
      id: "cv-999",
      user_id: "user-1",
      job_target_id: "job-99",
      name: payload.name,
      status: "draft",
      content_snapshot: {
        basics: { first_name: "Aarav" },
      },
      created_at: "2026-10-10T12:00:00Z",
      updated_at: "2026-10-10T12:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockCreated });

    const result = await cvApi.createVersion(payload);

    expect(postSpy).toHaveBeenCalledWith("/cv/versions", payload);
    expect(result.id).toBe("cv-999");
    expect(result.name).toBe("Vercel Platform CV");
  });

  it("calls PATCH /cv/versions/:id with update payload", async () => {
    const updatePayload: CVVersionUpdate = {
      name: "Updated Name V2",
      status: "ready",
    };

    const mockUpdated: CVVersion = {
      id: "cv-100",
      user_id: "user-1",
      name: "Updated Name V2",
      status: "ready",
      content_snapshot: {},
      created_at: "2026-10-10T11:00:00Z",
      updated_at: "2026-10-10T12:30:00Z",
    };

    const patchSpy = vi.spyOn(apiClient, "patch").mockResolvedValueOnce({ data: mockUpdated });

    const result = await cvApi.updateVersion("cv-100", updatePayload);

    expect(patchSpy).toHaveBeenCalledWith("/cv/versions/cv-100", updatePayload);
    expect(result.name).toBe("Updated Name V2");
    expect(result.status).toBe("ready");
  });

  it("calls POST /cv/versions/:id/duplicate to clone a version", async () => {
    const dupPayload: CVVersionDuplicate = { name: "Custom Clone Name" };
    const mockCloned: CVVersion = {
      id: "cv-clone-2",
      user_id: "user-1",
      name: "Custom Clone Name",
      status: "draft",
      content_snapshot: {},
      created_at: "2026-10-10T13:00:00Z",
      updated_at: "2026-10-10T13:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockCloned });

    const result = await cvApi.duplicateVersion("cv-100", dupPayload);

    expect(postSpy).toHaveBeenCalledWith("/cv/versions/cv-100/duplicate", dupPayload);
    expect(result.id).toBe("cv-clone-2");
    expect(result.name).toBe("Custom Clone Name");
  });

  it("calls POST /cv/versions/:id/archive and restore", async () => {
    const mockArchived: CVVersion = {
      id: "cv-100",
      user_id: "user-1",
      name: "Version",
      status: "archived",
      content_snapshot: {},
      created_at: "2026-10-10T11:00:00Z",
      updated_at: "2026-10-10T13:00:00Z",
    };
    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockArchived });

    const archResult = await cvApi.archiveVersion("cv-100");
    expect(postSpy).toHaveBeenCalledWith("/cv/versions/cv-100/archive");
    expect(archResult.status).toBe("archived");

    const mockRestored: CVVersion = { ...mockArchived, status: "draft" };
    postSpy.mockResolvedValueOnce({ data: mockRestored });

    const restResult = await cvApi.restoreVersion("cv-100");
    expect(postSpy).toHaveBeenCalledWith("/cv/versions/cv-100/restore");
    expect(restResult.status).toBe("draft");
  });

  it("calls DELETE /cv/versions/:id", async () => {
    const deleteSpy = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({ data: null });

    await cvApi.deleteVersion("cv-100");

    expect(deleteSpy).toHaveBeenCalledWith("/cv/versions/cv-100");
  });

  it("calls GET /cv/versions/:id/json-resume with apply_visibility parameter", async () => {
    const mockJsonResume = {
      basics: {
        name: "Aarav Mehta",
        label: "Staff Engineer",
      },
      work: [
        {
          name: "Stripe",
          position: "Staff Software Engineer",
        },
      ],
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockJsonResume });

    const result = await cvApi.exportJsonResume("cv-100", true);

    expect(getSpy).toHaveBeenCalledWith("/cv/versions/cv-100/json-resume", {
      params: { apply_visibility: true },
    });
    expect(result.basics.name).toBe("Aarav Mehta");

    // Test with apply_visibility = false
    getSpy.mockResolvedValueOnce({ data: mockJsonResume });
    await cvApi.exportJsonResume("cv-100", false);
    expect(getSpy).toHaveBeenCalledWith("/cv/versions/cv-100/json-resume", {
      params: { apply_visibility: false },
    });
  });

  it("calls GET /cv/versions/:id/export/pdf and extracts filename and blob", async () => {
    const mockBlob = new Blob(["%PDF-1.4 test"], { type: "application/pdf" });
    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: mockBlob,
      headers: {
        "content-disposition": 'attachment; filename="Aarav_Mehta_CV.pdf"',
      },
    });

    const result = await cvApi.exportPdf("cv-100", { template: "modern-professional" });

    expect(getSpy).toHaveBeenCalledWith("/cv/versions/cv-100/export/pdf", {
      params: { template: "modern-professional" },
      responseType: "blob",
    });
    expect(result.filename).toBe("Aarav_Mehta_CV.pdf");
    expect(result.blob).toBe(mockBlob);
  });

  it("calls GET /cv/versions/:id/export/docx and extracts filename and blob", async () => {
    const mockBlob = new Blob(["PK test"], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: mockBlob,
      headers: {
        "content-disposition": 'attachment; filename="Aarav_Mehta_CV.docx"',
      },
    });

    const result = await cvApi.exportDocx("cv-100", { spacing: "compact" });

    expect(getSpy).toHaveBeenCalledWith("/cv/versions/cv-100/export/docx", {
      params: { spacing: "compact" },
      responseType: "blob",
    });
    expect(result.filename).toBe("Aarav_Mehta_CV.docx");
    expect(result.blob).toBe(mockBlob);
  });
});
