export type CareerLevel =
  | "student"
  | "entry"
  | "junior"
  | "mid"
  | "senior"
  | "lead"
  | "manager"
  | "director"
  | "executive";

export type EmploymentType =
  | "full_time"
  | "part_time"
  | "contract"
  | "internship"
  | "freelance"
  | "temporary"
  | "volunteer"
  | "other";

export type SkillCategory =
  | "programming_language"
  | "frontend"
  | "backend"
  | "database"
  | "framework"
  | "library"
  | "cloud"
  | "devops"
  | "testing"
  | "ai_ml"
  | "design"
  | "tool"
  | "soft_skill"
  | "domain"
  | "other";

export type SkillProficiency = "beginner" | "intermediate" | "advanced" | "expert";

export type LanguageProficiency = "basic" | "conversational" | "professional" | "fluent" | "native";

export type RemotePreference = "remote" | "hybrid" | "onsite" | "flexible";

export type AvailabilityStatus = "actively_looking" | "open_to_opportunities" | "not_looking";

export type AchievementCategory =
  | "hackathon"
  | "award"
  | "competition"
  | "scholarship"
  | "open_source"
  | "publication"
  | "conference"
  | "leadership"
  | "community"
  | "other";

export type LinkType =
  | "github"
  | "linkedin"
  | "portfolio"
  | "website"
  | "behance"
  | "dribbble"
  | "stackoverflow"
  | "kaggle"
  | "medium"
  | "other";

export type ProvenanceType = "user_provided" | "ai_generated" | "ai_enhanced" | "imported";

export type EvidenceSourceType =
  | "link"
  | "document"
  | "repository"
  | "recommendation"
  | "metric_report"
  | "credential"
  | "other";

export type VerificationStatus = "unverified" | "verified" | "self_attested" | "third_party_confirmed";

// ==========================================
// Links
// ==========================================

export interface CandidateLink {
  id: string;
  profile_id: string;
  type: string;
  label: string;
  url: string;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface LinkCreatePayload {
  type: string;
  label: string;
  url: string;
  order_index?: number;
}

export interface LinkUpdatePayload {
  type?: string;
  label?: string;
  url?: string;
  order_index?: number;
}

// ==========================================
// Work Experience
// ==========================================

export interface ExperienceMetric {
  value: number | string;
  unit: string;
  description: string;
}

export interface WorkExperience {
  id: string;
  profile_id: string;
  company: string;
  position: string;
  employment_type: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string | null;
  responsibilities: string[];
  achievements: string[];
  technologies: string[];
  metrics: ExperienceMetric[];
  provenance: ProvenanceType;
  evidence_ids: string[];
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface WorkExperienceCreatePayload {
  company: string;
  position: string;
  employment_type?: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
  responsibilities?: string[];
  achievements?: string[];
  technologies?: string[];
  metrics?: ExperienceMetric[];
  provenance?: ProvenanceType;
  order_index?: number;
}

export interface WorkExperienceUpdatePayload {
  company?: string;
  position?: string;
  employment_type?: string;
  location?: string | null;
  start_date?: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
  responsibilities?: string[];
  achievements?: string[];
  technologies?: string[];
  metrics?: ExperienceMetric[];
  provenance?: ProvenanceType;
  order_index?: number;
}

// ==========================================
// Education
// ==========================================

export interface EducationRecord {
  id: string;
  profile_id: string;
  institution: string;
  degree: string;
  field_of_study?: string | null;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  description?: string | null;
  achievements: string[];
  provenance: ProvenanceType;
  evidence_ids: string[];
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface EducationCreatePayload {
  institution: string;
  degree: string;
  field_of_study?: string | null;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  description?: string | null;
  achievements?: string[];
  provenance?: ProvenanceType;
  order_index?: number;
}

export interface EducationUpdatePayload {
  institution?: string;
  degree?: string;
  field_of_study?: string | null;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  description?: string | null;
  achievements?: string[];
  provenance?: ProvenanceType;
  order_index?: number;
}

// ==========================================
// Skills & Relationships
// ==========================================

export interface CandidateSkill {
  id: string;
  profile_id: string;
  name: string;
  category?: string | null;
  proficiency?: string | null;
  years_of_experience?: number | null;
  last_used?: string | null;
  evidence_references: string[];
  provenance: ProvenanceType;
  experience_ids: string[];
  project_ids: string[];
  certification_ids: string[];
  achievement_ids: string[];
  evidence_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface SkillCreatePayload {
  name: string;
  category?: string | null;
  proficiency?: string | null;
  years_of_experience?: number | null;
  last_used?: string | null;
  evidence_references?: string[];
  provenance?: ProvenanceType;
  experience_ids?: string[];
  project_ids?: string[];
  certification_ids?: string[];
  achievement_ids?: string[];
}

export interface SkillUpdatePayload {
  name?: string;
  category?: string | null;
  proficiency?: string | null;
  years_of_experience?: number | null;
  last_used?: string | null;
  evidence_references?: string[];
  provenance?: ProvenanceType;
  experience_ids?: string[];
  project_ids?: string[];
  certification_ids?: string[];
  achievement_ids?: string[];
}

export interface SkillRelationshipsUpdatePayload {
  experience_ids?: string[];
  project_ids?: string[];
  certification_ids?: string[];
  achievement_ids?: string[];
}

// ==========================================
// Projects
// ==========================================

export interface ProjectRecord {
  id: string;
  profile_id: string;
  name: string;
  role?: string | null;
  description?: string | null;
  problem?: string | null;
  solution?: string | null;
  responsibilities: string[];
  achievements: string[];
  technologies: string[];
  architecture?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  team_size?: number | null;
  live_url?: string | null;
  repository_url?: string | null;
  featured: boolean;
  provenance: ProvenanceType;
  evidence_ids: string[];
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreatePayload {
  name: string;
  role?: string | null;
  description?: string | null;
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
  provenance?: ProvenanceType;
  order_index?: number;
}

export interface ProjectUpdatePayload {
  name?: string;
  role?: string | null;
  description?: string | null;
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
  provenance?: ProvenanceType;
  order_index?: number;
}

// ==========================================
// Certifications
// ==========================================

export interface Certification {
  id: string;
  profile_id: string;
  name: string;
  issuer: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  skills: string[];
  provenance: ProvenanceType;
  evidence_ids: string[];
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface CertificationCreatePayload {
  name: string;
  issuer: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  skills?: string[];
  provenance?: ProvenanceType;
  order_index?: number;
}

export interface CertificationUpdatePayload {
  name?: string;
  issuer?: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  skills?: string[];
  provenance?: ProvenanceType;
  order_index?: number;
}

// ==========================================
// Achievements
// ==========================================

export interface AchievementRecord {
  id: string;
  profile_id: string;
  title: string;
  description?: string | null;
  date?: string | null;
  issuer?: string | null;
  category?: string | null;
  evidence_url?: string | null;
  provenance: ProvenanceType;
  evidence_ids: string[];
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface AchievementCreatePayload {
  title: string;
  description?: string | null;
  date?: string | null;
  issuer?: string | null;
  category?: string | null;
  evidence_url?: string | null;
  provenance?: ProvenanceType;
  order_index?: number;
}

export interface AchievementUpdatePayload {
  title?: string;
  description?: string | null;
  date?: string | null;
  issuer?: string | null;
  category?: string | null;
  evidence_url?: string | null;
  provenance?: ProvenanceType;
  order_index?: number;
}

// ==========================================
// Languages
// ==========================================

export interface CandidateLanguage {
  id: string;
  profile_id: string;
  name: string;
  proficiency: string;
  created_at: string;
  updated_at: string;
}

export interface LanguageCreatePayload {
  name: string;
  proficiency: string;
}

export interface LanguageUpdatePayload {
  name?: string;
  proficiency?: string;
}

// ==========================================
// Career Preferences
// ==========================================

export interface CareerPreferences {
  id: string;
  profile_id: string;
  target_roles: string[];
  target_industries: string[];
  preferred_locations: string[];
  remote_preference?: string | null;
  employment_types: string[];
  availability_status?: string | null;
  available_from?: string | null;
  notice_period_days?: number | null;
  created_at: string;
  updated_at: string;
}

export interface CareerPreferencesUpdatePayload {
  target_roles?: string[];
  target_industries?: string[];
  preferred_locations?: string[];
  remote_preference?: string | null;
  employment_types?: string[];
  availability_status?: string | null;
  available_from?: string | null;
  notice_period_days?: number | null;
}

// ==========================================
// Phase 1.1: Evidence Models
// ==========================================

export interface EvidenceAssociation {
  id: string;
  evidence_id: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
}

export interface EvidenceAssociationCreatePayload {
  entity_type: string;
  entity_id: string;
}

export interface EvidenceItem {
  id: string;
  profile_id: string;
  title: string;
  description?: string | null;
  source: string;
  source_type: EvidenceSourceType;
  url?: string | null;
  notes?: string | null;
  date?: string | null;
  verification_status: VerificationStatus;
  provenance: ProvenanceType;
  associations: EvidenceAssociation[];
  created_at: string;
  updated_at: string;
}

export interface EvidenceCreatePayload {
  title: string;
  description?: string | null;
  source: string;
  source_type?: EvidenceSourceType;
  url?: string | null;
  notes?: string | null;
  date?: string | null;
  verification_status?: VerificationStatus;
  provenance?: ProvenanceType;
  associated_entities?: EvidenceAssociationCreatePayload[];
}

export interface EvidenceUpdatePayload {
  title?: string;
  description?: string | null;
  source?: string;
  source_type?: EvidenceSourceType;
  url?: string | null;
  notes?: string | null;
  date?: string | null;
  verification_status?: VerificationStatus;
  provenance?: ProvenanceType;
}

// ==========================================
// Profile Strength & Quality Breakdown
// ==========================================

export interface ProfileQualityBreakdown {
  score: number;
  completeness: number;
  evidence_coverage: number;
  skill_validation: number;
  experience_quality: number;
  project_quality: number;
  achievement_quality: number;
  recommendations: string[];
}

export interface ProfileStrength {
  completion_percentage: number;
  sections_breakdown: Record<string, boolean>;
  completed_sections_count: number;
  total_sections_count: number;
  suggestions: string[];
  quality: ProfileQualityBreakdown;
}

// ==========================================
// Candidate Profile Master
// ==========================================

export interface CandidateProfileData {
  id: string;
  user_id: string;
  first_name: string;
  last_name?: string | null;
  preferred_name?: string | null;
  professional_headline?: string | null;
  profile_photo?: string | null;
  email?: string | null;
  phone?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  country_code?: string | null;
  primary_title?: string | null;
  secondary_titles: string[];
  career_level?: string | null;
  industry?: string | null;
  years_of_experience?: number | null;
  specializations: string[];
  base_summary?: string | null;
  created_at: string;
  updated_at: string;

  // Normalized collections
  links: CandidateLink[];
  experiences: WorkExperience[];
  education: EducationRecord[];
  skills: CandidateSkill[];
  projects: ProjectRecord[];
  certifications: Certification[];
  achievements: AchievementRecord[];
  languages: CandidateLanguage[];
  career_preferences?: CareerPreferences | null;
  evidence_items?: EvidenceItem[];
  strength?: ProfileStrength | null;
}

export interface CandidateProfileCreatePayload {
  first_name: string;
  last_name?: string | null;
  preferred_name?: string | null;
  professional_headline?: string | null;
  profile_photo?: string | null;
  email?: string | null;
  phone?: string | null;
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

export interface CandidateProfileUpdatePayload {
  first_name?: string;
  last_name?: string | null;
  preferred_name?: string | null;
  professional_headline?: string | null;
  profile_photo?: string | null;
  email?: string | null;
  phone?: string | null;
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
