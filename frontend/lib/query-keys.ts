/**
 * Centralized Query Keys for TanStack Query.
 */
export const authKeys = {
  all: ["auth"] as const,
  currentUser: () => [...authKeys.all, "currentUser"] as const,
};

export const profileKeys = {
  all: ["profile"] as const,
  current: () => [...profileKeys.all, "current"] as const,
  strength: () => [...profileKeys.all, "strength"] as const,
  preferences: () => [...profileKeys.all, "preferences"] as const,
  evidence: () => [...profileKeys.all, "evidence"] as const,
  evidenceDetail: (id: string) => [...profileKeys.evidence(), id] as const,
};

export const jobKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobKeys.all, "list"] as const,
  list: (filters?: Record<string, any>) => [...jobKeys.lists(), filters || {}] as const,
  details: () => [...jobKeys.all, "detail"] as const,
  detail: (id: string) => [...jobKeys.details(), id] as const,
  analyses: () => [...jobKeys.all, "analysis"] as const,
  analysis: (id: string) => [...jobKeys.analyses(), id] as const,
  clarifications: (id: string) => [...jobKeys.detail(id), "clarifications"] as const,
  versions: (id: string) => [...jobKeys.detail(id), "versions"] as const,
};

export const cvKeys = {
  all: ["cv"] as const,
  lists: () => [...cvKeys.all, "list"] as const,
  list: (filters?: Record<string, any>) => [...cvKeys.lists(), filters || {}] as const,
  details: () => [...cvKeys.all, "detail"] as const,
  detail: (id: string) => [...cvKeys.details(), id] as const,
};export const atsKeys = {
  all: ["ats"] as const,
  analysis: (versionId?: string, jobId?: string) =>
    [...atsKeys.all, "analysis", versionId || "", jobId || ""] as const,
};

export const coverLetterKeys = {
  all: ["coverLetters"] as const,
  lists: () => [...coverLetterKeys.all, "list"] as const,
  list: (filters?: Record<string, any>) =>
    [...coverLetterKeys.lists(), filters || {}] as const,
  details: () => [...coverLetterKeys.all, "detail"] as const,
  detail: (id: string) => [...coverLetterKeys.details(), id] as const,
};

