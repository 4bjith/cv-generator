export interface JobSearchProfile {
  id: string;
  user_id: string;
  target_roles: string[];
  primary_skills: string[];
  target_locations: string[];
  is_remote_prioritized: boolean;
  include_internships: boolean;
  fresher_mode: boolean;
  min_salary: number | null;
  max_job_age_days: number;
  daily_application_cap: number;
  cron_schedule: string;
  auto_submit_enabled: boolean;
  is_active: boolean;
  emergency_stopped: boolean;
  created_at: string;
  updated_at: string;
}

export interface DiscoveredJob {
  id: string;
  user_id: string;
  source_platform: string;
  external_id: string;
  title: string;
  company_name: string;
  location: string;
  is_remote: boolean;
  employment_type: string;
  source_url: string;
  apply_url: string;
  posted_at: string | null;
  raw_description: string;
  extracted_skills: string[];
  match_score: number;
  fit_reasoning: string;
  eligibility_status: "eligible" | "ineligible" | "needs_review";
  status: "discovered" | "shortlisted" | "tailored" | "applied" | "dismissed";
  created_at: string;
}

export interface QAMemoryBankItem {
  id: string;
  user_id: string;
  category: string;
  question_pattern: string;
  answer_value: string;
  is_confirmed: boolean;
  user_notes?: string;
  created_at: string;
}

export interface RecruiterOutreach {
  id: string;
  application_id: string;
  company_name: string;
  contact_name: string;
  contact_title: string;
  channel: "linkedin" | "email";
  profile_url?: string;
  email?: string;
  message_type: "connection_note" | "recruiter_email" | "referral_request";
  message_content: string;
  status: "drafted" | "approved" | "sent" | "replied";
  sent_at?: string;
  reply_notes?: string;
  created_at: string;
}

export interface ApplicationRecord {
  id: string;
  user_id: string;
  discovered_job_id?: string;
  job_target_id: string;
  cv_version_id?: string;
  cover_letter_id?: string;
  submission_mode: string;
  status:
    | "prepared"
    | "submitting"
    | "submitted_confirmed"
    | "submission_failed"
    | "requires_human_intervention"
    | "screening"
    | "interview"
    | "offer"
    | "rejected";
  portal_confirmation_code?: string;
  screenshot_url?: string;
  failure_reason?: string;
  submitted_at?: string;
  created_at: string;
  recruiter_outreach: RecruiterOutreach[];
}

export interface AgentDailyReport {
  id: string;
  user_id: string;
  run_date: string;
  jobs_discovered_count: number;
  jobs_shortlisted_count: number;
  applications_submitted_count: number;
  applications_prepared_count: number;
  recruiter_outreach_count: number;
  action_items: Array<{
    type: string;
    title: string;
    apply_url?: string;
    notes?: string;
  }>;
  summary_markdown: string;
  created_at: string;
}

export interface AgentRunResult {
  status: string;
  message: string;
  jobs_found: number;
  jobs_shortlisted: number;
  applications_prepared: number;
  applications_submitted: number;
  recruiter_messages_drafted: number;
  report?: AgentDailyReport;
}
