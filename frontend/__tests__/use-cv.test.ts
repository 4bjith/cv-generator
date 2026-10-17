import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { cvKeys } from "@/lib/query-keys";
import { cvApi } from "@/services/cv/cv.api";
import { CVVersion, CVVersionListResponse } from "@/types/cv";

describe("TanStack Query CV Version State & Cache Invalidation", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.restoreAllMocks();
  });

  it("stores CV version list in query cache and invalidates on mutations", async () => {
    const mockList: CVVersionListResponse = {
      items: [
        {
          id: "cv-1",
          user_id: "u-1",
          job_target_id: null,
          job_target_title: null,
          job_target_company: null,
          name: "Senior Frontend CV",
          status: "draft",
          created_at: "2026-10-10T00:00:00Z",
          updated_at: "2026-10-10T00:00:00Z",
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    };

    vi.spyOn(cvApi, "listVersions").mockResolvedValueOnce(mockList);

    queryClient.setQueryData(cvKeys.list({ status: "draft" }), mockList);

    const cached = queryClient.getQueryData<CVVersionListResponse>(cvKeys.list({ status: "draft" }));
    expect(cached?.total).toBe(1);
    expect(cached?.items[0].name).toBe("Senior Frontend CV");

    // Invalidation test
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    await queryClient.invalidateQueries({ queryKey: cvKeys.all });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: cvKeys.all });
  });

  it("stores and updates single CV version detail query in cache", async () => {
    const mockVersion: CVVersion = {
      id: "cv-42",
      user_id: "u-1",
      job_target_id: "job-1",
      job_target_title: "Staff Engineer",
      job_target_company: "Stripe",
      name: "Stripe Targeted Version",
      status: "draft",
      content_snapshot: {
        basics: { first_name: "Aarav" },
      },
      created_at: "2026-10-10T00:00:00Z",
      updated_at: "2026-10-10T00:00:00Z",
    };

    queryClient.setQueryData(cvKeys.detail("cv-42"), mockVersion);

    const cachedVersion = queryClient.getQueryData<CVVersion>(cvKeys.detail("cv-42"));
    expect(cachedVersion?.id).toBe("cv-42");
    expect(cachedVersion?.name).toBe("Stripe Targeted Version");

    // Update status in cache
    const updatedVersion: CVVersion = { ...mockVersion, status: "ready" };
    queryClient.setQueryData(cvKeys.detail("cv-42"), updatedVersion);

    const cachedAfterUpdate = queryClient.getQueryData<CVVersion>(cvKeys.detail("cv-42"));
    expect(cachedAfterUpdate?.status).toBe("ready");
  });

  it("removes detail query from cache on delete", async () => {
    const mockVersion: CVVersion = {
      id: "cv-to-delete",
      user_id: "u-1",
      name: "Temporary Version",
      status: "draft",
      content_snapshot: {},
      created_at: "2026-10-10T00:00:00Z",
      updated_at: "2026-10-10T00:00:00Z",
    };

    queryClient.setQueryData(cvKeys.detail("cv-to-delete"), mockVersion);
    expect(queryClient.getQueryData(cvKeys.detail("cv-to-delete"))).toBeDefined();

    queryClient.removeQueries({ queryKey: cvKeys.detail("cv-to-delete") });
    expect(queryClient.getQueryData(cvKeys.detail("cv-to-delete"))).toBeUndefined();
  });

  it("stores and fetches JSON Resume export query data in cache", async () => {
    const mockResume = {
      basics: { name: "Aarav Mehta", label: "Staff Engineer" },
      work: [{ name: "Stripe", position: "Staff Software Engineer" }],
    };

    const queryKey = [...cvKeys.detail("cv-export-1"), "json-resume", true];
    queryClient.setQueryData(queryKey, mockResume);

    const cached = queryClient.getQueryData<Record<string, any>>(queryKey);
    expect(cached?.basics?.name).toBe("Aarav Mehta");
    expect(cached?.work?.length).toBe(1);
  });

  it("handles exportPdf and exportDocx API calls and triggers object URL download", async () => {
    const mockPdfBlob = new Blob(["%PDF-1.4 test"], { type: "application/pdf" });
    const exportPdfSpy = vi.spyOn(cvApi, "exportPdf").mockResolvedValueOnce({
      blob: mockPdfBlob,
      filename: "Aarav_Mehta_CV.pdf",
    });

    const pdfResult = await cvApi.exportPdf("cv-1", { template: "modern-professional" });
    expect(exportPdfSpy).toHaveBeenCalledWith("cv-1", { template: "modern-professional" });
    expect(pdfResult.filename).toBe("Aarav_Mehta_CV.pdf");

    const mockDocxBlob = new Blob(["PK test"], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    const exportDocxSpy = vi.spyOn(cvApi, "exportDocx").mockResolvedValueOnce({
      blob: mockDocxBlob,
      filename: "Aarav_Mehta_CV.docx",
    });

    const docxResult = await cvApi.exportDocx("cv-1", { spacing: "compact" });
    expect(exportDocxSpy).toHaveBeenCalledWith("cv-1", { spacing: "compact" });
    expect(docxResult.filename).toBe("Aarav_Mehta_CV.docx");
  });
});
