export type ClarificationQuestionStatus = "unanswered" | "answered" | "skipped";

export interface ClarificationQuestionItem {
  id: string;
  job_id: string;
  requirement_id?: string | null;
  requirement_text: string;
  is_mandatory: boolean;
  category: string;
  gap_type?: string | null;
  question: string;
  context: string;
  status: ClarificationQuestionStatus;
  answer?: string | null;
  answered_at?: string | null;
  priority: number;
  suggested_options?: string[];
  save_to_profile: boolean;
  provenance: string;
  verification_status: string;
}

export interface ClarificationSessionResponse {
  job_id: string;
  job_title: string;
  company_name: string;
  total_questions: number;
  answered_count: number;
  skipped_count: number;
  unanswered_count: number;
  is_completed: boolean;
  questions: ClarificationQuestionItem[];
  updated_at?: string | null;
}

export interface ClarificationAnswerRequest {
  answer: string;
  save_to_profile?: boolean;
}

export interface ClarificationBulkAnswerRequest {
  answers: Record<string, string>;
  save_to_profile?: boolean;
}

export interface ClarificationPromoteRequest {
  category?: string;
  skill_proficiency?: string;
}
