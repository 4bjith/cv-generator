import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient } from "@/lib/api/axios";
import { jobsApi } from "@/services/jobs/jobs.api";
import {
  ClarificationSessionResponse,
  ClarificationQuestionItem,
  ClarificationAnswerRequest,
  ClarificationBulkAnswerRequest,
} from "@/types/clarification";
import {
  CVTailorRequest,
  CVTailoringResponse,
} from "@/types/tailoring";

describe("Clarification Engine & AI CV Tailoring Frontend Service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockSession: ClarificationSessionResponse = {
    job_id: "job-123",
    job_title: "Staff Systems Engineer",
    company_name: "Apex Data",
    total_questions: 2,
    answered_count: 1,
    skipped_count: 0,
    unanswered_count: 1,
    is_completed: false,
    questions: [
      {
        id: "q-1",
        job_id: "job-123",
        requirement_id: "req-1",
        requirement_text: "Apache Kafka streaming architecture",
        is_mandatory: true,
        category: "skills",
        gap_type: "unverified_claim",
        question: "Do you have production experience with Apache Kafka?",
        context: "The role requires event streaming architectures.",
        priority: 1,
        status: "answered",
        answer: "Yes, 3 years building streaming pipelines at scale.",
        answered_at: "2026-10-18T10:00:00Z",
        save_to_profile: true,
        provenance: "candidate_clarification",
        verification_status: "unverified",
      },
      {
        id: "q-2",
        job_id: "job-123",
        requirement_id: "req-2",
        requirement_text: "Kubernetes container orchestration",
        is_mandatory: false,
        category: "technologies",
        gap_type: "absent_from_profile",
        question: "Have you worked with Kubernetes clusters in production?",
        context: "Preferred qualification for cloud orchestration.",
        priority: 2,
        status: "unanswered",
        answer: null,
        answered_at: null,
        save_to_profile: false,
        provenance: "candidate_clarification",
        verification_status: "unverified",
      },
    ],
  };

  it("fetches clarification session with prioritized questions and statistics", async () => {
    const getSpy = vi.spyOn(apiClient, "get").mockResolvedValueOnce({ data: mockSession });

    const session = await jobsApi.getClarifications("job-123");

    expect(getSpy).toHaveBeenCalledWith("/jobs/job-123/clarifications");
    expect(session.job_id).toBe("job-123");
    expect(session.questions.length).toBe(2);
    expect(session.questions[0].priority).toBe(1);
    expect(session.questions[0].is_mandatory).toBe(true);
    expect(session.questions[0].status).toBe("answered");
    expect(session.questions[1].priority).toBe(2);
    expect(session.questions[1].status).toBe("unanswered");
  });

  it("submits single answer with optional profile promotion flag", async () => {
    const updatedSession: ClarificationSessionResponse = {
      ...mockSession,
      answered_count: 2,
      unanswered_count: 0,
      is_completed: true,
      questions: [
        mockSession.questions[0],
        {
          ...mockSession.questions[1],
          status: "answered",
          answer: "Managed 5-node EKS clusters for 2 years.",
          answered_at: "2026-10-18T10:05:00Z",
          save_to_profile: true,
        },
      ],
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: updatedSession });

    const payload: ClarificationAnswerRequest = {
      answer: "Managed 5-node EKS clusters for 2 years.",
      save_to_profile: true,
    };

    const result = await jobsApi.answerClarificationQuestion("job-123", "q-2", payload);

    expect(postSpy).toHaveBeenCalledWith(
      "/jobs/job-123/clarifications/q-2/answer",
      payload
    );
    expect(result.answered_count).toBe(2);
    expect(result.questions[1].status).toBe("answered");
    expect(result.questions[1].answer).toBe("Managed 5-node EKS clusters for 2 years.");
    expect(result.questions[1].save_to_profile).toBe(true);
  });

  it("skips clarification question when candidate has no relevant background", async () => {
    const skippedSession: ClarificationSessionResponse = {
      ...mockSession,
      skipped_count: 1,
      unanswered_count: 0,
      questions: [
        mockSession.questions[0],
        {
          ...mockSession.questions[1],
          status: "skipped",
          answer: null,
        },
      ],
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({ data: skippedSession });

    const result = await jobsApi.skipClarificationQuestion("job-123", "q-2");

    expect(postSpy).toHaveBeenCalledWith(
      "/jobs/job-123/clarifications/q-2/skip"
    );
    expect(result.skipped_count).toBe(1);
    expect(result.questions[1].status).toBe("skipped");
    expect(result.questions[1].answer).toBeNull();
  });

  it("promotes confirmed clarification to master candidate profile as unverified evidence", async () => {
    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: {
        status: "promoted",
        requirement: "FastAPI and streaming experience",
        promoted_entity_id: "ev-k8s-new",
        verification_status: "unverified",
        provenance: "candidate_clarification",
      },
    });

    const result = await jobsApi.promoteClarificationAnswer("job-123", "q-2", {
      category: "skills",
      skill_proficiency: "advanced",
    });

    expect(postSpy).toHaveBeenCalledWith(
      "/jobs/job-123/clarifications/q-2/promote",
      { category: "skills", skill_proficiency: "advanced" }
    );
    expect(result.status).toBe("promoted");
    expect(result.requirement).toBe("FastAPI and streaming experience");
  });

  it("submits bulk clarification answers in a single request", async () => {
    const bulkSession: ClarificationSessionResponse = {
      ...mockSession,
      answered_count: 2,
      unanswered_count: 0,
      is_completed: true,
    };

    const bulkSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: bulkSession,
    });

    const payload: ClarificationBulkAnswerRequest = {
      answers: {
        "q-1": "Updated answer 1",
        "q-2": "Answer 2",
      },
      save_to_profile: true,
    };

    const result = await jobsApi.bulkAnswerClarifications("job-123", payload);

    expect(bulkSpy).toHaveBeenCalledWith(
      "/jobs/job-123/clarifications/bulk",
      payload
    );
    expect(result.answered_count).toBe(2);
    expect(result.unanswered_count).toBe(0);
    expect(result.is_completed).toBe(true);
  });

  it("triggers evidence-grounded CV tailoring and receives independent CVVersion snapshot", async () => {
    const mockTailoringResponse: CVTailoringResponse = {
      cv_version_id: "cv-tailored-999",
      job_id: "job-123",
      job_title: "Staff Systems Engineer",
      company_name: "Apex Data",
      version_name: "Staff Engineer - Kafka & Distributed Systems",
      status: "ready",
      quality_score: 95,
      unsupported_claims_prevented: [],
      change_summary: [
        "Elevated streaming systems experience to top of career summary",
        "Aligned Kafka cluster management evidence with job requirements",
      ],
      unresolved_gaps: [
        "Kubernetes container orchestration remains unconfirmed",
      ],
      content_snapshot: {
        schema_version: "2.0.0",
        basics: {
          name: "Alex Morgan",
          label: "Senior Distributed Systems Engineer",
          email: "alex@example.com",
        },
        work: [],
        skills: [],
        education: [],
        presentation: {
          template: "modern",
          color_scheme: "emerald",
          section_order: ["basics", "skills", "work", "education", "projects"],
        },
      },
      created_at: "2026-10-18T10:10:00Z",
    };

    const postSpy = vi.spyOn(apiClient, "post").mockResolvedValueOnce({
      data: mockTailoringResponse,
    });

    const tailorPayload: CVTailorRequest = {
      template: "modern",
      target_role: "Staff Engineer",
      custom_instructions: "Emphasize high-throughput messaging",
    };

    const response = await jobsApi.tailorCv("job-123", tailorPayload);

    expect(postSpy).toHaveBeenCalledWith(
      "/jobs/job-123/tailor-cv",
      tailorPayload
    );
    expect(response.cv_version_id).toBe("cv-tailored-999");
    expect(response.change_summary.length).toBeGreaterThan(0);
    expect(response.unresolved_gaps.length).toBeGreaterThan(0);
    expect(response.content_snapshot.schema_version).toBe("2.0.0");
    expect(response.content_snapshot.presentation?.template).toBe("modern");
  });
});
