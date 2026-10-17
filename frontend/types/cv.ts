export type CVVersionStatus = "draft" | "ready" | "archived";

export interface CVLocation {
  address?: string | null;
  postal_code?: string | null;
  postalCode?: string | null;
  city?: string | null;
  country_code?: string | null;
  countryCode?: string | null;
  region?: string | null;
  country?: string | null;
}

export interface CVProfile {
  network: string;
  username?: string | null;
  url: string;
  id?: string;
}

export interface CVLinkSnapshot {
  id?: string;
  type: string;
  label: string;
  url: string;
  order_index?: number;
}

export interface CVBasicsSnapshot {
  // Canonical JSON Resume fields
  name?: string;
  label?: string | null;
  image?: string | null;
  email?: string | null;
  phone?: string | null;
  url?: string | null;
  summary?: string | null;
  location?: CVLocation | null;
  profiles?: CVProfile[];

  // Legacy & product-specific fields
  first_name?: string;
  last_name?: string | null;
  preferred_name?: string | null;
  professional_headline?: string | null;
  profile_photo?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  country_code?: string | null;
  primary_title?: string | null;
  secondary_titles?: string[];
  career_level?: string | null;
  industry?: string | null;
  years_of_experience?: number | null;
  specializations?: string[];
  base_summary?: string | null;
}

export interface CVWorkSnapshot {
  // Canonical JSON Resume fields
  name?: string;
  position?: string;
  url?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  summary?: string | null;
  highlights?: string[];

  // Extended Application & Legacy fields
  id?: string;
  company?: string;
  employment_type?: string;
  location?: string | null;
  start_date?: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
  responsibilities?: string[];
  achievements?: string[];
  technologies?: string[];
  metrics?: Array<Record<string, any>>;
  provenance?: string;
  evidence_ids?: string[];
  order_index?: number;
}

// Backward-compatible alias
export type CVExperienceSnapshot = CVWorkSnapshot;

export interface CVEducationSnapshot {
  // Canonical JSON Resume fields
  institution: string;
  url?: string | null;
  area?: string | null;
  studyType?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  score?: string | null;
  courses?: string[];

  // Extended Application & Legacy fields
  id?: string;
  degree?: string;
  field_of_study?: string | null;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  description?: string | null;
  achievements?: string[];
  provenance?: string;
  evidence_ids?: string[];
  order_index?: number;
}

export interface CVSkillSnapshot {
  // Canonical JSON Resume fields
  name: string;
  level?: string | null;
  keywords?: string[];

  // Extended Application & Legacy fields
  id?: string;
  category?: string | null;
  proficiency?: string | null;
  years_of_experience?: number | null;
  last_used?: string | null;
  evidence_references?: string[];
  provenance?: string;
  experience_ids?: string[];
  project_ids?: string[];
  certification_ids?: string[];
  achievement_ids?: string[];
  evidence_ids?: string[];
}

export interface CVProjectSnapshot {
  // Canonical JSON Resume fields
  name: string;
  description?: string | null;
  highlights?: string[];
  keywords?: string[];
  startDate?: string | null;
  endDate?: string | null;
  url?: string | null;
  roles?: string[];

  // Extended Application & Legacy fields
  id?: string;
  role?: string | null;
  problem?: string | null;
  solution?: string | null;
  responsibilities?: string[];
  achievements?: string[];
  technologies?: string[];
  architecture?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  team_size?: number | null;
  live_url?: string | null;
  repository_url?: string | null;
  featured?: boolean;
  provenance?: string;
  evidence_ids?: string[];
  order_index?: number;
}

export interface CVCertificateSnapshot {
  // Canonical JSON Resume fields
  name: string;
  date?: string | null;
  issuer?: string | null;
  url?: string | null;

  // Extended Application & Legacy fields
  id?: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  skills?: string[];
  provenance?: string;
  evidence_ids?: string[];
  order_index?: number;
}

// Backward-compatible alias
export type CVCertificationSnapshot = CVCertificateSnapshot;

export interface CVAwardSnapshot {
  // Canonical JSON Resume fields
  title: string;
  date?: string | null;
  awarder?: string | null;
  summary?: string | null;

  // Extended Application & Legacy fields
  id?: string;
  description?: string | null;
  issuer?: string | null;
  category?: string | null;
  evidence_url?: string | null;
  provenance?: string;
  evidence_ids?: string[];
  order_index?: number;
}

// Backward-compatible alias
export type CVAchievementSnapshot = CVAwardSnapshot;

export interface CVLanguageSnapshot {
  // Canonical JSON Resume fields
  language?: string;
  fluency?: string | null;

  // Extended Application & Legacy fields
  id?: string;
  name?: string;
  proficiency?: string;
}

export interface CVCareerPreferencesSnapshot {
  target_roles?: string[];
  target_industries?: string[];
  preferred_locations?: string[];
  remote_preference?: string | null;
  employment_types?: string[];
  availability_status?: string | null;
  available_from?: string | null;
  notice_period_days?: number | null;
}

export interface CVEvidenceItemSnapshot {
  id?: string;
  title: string;
  description?: string | null;
  source: string;
  source_type?: string;
  url?: string | null;
  notes?: string | null;
  date?: string | null;
  verification_status?: string;
  provenance?: string;
  associated_entities?: Array<Record<string, any>>;
}

export interface CVPresentationSnapshot {
  template?: string;
  typography?: string | null;
  color_scheme?: string | null;
  page_size?: "a4" | "letter" | string;
  spacing?: "compact" | "normal" | "relaxed" | string;
  section_order: string[];
  section_visibility?: Record<string, boolean>;
  item_visibility?: Record<string, boolean>;
  hidden_sections?: string[];
  hidden_items?: Record<string, string[]>;
}

export interface CVExtensionsSnapshot {
  career_preferences?: CVCareerPreferencesSnapshot | null;
  evidence_items?: CVEvidenceItemSnapshot[];
  custom_sections?: Array<Record<string, any>>;
  links?: CVLinkSnapshot[];
  basics_ext?: Record<string, any> | null;
}

export interface CVContentSnapshot {
  schema_version?: string;
  basics?: CVBasicsSnapshot | null;
  work?: CVWorkSnapshot[];
  education?: CVEducationSnapshot[];
  skills?: CVSkillSnapshot[];
  projects?: CVProjectSnapshot[];
  certificates?: CVCertificateSnapshot[];
  awards?: CVAwardSnapshot[];
  languages?: CVLanguageSnapshot[];
  presentation?: CVPresentationSnapshot;
  extensions?: CVExtensionsSnapshot;

  // Legacy mirrors
  experiences?: CVWorkSnapshot[];
  certifications?: CVCertificateSnapshot[];
  achievements?: CVAwardSnapshot[];
  links?: CVLinkSnapshot[];
  career_preferences?: CVCareerPreferencesSnapshot | null;
  evidence_items?: CVEvidenceItemSnapshot[];
  section_order?: string[];
  custom_sections?: Array<Record<string, any>>;
}

export interface CVVersionSummary {
  id: string;
  user_id: string;
  job_target_id?: string | null;
  job_target_title?: string | null;
  job_target_company?: string | null;
  name: string;
  status: CVVersionStatus;
  created_at: string;
  updated_at: string;
}

export interface CVVersion {
  id: string;
  user_id: string;
  job_target_id?: string | null;
  job_target_title?: string | null;
  job_target_company?: string | null;
  name: string;
  status: CVVersionStatus;
  content_snapshot: CVContentSnapshot;
  created_at: string;
  updated_at: string;
}

export interface CVVersionCreate {
  name: string;
  job_target_id?: string | null;
}

export interface CVVersionUpdate {
  name?: string;
  job_target_id?: string | null;
  status?: CVVersionStatus;
  content_snapshot?: CVContentSnapshot;
}

export interface CVVersionDuplicate {
  name?: string;
}

export interface CVVersionListResponse {
  items: CVVersionSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface CVVersionFilters {
  status?: CVVersionStatus;
  job_target_id?: string;
  search?: string;
  limit?: number;
  offset?: number;
}
