import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { jobsApi } from "@/services/jobs/jobs.api";
import {
  JobTarget,
  JobTargetCreate,
  JobTargetListResponse,
  JobTargetUpdate,
} from "@/types/job";

describe("Job Targets API Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("calls GET /jobs with correct pagination and search filters", async () => {
    const mockResponse: JobTargetListResponse = {
      items: [
        {
          id: "job-1",
          user_id: "user-1",
          title: "Senior Frontend Engineer",
          company_name: "Lattice Systems",
          location: "San Francisco, CA",
          job_description: "Core frontend architecture and design systems",
          source_url: "https://lattice.com/careers/senior-frontend",
          user_notes: "Referral from John",
          status: "saved",
          created_at: "2026-10-10T10:00:00Z",
          updated_at: "2026-10-10T10:00:00Z",
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockResponse });

    const result = await jobsApi.listJobs({
      status: "saved",
      search: "Lattice",
      limit: 20,
      offset: 0,
    });

    expect(getSpy).toHaveBeenCalledWith("/jobs", {
      params: {
        status: "saved",
        search: "Lattice",
        limit: 20,
        offset: 0,
      },
    });
    expect(result.total).toBe(1);
    expect(result.items[0].company_name).toBe("Lattice Systems");
  });

  it("calls GET /jobs/:id and returns a single job target", async () => {
    const mockJob: JobTarget = {
      id: "job-123",
      user_id: "user-1",
      title: "Staff Product Engineer",
      company_name: "Stripe",
      location: "Seattle, WA",
      job_description: "Billing and dashboard experience",
      source_url: null,
      user_notes: null,
      status: "saved",
      created_at: "2026-10-10T11:00:00Z",
      updated_at: "2026-10-10T11:00:00Z",
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockJob });

    const result = await jobsApi.getJob("job-123");

    expect(getSpy).toHaveBeenCalledWith("/jobs/job-123");
    expect(result.title).toBe("Staff Product Engineer");
    expect(result.company_name).toBe("Stripe");
  });

  it("calls POST /jobs with creation payload", async () => {
    const payload: JobTargetCreate = {
      title: "AI Engineer",
      company_name: "Anthropic",
      location: "Remote",
      job_description: "Building next-generation agent workflows",
      source_url: "https://anthropic.com/careers/ai-eng",
      user_notes: "High priority application",
      status: "saved",
    };

    const mockCreated: JobTarget = {
      id: "job-999",
      user_id: "user-1",
      title: payload.title,
      company_name: payload.company_name,
      location: payload.location,
      job_description: payload.job_description,
      source_url: payload.source_url,
      user_notes: payload.user_notes,
      status: "saved",
      created_at: "2026-10-10T12:00:00Z",
      updated_at: "2026-10-10T12:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockCreated });

    const result = await jobsApi.createJob(payload);

    expect(postSpy).toHaveBeenCalledWith("/jobs", payload);
    expect(result.id).toBe("job-999");
    expect(result.title).toBe("AI Engineer");
  });

  it("calls PATCH /jobs/:id with update payload", async () => {
    const updatePayload: JobTargetUpdate = {
      status: "archived",
      user_notes: "Offer accepted elsewhere",
    };

    const mockUpdated: JobTarget = {
      id: "job-123",
      user_id: "user-1",
      title: "Staff Product Engineer",
      company_name: "Stripe",
      location: "Seattle, WA",
      job_description: "Billing and dashboard experience",
      source_url: null,
      user_notes: "Offer accepted elsewhere",
      status: "archived",
      created_at: "2026-10-10T11:00:00Z",
      updated_at: "2026-10-10T12:30:00Z",
    };

    const patchSpy = vi.spyOn(apiClient, "patch").mockResolvedValueOnce({ data: mockUpdated });

    const result = await jobsApi.updateJob("job-123", updatePayload);

    expect(patchSpy).toHaveBeenCalledWith("/jobs/job-123", updatePayload);
    expect(result.status).toBe("archived");
    expect(result.user_notes).toBe("Offer accepted elsewhere");
  });

  it("calls DELETE /jobs/:id", async () => {
    const deleteSpy = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({ data: null });

    await jobsApi.deleteJob("job-123");

    expect(deleteSpy).toHaveBeenCalledWith("/jobs/job-123");
  });

  it("calls POST /jobs/:id/analyze and returns analysis response", async () => {
    const mockAnalysisResponse = {
      job_id: "job-123",
      job_title: "Staff Product Engineer",
      company_name: "Stripe",
      analysis: {
        job_id: "job-123",
        extracted_at: "2026-10-17T12:00:00Z",
        role_overview: "Lead billing product engineering",
        requirements: [
          {
            id: "req-1",
            category: "skills",
            requirement: "Proficiency in Python and TypeScript",
            is_mandatory: true,
            candidate_match_status: "supported" as const,
            reasoning: "Verified by candidate profile skill Python",
            evidence_ids: ["ev-1"],
            evidence_items: [
              {
                id: "ev-1",
                title: "GitHub Repository",
                source: "GitHub",
                source_type: "link",
                url: "https://github.com/candidate/repo",
                verification_status: "verified",
              },
            ],
            confidence_score: 0.95,
          },
        ],
        keyword_summary: {
          total_requirements: 1,
          mandatory_count: 1,
          preferred_count: 0,
          supported_count: 1,
          partial_count: 0,
          unverified_count: 0,
          missing_count: 0,
          coverage_percentage: 100,
          mandatory_coverage_percentage: 100,
          top_matched_keywords: ["Python"],
          top_missing_keywords: [],
          identified_gaps: [],
        },
      },
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockAnalysisResponse });

    const result = await jobsApi.analyzeJob("job-123");

    expect(postSpy).toHaveBeenCalledWith("/jobs/job-123/analyze");
    expect(result.job_id).toBe("job-123");
    expect(result.analysis.keyword_summary.coverage_percentage).toBe(100);
    expect(result.analysis.requirements[0].candidate_match_status).toBe("supported");
  });

  it("calls GET /jobs/:id/analysis to retrieve cached analysis", async () => {
    const mockAnalysisResponse = {
      job_id: "job-123",
      job_title: "Staff Product Engineer",
      company_name: "Stripe",
      analysis: {
        job_id: "job-123",
        extracted_at: "2026-10-17T12:00:00Z",
        requirements: [],
        keyword_summary: {
          total_requirements: 0,
          mandatory_count: 0,
          preferred_count: 0,
          supported_count: 0,
          partial_count: 0,
          unverified_count: 0,
          missing_count: 0,
          coverage_percentage: 0,
          mandatory_coverage_percentage: 100,
          top_matched_keywords: [],
          top_missing_keywords: [],
          identified_gaps: [],
        },
      },
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockAnalysisResponse });

    const result = await jobsApi.getJobAnalysis("job-123");

    expect(getSpy).toHaveBeenCalledWith("/jobs/job-123/analysis");
    expect(result.job_id).toBe("job-123");
  });

  it("calls POST /jobs/extract for ad-hoc requirement extraction", async () => {
    const mockExtraction = {
      role_overview: "Senior backend developer",
      seniority_level: "Senior",
      employment_type: "Full-time",
      requirements: [],
      extracted_keywords: ["Python", "FastAPI"],
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockExtraction });

    const result = await jobsApi.extractRequirements({
      job_description: "We need a senior backend engineer with Python experience.",
      title: "Senior Backend Developer",
    });

    expect(postSpy).toHaveBeenCalledWith("/jobs/extract", {
      job_description: "We need a senior backend engineer with Python experience.",
      title: "Senior Backend Developer",
    });
    expect(result.seniority_level).toBe("Senior");
    expect(result.extracted_keywords).toContain("Python");
  });

  it("calls GET /jobs/:id/versions to list associated CV versions", async () => {
    const mockVersions = {
      items: [
        {
          id: "cv-1",
          user_id: "user-1",
          job_target_id: "job-123",
          name: "Stripe Staff Application",
          status: "draft",
          created_at: "2026-10-17T12:00:00Z",
          updated_at: "2026-10-17T12:00:00Z",
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockVersions });

    const result = await jobsApi.getJobCvVersions("job-123");

    expect(getSpy).toHaveBeenCalledWith("/jobs/job-123/versions", {
      params: { limit: 50, offset: 0 },
    });
    expect(result.total).toBe(1);
    expect(result.items[0].job_target_id).toBe("job-123");
  });
});
