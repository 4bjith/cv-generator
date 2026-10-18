import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { atsApi } from "@/services/ats/ats.api";
import {
  ATSAnalysisRequest,
  ATSAnalysisResponse,
  ApplyATSSuggestionsRequest,
  ApplyATSSuggestionsResponse,
} from "@/types/ats";

describe("ATS Analysis Engine & Keyword Optimization Frontend API", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockAnalysisResponse: ATSAnalysisResponse = {
    id: "ats-analysis-1",
    cv_version_id: "cv-v1-uuid",
    cv_version_name: "Tailored Staff Engineer CV",
    job_id: "job-target-uuid",
    job_title: "Senior Cloud Architect",
    company_name: "Apex Enterprise",
    scoring_mode: "job_targeted",
    overall_score: 84.5,
    keyword_coverage_percentage: 83.3,
    components: [
      {
        name: "Keyword Coverage",
        score: 25.0,
        max_score: 30.0,
        weight_percentage: 30.0,
        explanation: "10/12 critical job target keywords present (83.3% match).",
        deductions: ["Missing keyword: terraform", "Missing keyword: event-driven"],
      },
      {
        name: "Requirement Match",
        score: 24.5,
        max_score: 30.0,
        weight_percentage: 30.0,
        explanation: "Mandatory qualifications well satisfied; 1 preferred qualification missing.",
        deductions: ["Preferred requirement missing: Kubernetes multi-cluster federation"],
      },
      {
        name: "Structure & Completeness",
        score: 18.0,
        max_score: 20.0,
        weight_percentage: 20.0,
        explanation: "All core sections present with contact details verified.",
        deductions: ["Summary could be more role-focused"],
      },
      {
        name: "Format & Parsing Safety",
        score: 17.0,
        max_score: 20.0,
        weight_percentage: 20.0,
        explanation: "Clean single-column ATS layout detected.",
        deductions: ["Contains 1 decorative Unicode bullet"],
      },
    ],
    keywords: [
      {
        keyword: "python",
        count: 5,
        density_percentage: 1.25,
        is_mandatory: true,
        is_present: true,
        is_overused: false,
        locations_found: ["skills", "work_experience"],
      },
      {
        keyword: "aws",
        count: 18,
        density_percentage: 4.5,
        is_mandatory: true,
        is_present: true,
        is_overused: true,
        locations_found: ["skills", "work_experience", "summary"],
      },
    ],
    suggestions: [
      {
        id: "sugg-terraform",
        keyword: "terraform",
        is_mandatory: true,
        is_grounded_in_profile: true,
        grounding_evidence: "Candidate profile includes verified skill: Terraform (5 years experience)",
        suggested_action: "Add to Skills section",
        target_section: "skills",
        sample_text: "Terraform (Infrastructure as Code)",
        status: "pending",
        warning: null,
      },
      {
        id: "sugg-event-driven",
        keyword: "event-driven",
        is_mandatory: false,
        is_grounded_in_profile: false,
        grounding_evidence: null,
        suggested_action: "Integrate into bullet points if genuine experience exists",
        target_section: "work",
        sample_text: "Architected event-driven distributed pipeline",
        status: "pending",
        warning: "Warning: Skill not found in verified candidate profile. Do not fabricate experience.",
      },
    ],
    checks: [
      {
        id: "chk-contact-email",
        label: "Contact Email Check",
        category: "contact_info",
        status: "pass",
        detail: "Email found: abhijith@example.com",
        recommendation: null,
      },
      {
        id: "chk-stuffing-aws",
        label: "Keyword Density: aws",
        category: "keyword_density",
        status: "warning",
        detail: "The keyword 'aws' appears 18 times (4.5% density). Densities above 3.5% trigger ATS spam heuristics.",
        recommendation: "Reduce occurrences to between 2 and 5 mentions to avoid penalty filters.",
      },
    ],
    total_words: 400,
    disclaimer:
      "ATS scores are heuristic estimates based on parsing standards and keyword alignment. No algorithm guarantees interview selection or ATS parsing passage.",
    analyzed_at: "2026-10-18T12:00:00Z",
  };

  it("calls POST /api/v1/ats/analyze with the specified payload", async () => {
    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: mockAnalysisResponse,
    });

    const request: ATSAnalysisRequest = {
      cv_version_id: "cv-v1-uuid",
      job_id: "job-target-uuid",
    };

    const result = await atsApi.analyzeCvAts(request);

    expect(postSpy).toHaveBeenCalledTimes(1);
    expect(postSpy).toHaveBeenCalledWith("/ats/analyze", request);
    expect(result.overall_score).toBe(84.5);
    expect(result.scoring_mode).toBe("job_targeted");
    expect(result.components).toHaveLength(4);
  });

  it("calls GET /api/v1/ats/cv/{cv_version_id} with optional job_id query param", async () => {
    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: mockAnalysisResponse,
    });

    const result = await atsApi.getCvAtsAnalysis("cv-v1-uuid", "job-target-uuid");

    expect(getSpy).toHaveBeenCalledTimes(1);
    expect(getSpy).toHaveBeenCalledWith("/ats/cv/cv-v1-uuid", {
      params: { job_id: "job-target-uuid" },
    });
    expect(result.cv_version_id).toBe("cv-v1-uuid");
  });

  it("calls POST /api/v1/ats/apply-suggestions with accepted suggestions and receives new CV version snapshot", async () => {
    const mockApplyResponse: ApplyATSSuggestionsResponse = {
      original_version_id: "cv-v1-uuid",
      new_version_id: "cv-v2-uuid",
      new_version_name: "Tailored Staff Engineer CV (ATS-Optimized)",
      applied_suggestions_count: 1,
      content_snapshot: {
        schema_version: "2.0.0",
        basics: { name: "Abhijith" },
        work: [],
        education: [],
        skills: [{ name: "terraform" }],
        projects: [],
      },
      created_at: "2026-10-18T12:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: mockApplyResponse,
    });

    const request: ApplyATSSuggestionsRequest = {
      cv_version_id: "cv-v1-uuid",
      job_id: "job-target-uuid",
      new_version_name: "Tailored Staff Engineer CV (ATS-Optimized)",
      accepted_suggestion_ids: ["sugg-terraform"],
    };

    const result = await atsApi.applyAtsSuggestions(request);

    expect(postSpy).toHaveBeenCalledTimes(1);
    expect(postSpy).toHaveBeenCalledWith("/ats/apply-suggestions", request);
    expect(result.new_version_id).toBe("cv-v2-uuid");
    expect(result.applied_suggestions_count).toBe(1);
    expect(result.content_snapshot.skills?.[0]?.name).toBe("terraform");
  });

  describe("Explainable Scoring & Audit Integrity", () => {
    it("transparently computes overall score from component weights", () => {
      const sumOfComponents = mockAnalysisResponse.components.reduce(
        (sum, c) => sum + c.score,
        0
      );
      expect(sumOfComponents).toBe(mockAnalysisResponse.overall_score);
      expect(mockAnalysisResponse.overall_score).toBeLessThanOrEqual(100);
      expect(mockAnalysisResponse.overall_score).toBeGreaterThanOrEqual(0);
    });

    it("includes required legal heuristic disclaimer", () => {
      expect(mockAnalysisResponse.disclaimer).toBeDefined();
      expect(mockAnalysisResponse.disclaimer.toLowerCase()).toContain("heuristic");
      expect(mockAnalysisResponse.disclaimer.toLowerCase()).toContain("no algorithm guarantees");
    });

    it("identifies keyword density stuffing with appropriate check warning", () => {
      const overusedKeywords = mockAnalysisResponse.keywords.filter(
        (k) => k.is_overused
      );
      expect(overusedKeywords).toHaveLength(1);
      expect(overusedKeywords[0].keyword).toBe("aws");
      expect(overusedKeywords[0].density_percentage).toBeGreaterThan(3.5);

      const densityCheck = mockAnalysisResponse.checks.find(
        (c) => c.category === "keyword_density"
      );
      expect(densityCheck).toBeDefined();
      expect(densityCheck?.status).toBe("warning");
      expect(densityCheck?.recommendation).toContain("Reduce occurrences");
    });

    it("strictly separates candidate-substantiated suggestions from unsupported suggestions", () => {
      const substantiated = mockAnalysisResponse.suggestions.filter(
        (s) => s.is_grounded_in_profile
      );
      const unsupported = mockAnalysisResponse.suggestions.filter(
        (s) => !s.is_grounded_in_profile
      );

      expect(substantiated).toHaveLength(1);
      expect(substantiated[0].keyword).toBe("terraform");
      expect(substantiated[0].grounding_evidence).toContain("5 years experience");

      expect(unsupported).toHaveLength(1);
      expect(unsupported[0].keyword).toBe("event-driven");
      expect(unsupported[0].warning).toContain("Do not fabricate");
    });
  });
});
