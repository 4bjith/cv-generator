export type JobTargetStatus = "saved" | "archived";

export type CandidateMatchStatus = "supported" | "partial" | "unverified" | "missing";

export type GapType = "absent_from_profile" | "unverified_claim" | "skill_gap";

export interface EvidenceTraceItem {
  id: string;
  title: string;
  source: string;
  source_type: string;
  url?: string | null;
  verification_status: string;
  date?: string | null;
}

export interface JobRequirementItem {
  id: string;
  category: string;
  requirement: string;
  is_mandatory: boolean;
  candidate_match_status: CandidateMatchStatus;
  reasoning?: string | null;
  matched_entity_type?: string | null;
  matched_entity_id?: string | null;
  matched_entity_name?: string | null;
  evidence_ids?: string[];
  evidence_items?: EvidenceTraceItem[];
  confidence_score?: number;
  gap_type?: GapType | null;
}

export interface KeywordSummary {
  total_requirements: number;
  mandatory_count: number;
  preferred_count: number;
  supported_count: number;
  partial_count: number;
  unverified_count: number;
  missing_count: number;
  coverage_percentage: number;
  mandatory_coverage_percentage: number;
  top_matched_keywords: string[];
  top_missing_keywords: string[];
  identified_gaps: string[];
}

export interface JobAnalysisResult {
  job_id: string;
  extracted_at: string;
  role_overview?: string | null;
  seniority_level?: string | null;
  employment_type?: string | null;
  requirements: JobRequirementItem[];
  keyword_summary: KeywordSummary;
}

export interface JobAnalysisResponse {
  job_id: string;
  job_title: string;
  company_name: string;
  analysis: JobAnalysisResult;
}

export interface JobExtractionResult {
  role_overview?: string | null;
  seniority_level?: string | null;
  employment_type?: string | null;
  requirements: JobRequirementItem[];
  extracted_keywords: string[];
}

export interface JobTarget {
  id: string;
  user_id: string;
  title: string;
  company_name: string;
  location?: string | null;
  employment_type?: string | null;
  job_description: string;
  source_url?: string | null;
  user_notes?: string | null;
  status: JobTargetStatus;
  analysis_result?: JobAnalysisResult | null;
  created_at: string;
  updated_at: string;
}

export interface JobTargetCreate {
  title: string;
  company_name: string;
  location?: string;
  employment_type?: string;
  job_description: string;
  source_url?: string;
  user_notes?: string;
  status?: JobTargetStatus;
}

export interface JobTargetUpdate {
  title?: string;
  company_name?: string;
  location?: string | null;
  employment_type?: string | null;
  job_description?: string;
  source_url?: string | null;
  user_notes?: string | null;
  status?: JobTargetStatus;
}

export interface JobTargetListResponse {
  items: JobTarget[];
  total: number;
  limit: number;
  offset: number;
}

export interface JobTargetFilters {
  status?: JobTargetStatus;
  search?: string;
  limit?: number;
  offset?: number;
}
