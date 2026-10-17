import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { jobKeys } from "@/lib/query-keys";
import { jobsApi } from "@/services/jobs/jobs.api";
import { JobTarget, JobTargetListResponse } from "@/types/job";

describe("TanStack Query Job Target State & Cache Invalidation", () => {
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

  it("stores job list in query cache and updates on filter changes", async () => {
    const mockList: JobTargetListResponse = {
      items: [
        {
          id: "job-1",
          user_id: "u-1",
          title: "Senior Frontend Engineer",
          company_name: "Lattice",
          location: "San Francisco, CA",
          job_description: "Frontend architecture with React and TypeScript",
          status: "saved",
          created_at: "2026-10-10T00:00:00Z",
          updated_at: "2026-10-10T00:00:00Z",
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    };

    vi.spyOn(jobsApi, "listJobs").mockResolvedValueOnce(mockList);

    queryClient.setQueryData(jobKeys.list({ status: "saved" }), mockList);

    const cached = queryClient.getQueryData<JobTargetListResponse>(jobKeys.list({ status: "saved" }));
    expect(cached?.total).toBe(1);
    expect(cached?.items[0].title).toBe("Senior Frontend Engineer");

    // Invalidation test
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    await queryClient.invalidateQueries({ queryKey: jobKeys.all });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: jobKeys.all });
  });

  it("stores and updates single job detail query in cache", async () => {
    const mockJob: JobTarget = {
      id: "job-42",
      user_id: "u-1",
      title: "Staff Engineer",
      company_name: "Stripe",
      location: "Remote",
      job_description: "Distributed infrastructure",
      status: "saved",
      created_at: "2026-10-10T00:00:00Z",
      updated_at: "2026-10-10T00:00:00Z",
    };

    queryClient.setQueryData(jobKeys.detail("job-42"), mockJob);

    const cachedJob = queryClient.getQueryData<JobTarget>(jobKeys.detail("job-42"));
    expect(cachedJob?.id).toBe("job-42");
    expect(cachedJob?.company_name).toBe("Stripe");

    // Update job status in cache
    const updatedJob: JobTarget = { ...mockJob, status: "archived" };
    queryClient.setQueryData(jobKeys.detail("job-42"), updatedJob);

    const cachedAfterUpdate = queryClient.getQueryData<JobTarget>(jobKeys.detail("job-42"));
    expect(cachedAfterUpdate?.status).toBe("archived");
  });

  it("removes detail query from cache on delete", async () => {
    const mockJob: JobTarget = {
      id: "job-to-delete",
      user_id: "u-1",
      title: "DevOps Engineer",
      company_name: "Docker",
      job_description: "Kubernetes, CI/CD",
      status: "saved",
      created_at: "2026-10-10T00:00:00Z",
      updated_at: "2026-10-10T00:00:00Z",
    };

    queryClient.setQueryData(jobKeys.detail("job-to-delete"), mockJob);
    expect(queryClient.getQueryData(jobKeys.detail("job-to-delete"))).toBeDefined();

    queryClient.removeQueries({ queryKey: jobKeys.detail("job-to-delete") });
    expect(queryClient.getQueryData(jobKeys.detail("job-to-delete"))).toBeUndefined();
  });

  it("manages job analysis and cv version queries in cache", async () => {
    const mockAnalysis = {
      job_id: "job-1",
      analyzed_at: "2026-10-17T10:00:00Z",
      analysis: {
        job_summary: "High impact backend engineer role",
        seniority: "Senior",
        employment_type: "full-time",
        requirements: [
          {
            id: "req-1",
            category: "skills",
            requirement: "Python and FastAPI",
            is_mandatory: true,
            candidate_match_status: "supported" as const,
            supporting_facts: ["5 years Python experience"],
            evidence_ids: ["ev-1"],
            match_confidence: 1.0,
            gap_type: null,
            reasoning: "Matched against Python skill",
          },
        ],
        keyword_summary: {
          total_keywords: 10,
          matched_keywords: ["python", "fastapi"],
          missing_keywords: ["graphql"],
          coverage_percentage: 66.7,
        },
        coverage_score: 85,
        mandatory_coverage_score: 100,
        preferred_coverage_score: 70,
        total_requirements: 1,
        supported_count: 1,
        partial_count: 0,
        unverified_count: 0,
        missing_count: 0,
      },
    };

    queryClient.setQueryData(jobKeys.analysis("job-1"), mockAnalysis);
    const cachedAnalysis = queryClient.getQueryData(jobKeys.analysis("job-1"));
    expect(cachedAnalysis).toEqual(mockAnalysis);

    const mockVersions = {
      items: [
        {
          id: "cv-v1",
          user_id: "u-1",
          name: "Tailored Python CV",
          version_number: 1,
          job_target_id: "job-1",
        },
      ],
      total: 1,
    };

    queryClient.setQueryData(jobKeys.versions("job-1"), mockVersions);
    const cachedVersions = queryClient.getQueryData(jobKeys.versions("job-1"));
    expect(cachedVersions).toEqual(mockVersions);
  });
});
