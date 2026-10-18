import { CVContentSnapshot } from "./cv";

export interface CVTailorRequest {
  template?: string;
  tone?: string;
  target_role?: string;
  focus_areas?: string[];
  custom_instructions?: string;
  include_clarifications?: boolean;
}

export interface CVTailoringResponse {
  cv_version_id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  version_name: string;
  status: string;
  content_snapshot: CVContentSnapshot;
  change_summary: string[];
  unresolved_gaps: string[];
  quality_score: number;
  unsupported_claims_prevented: string[];
  created_at: string;
}
