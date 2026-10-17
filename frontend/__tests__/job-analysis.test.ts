import { describe, it, expect } from "vitest";
import {
  JobRequirementItem,
  JobAnalysisResult,
  CandidateMatchStatus,
  GapType,
} from "@/types/job";

describe("Job Requirement & Intelligence Domain Logic", () => {
  it("enforces canonical requirement structure with mandatory/preferred flag and candidate match status", () => {
    const requirement: JobRequirementItem = {
      id: "req-101",
      category: "skills",
      requirement: "Expertise in React and TypeScript",
      is_mandatory: true,
      candidate_match_status: "supported",
      matched_entity_type: "skill",
      matched_entity_name: "React",
      evidence_ids: ["ev-abc-1"],
      evidence_items: [
        {
          id: "ev-abc-1",
          source: "github_repo",
          source_type: "code_repository",
          title: "Production React System",
          url: "https://github.com/example/react-app",
          verification_status: "verified",
          date: "2026-01-01",
        },
      ],
      confidence_score: 0.95,
      gap_type: null,
      reasoning: "Matched confirmed skill 'React' with strong repository evidence.",
    };

    expect(requirement.id).toBe("req-101");
    expect(requirement.is_mandatory).toBe(true);
    expect(requirement.candidate_match_status).toBe("supported");
    expect(requirement.evidence_items?.[0].source).toBe("github_repo");
    expect(requirement.gap_type).toBeNull();
  });

  it("distinguishes genuine skill gap from absent profile data and unverified claims", () => {
    const gapTypes: GapType[] = ["absent_from_profile", "unverified_claim", "skill_gap"];

    const absentReq: JobRequirementItem = {
      id: "req-201",
      category: "certifications",
      requirement: "AWS Certified Solutions Architect",
      is_mandatory: false,
      candidate_match_status: "missing",
      evidence_ids: [],
      confidence_score: 0,
      gap_type: "absent_from_profile",
      reasoning: "Certification not mentioned anywhere in candidate profile.",
    };

    const unverifiedReq: JobRequirementItem = {
      id: "req-202",
      category: "technologies",
      requirement: "Kubernetes orchestration",
      is_mandatory: true,
      candidate_match_status: "unverified",
      evidence_ids: [],
      confidence_score: 0.4,
      gap_type: "unverified_claim",
      reasoning: "Skill claim exists on profile but lacks verifiable evidence link or artifact.",
    };

    const skillGapReq: JobRequirementItem = {
      id: "req-203",
      category: "experience",
      requirement: "10+ years of distributed systems engineering",
      is_mandatory: true,
      candidate_match_status: "partial",
      evidence_ids: ["ev-work-1"],
      confidence_score: 0.4,
      gap_type: "skill_gap",
      reasoning: "Candidate experience falls short of senior 10-year requirement threshold.",
    };

    expect(absentReq.gap_type).toBe("absent_from_profile");
    expect(unverifiedReq.candidate_match_status).toBe("unverified");
    expect(skillGapReq.candidate_match_status).toBe("partial");
    expect(skillGapReq.gap_type).toBe("skill_gap");
  });

  it("calculates requirement distributions and coverage percentages accurately", () => {
    const requirements: JobRequirementItem[] = [
      {
        id: "1",
        category: "skills",
        requirement: "FastAPI",
        is_mandatory: true,
        candidate_match_status: "supported",
      },
      {
        id: "2",
        category: "skills",
        requirement: "PostgreSQL",
        is_mandatory: true,
        candidate_match_status: "supported",
      },
      {
        id: "3",
        category: "technologies",
        requirement: "Docker",
        is_mandatory: true,
        candidate_match_status: "unverified",
      },
      {
        id: "4",
        category: "technologies",
        requirement: "Kubernetes",
        is_mandatory: false,
        candidate_match_status: "missing",
      },
    ];

    const supported = requirements.filter((r) => r.candidate_match_status === "supported").length;
    const unverified = requirements.filter((r) => r.candidate_match_status === "unverified").length;
    const missing = requirements.filter((r) => r.candidate_match_status === "missing").length;

    expect(supported).toBe(2);
    expect(unverified).toBe(1);
    expect(missing).toBe(1);

    const mandatory = requirements.filter((r) => r.is_mandatory);
    const mandatorySupported = mandatory.filter((r) => r.candidate_match_status === "supported").length;
    const mandatoryScore = (mandatorySupported / mandatory.length) * 100;
    expect(Math.round(mandatoryScore)).toBe(67);
  });
});
