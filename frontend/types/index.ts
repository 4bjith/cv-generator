export type AppView =
  | "landing"
  | "auth"
  | "onboarding"
  | "dashboard"
  | "profile"
  | "projects"
  | "add-job"
  | "job-analysis"
  | "matching"
  | "clarifications"
  | "cv-generation"
  | "cv-editor"
  | "ats-analysis"
  | "cover-email"
  | "interview"
  | "applications"
  | "application-detail"
  | "settings";

export type JobInputMode = "paste" | "upload" | "url";
export type MatchState = "strong" | "partial" | "weak" | "none" | "unknown";
export type ApplicationStatus =
  | "Saved"
  | "Applied"
  | "Screening"
  | "Interview"
  | "Technical Round"
  | "Final Round"
  | "Offer"
  | "Rejected"
  | "Withdrawn";

export interface CandidateProfile {
  name: string;
  role: string;
  location: string;
  email: string;
  phone: string;
  summary: string;
  yearsExperience: number;
  profileScore: number;
  linkedin: string;
  github: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  evidenceCount: number;
  confidence: number;
  status: "verified" | "review";
}

export interface Experience {
  id: string;
  company: string;
  role: string;
  start: string;
  end: string;
  location: string;
  description: string;
  highlights: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  stack: string[];
  stars: number;
  forks: number;
  lastUpdated: string;
  analyzed: boolean;
  repoUrl: string;
}

export interface Education {
  id: string;
  school: string;
  degree: string;
  period: string;
  detail: string;
}

export interface JobRequirement {
  id: string;
  name: string;
  type: "required" | "preferred";
  state: MatchState;
  evidence?: string;
  note?: string;
}

export interface Job {
  id: string;
  company: string;
  title: string;
  location: string;
  mode: string;
  salary: string;
  posted: string;
  description: string;
  requirements: JobRequirement[];
  matchScore: number;
}

export interface ClarificationQuestion {
  id: string;
  requirement: string;
  question: string;
  context: string;
  answer?: string;
  answered: boolean;
}

export interface CvSection {
  id: string;
  title: string;
  visible: boolean;
  content: string[];
}

export interface CvDocument {
  title: string;
  candidateName: string;
  targetRole: string;
  template: "signal" | "editorial" | "compact";
  sections: CvSection[];
  version: number;
  updatedAt: string;
}

export interface AtsCheck {
  id: string;
  label: string;
  detail: string;
  status: "pass" | "warning" | "review";
}

export interface AtsReport {
  score: number;
  keywordCoverage: number;
  checks: AtsCheck[];
  missingKeywords: string[];
}

export interface InterviewQuestion {
  id: string;
  category: "Technical" | "Project" | "Behavioral" | "Role-specific";
  question: string;
  why: string;
  evidence: string;
  prepared: boolean;
}

export interface Application {
  id: string;
  company: string;
  role: string;
  location: string;
  status: ApplicationStatus;
  matchScore: number;
  appliedDate: string;
  nextStep: string;
  nextDate?: string;
  initials: string;
  note: string;
}

export interface ToastMessage {
  id: number;
  type: "success" | "info" | "error";
  title: string;
  message: string;
}

export * from "./job";

