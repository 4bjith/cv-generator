import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { profileApi } from "@/services/profile/profile.api";
import {
  CandidateProfileCreatePayload,
  CandidateProfileData,
  ProfileStrength,
  WorkExperience,
  CandidateSkill,
  ProjectRecord,
} from "@/types/profile";

describe("Profile API Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("calls GET /profile and returns profile data", async () => {
    const mockProfile: CandidateProfileData = {
      id: "p-1",
      user_id: "u-1",
      first_name: "Aarav",
      last_name: "Mehta",
      primary_title: "Senior Frontend Engineer",
      secondary_titles: [],
      career_level: "senior",
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

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockProfile });

    const result = await profileApi.getProfile();

    expect(getSpy).toHaveBeenCalledWith("/profile");
    expect(result.first_name).toBe("Aarav");
    expect(result.primary_title).toBe("Senior Frontend Engineer");
  });

  it("calls POST /profile with create payload", async () => {
    const payload: CandidateProfileCreatePayload = {
      first_name: "Aarav",
      last_name: "Mehta",
      primary_title: "Staff Engineer",
      career_level: "lead",
    };

    const mockResponse: CandidateProfileData = {
      id: "p-2",
      user_id: "u-1",
      first_name: "Aarav",
      last_name: "Mehta",
      primary_title: "Staff Engineer",
      secondary_titles: [],
      career_level: "lead",
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

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockResponse });

    const result = await profileApi.createProfile(payload);

    expect(postSpy).toHaveBeenCalledWith("/profile", payload);
    expect(result.career_level).toBe("lead");
  });

  it("calls PATCH /profile to update profile fields", async () => {
    const updatePayload = {
      professional_headline: "Architecting high-scale frontends",
      years_of_experience: 8,
    };

    const mockUpdated: CandidateProfileData = {
      id: "p-1",
      user_id: "u-1",
      first_name: "Aarav",
      professional_headline: "Architecting high-scale frontends",
      secondary_titles: [],
      years_of_experience: 8,
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

    const patchSpy = vi.spyOn(apiClient, "patch").mockResolvedValueOnce({ data: mockUpdated });

    const result = await profileApi.updateProfile(updatePayload);

    expect(patchSpy).toHaveBeenCalledWith("/profile", updatePayload);
    expect(result.years_of_experience).toBe(8);
  });

  it("calls DELETE /profile to remove profile", async () => {
    const deleteSpy = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({
      data: null,
    });

    await profileApi.deleteProfile();

    expect(deleteSpy).toHaveBeenCalledWith("/profile");
  });

  it("calls GET /profile/strength to get readiness scorecard", async () => {
    const mockStrength: ProfileStrength = {
      completion_percentage: 85,
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
      suggestions: ["Add a certification or credential to strengthen profile."],
      quality: {
        score: 80,
        completeness: 85,
        evidence_coverage: 70,
        skill_validation: 75,
        experience_quality: 80,
        project_quality: 75,
        achievement_quality: 50,
        recommendations: ["Add direct evidence to work experience"],
      },
    };

    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockStrength });

    const result = await profileApi.getStrength();

    expect(getSpy).toHaveBeenCalledWith("/profile/strength");
    expect(result.completion_percentage).toBe(85);
    expect(result.sections_breakdown.skills).toBe(true);
  });

  it("handles Work Experience CRUD API operations", async () => {
    const mockExp: WorkExperience = {
      id: "exp-1",
      profile_id: "p-1",
      company: "Tech Corp",
      position: "Senior Engineer",
      employment_type: "full_time",
      start_date: "2022-01-01",
      is_current: true,
      responsibilities: ["Lead engineering team"],
      achievements: ["Reduced latency by 40%"],
      metrics: [{ value: 40, unit: "percent", description: "Reduced latency" }],
      technologies: ["React", "FastAPI"],
      provenance: "user_provided",
      evidence_ids: [],
      order_index: 0,
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockExp });
    const addResult = await profileApi.addExperience({
      company: "Tech Corp",
      position: "Senior Engineer",
      employment_type: "full_time",
      start_date: "2022-01-01",
      is_current: true,
      responsibilities: ["Lead engineering team"],
      achievements: ["Reduced latency by 40%"],
      metrics: [{ value: 40, unit: "percent", description: "Reduced latency" }],
      technologies: ["React", "FastAPI"],
    });

    expect(postSpy).toHaveBeenCalledWith("/profile/experience", expect.objectContaining({ company: "Tech Corp" }));
    expect(addResult.metrics?.[0]?.value).toBe(40);

    const deleteSpy = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({
      data: null,
    });
    await profileApi.deleteExperience("exp-1");
    expect(deleteSpy).toHaveBeenCalledWith("/profile/experience/exp-1");
  });

  it("handles Skills CRUD API operations", async () => {
    const mockSkill: CandidateSkill = {
      id: "skill-1",
      profile_id: "p-1",
      name: "TypeScript",
      category: "programming_language",
      proficiency: "expert",
      years_of_experience: 5,
      evidence_references: ["Project A"],
      provenance: "user_provided",
      experience_ids: [],
      project_ids: [],
      certification_ids: [],
      achievement_ids: [],
      evidence_ids: [],
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockSkill });
    const result = await profileApi.addSkill({
      name: "TypeScript",
      category: "programming_language",
      proficiency: "expert",
      years_of_experience: 5,
    });

    expect(postSpy).toHaveBeenCalledWith("/profile/skills", expect.objectContaining({ name: "TypeScript" }));
    expect(result.name).toBe("TypeScript");
    expect(result.category).toBe("programming_language");
  });

  it("handles Projects CRUD API operations", async () => {
    const mockProject: ProjectRecord = {
      id: "proj-1",
      profile_id: "p-1",
      name: "Distributed Task Engine",
      role: "Lead Architect",
      problem: "Tasks were dropping under load",
      solution: "Implemented Redis stream queues",
      responsibilities: [],
      achievements: [],
      architecture: "Microservices with async workers",
      technologies: ["Go", "Redis", "Docker"],
      featured: true,
      provenance: "user_provided",
      evidence_ids: [],
      order_index: 0,
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockProject });
    const result = await profileApi.addProject({
      name: "Distributed Task Engine",
      role: "Lead Architect",
      problem: "Tasks were dropping under load",
      solution: "Implemented Redis stream queues",
      architecture: "Microservices with async workers",
      technologies: ["Go", "Redis", "Docker"],
      featured: true,
    });

    expect(postSpy).toHaveBeenCalledWith("/profile/projects", expect.objectContaining({ name: "Distributed Task Engine" }));
    expect(result.featured).toBe(true);
  });

  it("handles Evidence CRUD and association operations (Phase 1.1)", async () => {
    const mockEvidence = {
      id: "ev-1",
      profile_id: "p-1",
      title: "Production Grafana Benchmark",
      source: "Datadog / Grafana",
      source_type: "metric_report" as const,
      url: "https://app.datadoghq.com/dashboard/123",
      verification_status: "verified" as const,
      provenance: "user_provided" as const,
      associations: [
        { id: "a-1", evidence_id: "ev-1", entity_type: "experience", entity_id: "exp-1", created_at: "2026-10-05T00:00:00Z" },
      ],
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: mockEvidence });
    const created = await profileApi.createEvidence({
      title: "Production Grafana Benchmark",
      source: "Datadog / Grafana",
      source_type: "metric_report",
      url: "https://app.datadoghq.com/dashboard/123",
      verification_status: "verified",
    });

    expect(postSpy).toHaveBeenCalledWith("/profile/evidence", expect.objectContaining({ title: "Production Grafana Benchmark" }));
    expect(created.associations).toHaveLength(1);
    expect(created.verification_status).toBe("verified");

    const getListSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: [mockEvidence] });
    const list = await profileApi.listEvidence();
    expect(getListSpy).toHaveBeenCalledWith("/profile/evidence");
    expect(list).toHaveLength(1);

    const deleteSpy = vi.spyOn(apiClient, "delete").mockResolvedValueOnce({ data: null });
    await profileApi.deleteEvidence("ev-1");
    expect(deleteSpy).toHaveBeenCalledWith("/profile/evidence/ev-1");
  });

  it("handles Skill Relationships syncing (Phase 1.1)", async () => {
    const mockUpdatedSkill: CandidateSkill = {
      id: "skill-1",
      profile_id: "p-1",
      name: "React",
      provenance: "user_provided",
      experience_ids: ["exp-1", "exp-2"],
      project_ids: ["proj-1"],
      certification_ids: [],
      achievement_ids: [],
      evidence_ids: [],
      evidence_references: [],
      created_at: "2026-10-05T00:00:00Z",
      updated_at: "2026-10-05T00:00:00Z",
    };

    const putSpy = vi.spyOn(apiClient, "put").mockResolvedValueOnce({ data: mockUpdatedSkill });
    const result = await profileApi.syncSkillRelationships("skill-1", {
      experience_ids: ["exp-1", "exp-2"],
      project_ids: ["proj-1"],
    });

    expect(putSpy).toHaveBeenCalledWith("/profile/skills/skill-1/relationships", {
      experience_ids: ["exp-1", "exp-2"],
      project_ids: ["proj-1"],
    });
    expect(result.experience_ids).toEqual(["exp-1", "exp-2"]);
    expect(result.project_ids).toEqual(["proj-1"]);
  });
});

