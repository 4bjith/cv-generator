import { CVContentSnapshot } from "./cv";

export type ATSCheckSeverity = "pass" | "warning" | "review" | "info";

export type ATSCheckCategory =
  | "contact_info"
  | "headings"
  | "dates"
  | "template_layout"
  | "symbols_and_formatting"
  | "keyword_density"
  | "content_quality";

export interface ATSCheckItem {
  id: string;
  label: string;
  category: ATSCheckCategory;
  status: ATSCheckSeverity;
  detail: string;
  recommendation?: string | null;
}

export interface ATSComponentScore {
  name: string;
  score: number;
  max_score: number;
  weight_percentage: number;
  explanation: string;
  deductions: string[];
}

export interface KeywordOccurrenceItem {
  keyword: string;
  count: number;
  density_percentage: number;
  is_mandatory: boolean;
  is_present: boolean;
  is_overused: boolean;
  locations_found: string[];
}

export interface GroundedKeywordSuggestion {
  id: string;
  keyword: string;
  is_mandatory: boolean;
  is_grounded_in_profile: boolean;
  grounding_evidence?: string | null;
  suggested_action: string;
  target_section: string;
  sample_text?: string | null;
  status: "pending" | "accepted" | "rejected";
  warning?: string | null;
}

export interface ATSAnalysisRequest {
  cv_version_id: string;
  job_id?: string | null;
}

export interface ATSAnalysisResponse {
  id: string;
  cv_version_id: string;
  cv_version_name: string;
  job_id?: string | null;
  job_title?: string | null;
  company_name?: string | null;
  overall_score: number;
  scoring_mode: "job_targeted" | "general_baseline";
  components: ATSComponentScore[];
  keyword_coverage_percentage: number;
  total_words: number;
  checks: ATSCheckItem[];
  keywords: KeywordOccurrenceItem[];
  suggestions: GroundedKeywordSuggestion[];
  disclaimer: string;
  analyzed_at: string;
}

export interface ApplyATSSuggestionsRequest {
  cv_version_id: string;
  accepted_suggestion_ids: string[];
  job_id?: string | null;
  new_version_name?: string | null;
}

export interface ApplyATSSuggestionsResponse {
  original_version_id: string;
  new_version_id: string;
  new_version_name: string;
  applied_suggestions_count: number;
  content_snapshot: CVContentSnapshot;
  created_at: string;
}
