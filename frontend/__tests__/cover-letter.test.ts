import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { coverLetterApi } from "@/services/cover-letter/cover-letter.api";
import {
  CoverLetterListResponse,
  CoverLetterResponse,
  GenerateCoverLetterRequest,
  RegenerateCoverLetterRequest,
  UpdateCoverLetterRequest,
} from "@/types/cover-letter";

describe("Cover Letter API Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockLetterResponse: CoverLetterResponse = {
    id: "cl-123",
    user_id: "user-abc",
    job_target_id: "job-xyz",
    job_target_title: "Senior Backend Engineer",
    job_target_company: "Acme Corp",
    cv_version_id: "cv-456",
    cv_version_name: "Tailored CV v1",
    name: "Acme Corp Senior Backend Cover Letter",
    status: "draft",
    tone: "professional",
    length_option: "standard",
    recipient_name: "Hiring Team",
    recipient_title: "Engineering Manager",
    recipient_company: "Acme Corp",
    recipient_address: "100 Market St, SF",
    salutation: "Dear Hiring Team,",
    opening: "I am excited to apply for the Senior Backend Engineer role at Acme Corp.",
    body_paragraphs: [
      "At TechCorp, I led the migration of legacy monolith services to event-driven microservices, improving throughput by 42%.",
      "I also mentored 6 junior engineers and standardized our CI/CD pipelines.",
    ],
    closing: "I look forward to discussing how my experience can benefit Acme Corp.",
    sign_off: "Sincerely,",
    sender_name: "Alex Candidate",
    sender_contact: "alex@example.com | (555) 123-4567",
    full_content: "Alex Candidate\n...\nSincerely,\nAlex Candidate",
    word_count: 320,
    factual_claims: [
      {
        claim_text: "Migrated monolith to microservices improving throughput by 42%",
        entity_type: "work_experience",
        entity_id: "work-1",
        verification_status: "verified",
      },
    ],
    unresolved_gaps: [
      "No candidate evidence found for Kubernetes multi-cluster federation.",
    ],
    change_summary: null,
    generation_parameters: {
      tone: "professional",
      length_option: "standard",
    },
    created_at: "2026-10-18T10:00:00Z",
    updated_at: "2026-10-18T10:00:00Z",
  };

  it("calls POST /cover-letters/generate with grounded parameters and returns response", async () => {
    const postSpy = vi
      .spyOn(apiClient, "post")
      .mockResolvedValueOnce({ data: mockLetterResponse });

    const request: GenerateCoverLetterRequest = {
      job_id: "job-xyz",
      cv_version_id: "cv-456",
      tone: "professional",
      length_option: "standard",
      additional_instructions: "Emphasize microservices and mentoring",
      recipient_name: "Hiring Team",
      recipient_company: "Acme Corp",
    };

    const result = await coverLetterApi.generateCoverLetter(request);

    expect(postSpy).toHaveBeenCalledWith("/cover-letters/generate", request);
    expect(result.id).toBe("cl-123");
    expect(result.factual_claims.length).toBe(1);
    expect(result.unresolved_gaps.length).toBe(1);
    expect(result.unresolved_gaps[0]).toContain("Kubernetes");
  });

  it("calls GET /cover-letters with status, search, and job_id filters", async () => {
    const mockList: CoverLetterListResponse = {
      items: [
        {
          id: "cl-123",
          name: "Acme Corp Senior Backend Cover Letter",
          status: "draft",
          tone: "professional",
          length_option: "standard",
          job_target_id: "job-xyz",
          job_target_title: "Senior Backend Engineer",
          job_target_company: "Acme Corp",
          cv_version_id: "cv-456",
          cv_version_name: "Tailored CV v1",
          word_count: 320,
          created_at: "2026-10-18T10:00:00Z",
          updated_at: "2026-10-18T10:00:00Z",
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    };

    const getSpy = vi
      .spyOn(apiClient, "get")
      .mockResolvedValueOnce({ data: mockList });

    const result = await coverLetterApi.listCoverLetters({
      status: "draft",
      search: "Acme",
      job_id: "job-xyz",
      limit: 20,
      offset: 0,
    });

    expect(getSpy).toHaveBeenCalledWith("/cover-letters", {
      params: {
        status: "draft",
        search: "Acme",
        job_id: "job-xyz",
        limit: 20,
        offset: 0,
      },
    });
    expect(result.total).toBe(1);
    expect(result.items[0].job_target_company).toBe("Acme Corp");
  });

  it("calls GET /cover-letters/:id to retrieve single letter", async () => {
    const getSpy = vi
      .spyOn(apiClient, "get")
      .mockResolvedValueOnce({ data: mockLetterResponse });

    const result = await coverLetterApi.getCoverLetter("cl-123");

    expect(getSpy).toHaveBeenCalledWith("/cover-letters/cl-123");
    expect(result.name).toBe("Acme Corp Senior Backend Cover Letter");
  });

  it("calls PUT /cover-letters/:id to update letter content and status", async () => {
    const updatedResponse = {
      ...mockLetterResponse,
      status: "ready" as const,
      name: "Final Acme Cover Letter",
    };

    const putSpy = vi
      .spyOn(apiClient, "put")
      .mockResolvedValueOnce({ data: updatedResponse });

    const updatePayload: UpdateCoverLetterRequest = {
      name: "Final Acme Cover Letter",
      status: "ready",
      opening: "Updated opening line...",
    };

    const result = await coverLetterApi.updateCoverLetter("cl-123", updatePayload);

    expect(putSpy).toHaveBeenCalledWith("/cover-letters/cl-123", updatePayload);
    expect(result.status).toBe("ready");
    expect(result.name).toBe("Final Acme Cover Letter");
  });

  it("calls POST /cover-letters/:id/regenerate with version preservation option", async () => {
    const regeneratedResponse = {
      ...mockLetterResponse,
      id: "cl-124",
      name: "Acme Corp Cover Letter (v2)",
      change_summary: "Re-crafted opening and strengthened cloud architecture narrative.",
    };

    const postSpy = vi
      .spyOn(apiClient, "post")
      .mockResolvedValueOnce({ data: regeneratedResponse });

    const regeneratePayload: RegenerateCoverLetterRequest = {
      tone: "technical",
      length_option: "detailed",
      preserve_as_new_version: true,
      new_name: "Acme Corp Cover Letter (v2)",
    };

    const result = await coverLetterApi.regenerateCoverLetter("cl-123", regeneratePayload);

    expect(postSpy).toHaveBeenCalledWith("/cover-letters/cl-123/regenerate", regeneratePayload);
    expect(result.id).toBe("cl-124");
    expect(result.change_summary).toContain("cloud architecture");
  });

  it("calls POST /cover-letters/:id/duplicate to clone a draft", async () => {
    const clonedResponse = {
      ...mockLetterResponse,
      id: "cl-125",
      name: "Acme Corp Senior Backend Cover Letter (Copy)",
    };

    const postSpy = vi
      .spyOn(apiClient, "post")
      .mockResolvedValueOnce({ data: clonedResponse });

    const result = await coverLetterApi.duplicateCoverLetter("cl-123", {
      new_name: "Acme Corp Senior Backend Cover Letter (Copy)",
    });

    expect(postSpy).toHaveBeenCalledWith("/cover-letters/cl-123/duplicate", {
      new_name: "Acme Corp Senior Backend Cover Letter (Copy)",
    });
    expect(result.id).toBe("cl-125");
  });

  it("calls DELETE /cover-letters/:id to permanently delete a letter", async () => {
    const deleteSpy = vi
      .spyOn(apiClient, "delete")
      .mockResolvedValueOnce({ data: { message: "Deleted" } });

    await coverLetterApi.deleteCoverLetter("cl-123");

    expect(deleteSpy).toHaveBeenCalledWith("/cover-letters/cl-123");
  });

  it("calls GET /cover-letters/:id/export/pdf and extracts filename from header", async () => {
    const mockBlob = new Blob(["%PDF-1.4 mock content"], { type: "application/pdf" });

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: mockBlob,
      headers: {
        "content-disposition": 'attachment; filename="Alex_Candidate_Cover_Letter.pdf"',
      },
    });

    const result = await coverLetterApi.exportPdf("cl-123");

    expect(getSpy).toHaveBeenCalledWith("/cover-letters/cl-123/export/pdf", {
      responseType: "blob",
    });
    expect(result.filename).toBe("Alex_Candidate_Cover_Letter.pdf");
    expect(result.blob).toBe(mockBlob);
  });

  it("calls GET /cover-letters/:id/export/docx and extracts filename from header", async () => {
    const mockBlob = new Blob(["mock docx binary"], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: mockBlob,
      headers: {
        "content-disposition": 'attachment; filename="Alex_Candidate_Cover_Letter.docx"',
      },
    });

    const result = await coverLetterApi.exportDocx("cl-123");

    expect(getSpy).toHaveBeenCalledWith("/cover-letters/cl-123/export/docx", {
      responseType: "blob",
    });
    expect(result.filename).toBe("Alex_Candidate_Cover_Letter.docx");
    expect(result.blob).toBe(mockBlob);
  });
});
