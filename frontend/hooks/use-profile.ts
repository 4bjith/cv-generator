import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { profileKeys } from "@/lib/query-keys";
import { profileApi } from "@/services/profile/profile.api";
import {
  AchievementCreatePayload,
  AchievementUpdatePayload,
  CandidateProfileCreatePayload,
  CandidateProfileData,
  CandidateProfileUpdatePayload,
  CareerPreferencesUpdatePayload,
  CertificationCreatePayload,
  CertificationUpdatePayload,
  EducationCreatePayload,
  EducationUpdatePayload,
  LanguageCreatePayload,
  LanguageUpdatePayload,
  LinkCreatePayload,
  LinkUpdatePayload,
  ProjectCreatePayload,
  ProjectUpdatePayload,
  SkillCreatePayload,
  SkillUpdatePayload,
  WorkExperienceCreatePayload,
  WorkExperienceUpdatePayload,
} from "@/types/profile";
import { ApiClientError } from "@/lib/api/errors";

export function useCandidateProfile() {
  const query = useQuery<CandidateProfileData, ApiClientError>({
    queryKey: profileKeys.current(),
    queryFn: () => profileApi.getProfile(),
    retry: (failureCount, error) => {
      // Don't retry if the profile simply does not exist yet (404)
      if (error?.status === 404 || error?.code === "PROFILE_NOT_FOUND") {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const isProfileNotFound = query.error?.status === 404 || query.error?.code === "PROFILE_NOT_FOUND";

  return {
    ...query,
    profile: query.data ?? null,
    isProfileNotFound,
  };
}

export function useProfileStrength() {
  return useQuery({
    queryKey: profileKeys.strength(),
    queryFn: () => profileApi.getStrength(),
    staleTime: 1000 * 60 * 2,
  });
}

export function useCreateCandidateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CandidateProfileCreatePayload) => profileApi.createProfile(payload),
    onSuccess: (newProfile) => {
      queryClient.setQueryData(profileKeys.current(), newProfile);
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateCandidateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CandidateProfileUpdatePayload) => profileApi.updateProfile(payload),
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(profileKeys.current(), updatedProfile);
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteCandidateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => profileApi.deleteProfile(),
    onSuccess: () => {
      queryClient.setQueryData(profileKeys.current(), null);
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Links Mutations
// ==========================================

export function useAddLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LinkCreatePayload) => profileApi.addLink(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: LinkUpdatePayload }) =>
      profileApi.updateLink(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteLink(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Work Experience Mutations
// ==========================================

export function useAddExperience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorkExperienceCreatePayload) => profileApi.addExperience(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateExperience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkExperienceUpdatePayload }) =>
      profileApi.updateExperience(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteExperience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteExperience(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Education Mutations
// ==========================================

export function useAddEducation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: EducationCreatePayload) => profileApi.addEducation(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateEducation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: EducationUpdatePayload }) =>
      profileApi.updateEducation(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteEducation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteEducation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Skills Mutations
// ==========================================

export function useAddSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SkillCreatePayload) => profileApi.addSkill(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: SkillUpdatePayload }) =>
      profileApi.updateSkill(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteSkill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteSkill(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Projects Mutations
// ==========================================

export function useAddProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectCreatePayload) => profileApi.addProject(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ProjectUpdatePayload }) =>
      profileApi.updateProject(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Certifications Mutations
// ==========================================

export function useAddCertification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CertificationCreatePayload) => profileApi.addCertification(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateCertification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CertificationUpdatePayload }) =>
      profileApi.updateCertification(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteCertification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteCertification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Achievements Mutations
// ==========================================

export function useAddAchievement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AchievementCreatePayload) => profileApi.addAchievement(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateAchievement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: AchievementUpdatePayload }) =>
      profileApi.updateAchievement(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteAchievement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteAchievement(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Languages Mutations
// ==========================================

export function useAddLanguage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LanguageCreatePayload) => profileApi.addLanguage(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateLanguage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: LanguageUpdatePayload }) =>
      profileApi.updateLanguage(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteLanguage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteLanguage(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Career Preferences Mutations
// ==========================================

export function useUpdateCareerPreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CareerPreferencesUpdatePayload) =>
      profileApi.updateCareerPreferences(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Phase 1.1: Evidence Hooks & Mutations
// ==========================================

export function useEvidenceList() {
  return useQuery({
    queryKey: profileKeys.evidence(),
    queryFn: () => profileApi.listEvidence(),
    staleTime: 1000 * 60 * 3,
  });
}

export function useCreateEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: import("@/types/profile").EvidenceCreatePayload) =>
      profileApi.createEvidence(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUpdateEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: import("@/types/profile").EvidenceUpdatePayload;
    }) => profileApi.updateEvidence(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => profileApi.deleteEvidence(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useAddEvidenceAssociation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      payload,
    }: {
      evidenceId: string;
      payload: import("@/types/profile").EvidenceAssociationCreatePayload;
    }) => profileApi.addEvidenceAssociation(evidenceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useDeleteEvidenceAssociation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      evidenceId,
      entityType,
      entityId,
    }: {
      evidenceId: string;
      entityType: string;
      entityId: string;
    }) => profileApi.deleteEvidenceAssociation(evidenceId, entityType, entityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

// ==========================================
// Phase 1.1: Skill Relationship Mutations
// ==========================================

export function useSyncSkillRelationships() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      skillId,
      payload,
    }: {
      skillId: string;
      payload: import("@/types/profile").SkillRelationshipsUpdatePayload;
    }) => profileApi.syncSkillRelationships(skillId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useLinkSkillExperience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ skillId, experienceId }: { skillId: string; experienceId: string }) =>
      profileApi.linkSkillExperience(skillId, experienceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUnlinkSkillExperience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ skillId, experienceId }: { skillId: string; experienceId: string }) =>
      profileApi.unlinkSkillExperience(skillId, experienceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useLinkSkillProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ skillId, projectId }: { skillId: string; projectId: string }) =>
      profileApi.linkSkillProject(skillId, projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

export function useUnlinkSkillProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ skillId, projectId }: { skillId: string; projectId: string }) =>
      profileApi.unlinkSkillProject(skillId, projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
    },
  });
}

