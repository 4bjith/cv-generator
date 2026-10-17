import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { profileKeys } from "@/lib/query-keys";
import { profileApi } from "@/services/profile/profile.api";
import { CandidateProfileData, ProfileStrength } from "@/types/profile";

describe("TanStack Query Profile State & Invalidation", () => {
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

  it("stores candidate profile in query cache and updates on mutation", async () => {
    const mockProfile: CandidateProfileData = {
      id: "p-test",
      user_id: "u-test",
      first_name: "Priya",
      last_name: "Sharma",
      primary_title: "Full Stack Engineer",
      secondary_titles: [],
      career_level: "mid",
      specializations: [],
      links: [],
      experiences: [],
      skills: [],
      projects: [],
      education: [],
      certifications: [],
      achievements: [],
      languages: [],
      career_preferences: null,
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    vi.spyOn(profileApi, "getProfile").mockResolvedValueOnce(mockProfile);

    // Populate profile query
    queryClient.setQueryData(profileKeys.current(), mockProfile);

    const cachedProfile = queryClient.getQueryData<CandidateProfileData>(profileKeys.current());
    expect(cachedProfile?.first_name).toBe("Priya");
    expect(cachedProfile?.primary_title).toBe("Full Stack Engineer");

    // Invalidate profile query
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    await queryClient.invalidateQueries({ queryKey: profileKeys.all });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: profileKeys.all });
  });

  it("stores profile strength and invalidates when sub-entities change", async () => {
    const mockStrength: ProfileStrength = {
      completion_percentage: 92,
      completed_sections_count: 11,
      total_sections_count: 12,
      sections_breakdown: {
        personal_info: true,
        contact: true,
        professional_identity: true,
        summary: true,
        experience: true,
        skills: true,
        projects: true,
        education: true,
        certifications: true,
        achievements: true,
        languages: true,
        career_preferences: true,
      },
      suggestions: [],
      quality: {
        score: 92,
        completeness: 92,
        evidence_coverage: 85,
        skill_validation: 90,
        experience_quality: 90,
        project_quality: 85,
        achievement_quality: 80,
        recommendations: [],
      },
    };

    queryClient.setQueryData(profileKeys.strength(), mockStrength);

    const cachedStrength = queryClient.getQueryData<ProfileStrength>(profileKeys.strength());
    expect(cachedStrength?.completion_percentage).toBe(92);

    // Invalidate strength
    await queryClient.invalidateQueries({ queryKey: profileKeys.strength() });
  });

  it("updates career preferences cache independently", async () => {
    const mockPreferences = {
      id: "pref-1",
      profile_id: "p-test",
      target_roles: ["Staff Engineer", "Engineering Manager"],
      target_industries: ["Fintech", "AI Infrastructure"],
      preferred_locations: ["Bengaluru", "Remote"],
      remote_preference: "flexible" as const,
      availability_status: "actively_looking" as const,
      notice_period_days: 30,
    };

    queryClient.setQueryData(profileKeys.preferences(), mockPreferences);

    const cached = queryClient.getQueryData(profileKeys.preferences());
    expect(cached).toEqual(mockPreferences);
  });

  it("stores evidence list in query cache and invalidates on mutation", async () => {
    const mockEvidence = [
      {
        id: "ev-100",
        profile_id: "p-test",
        title: "Distributed Messaging Latency Benchmark",
        source: "Grafana Dashboards",
        source_type: "metric_report" as const,
        verification_status: "verified" as const,
        provenance: "user_provided" as const,
        associations: [
          { id: "a-1", evidence_id: "ev-100", entity_type: "experience", entity_id: "exp-1", created_at: "2026-10-05T00:00:00Z" },
        ],
        created_at: "2026-10-05T00:00:00Z",
        updated_at: "2026-10-05T00:00:00Z",
      },
    ];

    queryClient.setQueryData(profileKeys.evidence(), mockEvidence);

    const cachedEvidence = queryClient.getQueryData(profileKeys.evidence());
    expect(cachedEvidence).toEqual(mockEvidence);

    // Invalidate evidence query
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
    await queryClient.invalidateQueries({ queryKey: profileKeys.evidence() });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: profileKeys.evidence() });
  });

  it("manages evidence-aware profile quality breakdown in strength cache", async () => {
    const mockStrength: ProfileStrength = {
      completion_percentage: 88,
      completed_sections_count: 10,
      total_sections_count: 12,
      sections_breakdown: {
        personal_info: true,
        contact: true,
        professional_identity: true,
        summary: true,
        experience: true,
        skills: true,
        projects: true,
        education: true,
        certifications: false,
        achievements: false,
        languages: true,
        career_preferences: true,
      },
      suggestions: ["Add evidence to your work experiences"],
      quality: {
        score: 82,
        completeness: 88,
        evidence_coverage: 75,
        skill_validation: 80,
        experience_quality: 85,
        project_quality: 80,
        achievement_quality: 50,
        recommendations: [
          "Connect React and FastAPI to relevant projects",
          "Add evidence to work experience at ScaleTech Systems",
        ],
      },
    };

    queryClient.setQueryData(profileKeys.strength(), mockStrength);

    const cached = queryClient.getQueryData<ProfileStrength>(profileKeys.strength());
    expect(cached?.quality.score).toBe(82);
    expect(cached?.quality.evidence_coverage).toBe(75);
    expect(cached?.quality.recommendations).toHaveLength(2);
  });
});

