export type CoverLetterTone = "professional" | "concise" | "technical" | "formal";

export type CoverLetterLength = "short" | "standard" | "detailed";

export type CoverLetterStatus = "draft" | "ready" | "archived";

export interface FactualClaimItem {
  claim_text: string;
  entity_type: string;
  entity_id?: string | null;
  verification_status: string;
}

export interface GenerateCoverLetterRequest {
  job_id: string;
  cv_version_id?: string | null;
  tone?: CoverLetterTone;
  length_option?: CoverLetterLength;
  additional_instructions?: string | null;
  recipient_name?: string | null;
  recipient_title?: string | null;
  recipient_company?: string | null;
  recipient_address?: string | null;
  name?: string | null;
}

export interface RegenerateCoverLetterRequest {
  tone?: CoverLetterTone;
  length_option?: CoverLetterLength;
  additional_instructions?: string | null;
  preserve_as_new_version?: boolean;
  new_name?: string | null;
}

export interface UpdateCoverLetterRequest {
  name?: string;
  status?: CoverLetterStatus;
  tone?: CoverLetterTone;
  length_option?: CoverLetterLength;
  recipient_name?: string | null;
  recipient_title?: string | null;
  recipient_company?: string | null;
  recipient_address?: string | null;
  salutation?: string;
  opening?: string;
  body_paragraphs?: string[];
  closing?: string;
  sign_off?: string;
  sender_name?: string;
  sender_contact?: string | null;
  full_content?: string;
}

export interface CoverLetterSummary {
  id: string;
  name: string;
  status: CoverLetterStatus;
  tone: CoverLetterTone;
  length_option: CoverLetterLength;
  job_target_id?: string | null;
  job_target_title?: string | null;
  job_target_company?: string | null;
  cv_version_id?: string | null;
  cv_version_name?: string | null;
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface CoverLetterResponse {
  id: string;
  user_id: string;
  job_target_id?: string | null;
  job_target_title?: string | null;
  job_target_company?: string | null;
  cv_version_id?: string | null;
  cv_version_name?: string | null;
  name: string;
  status: CoverLetterStatus;
  tone: CoverLetterTone;
  length_option: CoverLetterLength;
  recipient_name?: string | null;
  recipient_title?: string | null;
  recipient_company?: string | null;
  recipient_address?: string | null;
  salutation: string;
  opening: string;
  body_paragraphs: string[];
  closing: string;
  sign_off: string;
  sender_name: string;
  sender_contact?: string | null;
  full_content: string;
  word_count: number;
  factual_claims: FactualClaimItem[];
  unresolved_gaps: string[];
  change_summary?: string | null;
  generation_parameters?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CoverLetterListResponse {
  items: CoverLetterSummary[];
  total: number;
  limit: number;
  offset: number;
}
