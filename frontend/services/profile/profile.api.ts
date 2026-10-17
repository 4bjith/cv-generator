import { apiClient } from "@/lib/api/axios";
import {
  AchievementCreatePayload,
  AchievementRecord,
  AchievementUpdatePayload,
  CandidateLanguage,
  CandidateLink,
  CandidateProfileCreatePayload,
  CandidateProfileData,
  CandidateProfileUpdatePayload,
  CandidateSkill,
  CareerPreferences,
  CareerPreferencesUpdatePayload,
  Certification,
  CertificationCreatePayload,
  CertificationUpdatePayload,
  EducationCreatePayload,
  EducationRecord,
  EducationUpdatePayload,
  EvidenceAssociation,
  EvidenceAssociationCreatePayload,
  EvidenceCreatePayload,
  EvidenceItem,
  EvidenceUpdatePayload,
  LanguageCreatePayload,
  LanguageUpdatePayload,
  LinkCreatePayload,
  LinkUpdatePayload,
  ProfileStrength,
  ProjectCreatePayload,
  ProjectRecord,
  ProjectUpdatePayload,
  SkillCreatePayload,
  SkillRelationshipsUpdatePayload,
  SkillUpdatePayload,
  WorkExperience,
  WorkExperienceCreatePayload,
  WorkExperienceUpdatePayload,
} from "@/types/profile";

/**
 * Candidate Profile API Service.
 * Encapsulates all profile and master career data operations with the backend.
 */
export const profileApi = {
  // ==========================================
  // Root Profile
  // ==========================================

  async getProfile(): Promise<CandidateProfileData> {
    const response = await apiClient.get<CandidateProfileData>("/profile");
    return response.data;
  },

  async createProfile(payload: CandidateProfileCreatePayload): Promise<CandidateProfileData> {
    const response = await apiClient.post<CandidateProfileData>("/profile", payload);
    return response.data;
  },

  async updateProfile(payload: CandidateProfileUpdatePayload): Promise<CandidateProfileData> {
    const response = await apiClient.patch<CandidateProfileData>("/profile", payload);
    return response.data;
  },

  async deleteProfile(): Promise<void> {
    await apiClient.delete("/profile");
  },

  async getStrength(): Promise<ProfileStrength> {
    const response = await apiClient.get<ProfileStrength>("/profile/strength");
    return response.data;
  },

  // ==========================================
  // Links
  // ==========================================

  async addLink(payload: LinkCreatePayload): Promise<CandidateLink> {
    const response = await apiClient.post<CandidateLink>("/profile/links", payload);
    return response.data;
  },

  async updateLink(linkId: string, payload: LinkUpdatePayload): Promise<CandidateLink> {
    const response = await apiClient.patch<CandidateLink>(`/profile/links/${linkId}`, payload);
    return response.data;
  },

  async deleteLink(linkId: string): Promise<void> {
    await apiClient.delete(`/profile/links/${linkId}`);
  },

  // ==========================================
  // Work Experience
  // ==========================================

  async addExperience(payload: WorkExperienceCreatePayload): Promise<WorkExperience> {
    const response = await apiClient.post<WorkExperience>("/profile/experience", payload);
    return response.data;
  },

  async updateExperience(experienceId: string, payload: WorkExperienceUpdatePayload): Promise<WorkExperience> {
    const response = await apiClient.patch<WorkExperience>(`/profile/experience/${experienceId}`, payload);
    return response.data;
  },

  async deleteExperience(experienceId: string): Promise<void> {
    await apiClient.delete(`/profile/experience/${experienceId}`);
  },

  // ==========================================
  // Education
  // ==========================================

  async addEducation(payload: EducationCreatePayload): Promise<EducationRecord> {
    const response = await apiClient.post<EducationRecord>("/profile/education", payload);
    return response.data;
  },

  async updateEducation(educationId: string, payload: EducationUpdatePayload): Promise<EducationRecord> {
    const response = await apiClient.patch<EducationRecord>(`/profile/education/${educationId}`, payload);
    return response.data;
  },

  async deleteEducation(educationId: string): Promise<void> {
    await apiClient.delete(`/profile/education/${educationId}`);
  },

  // ==========================================
  // Skills & Relationships
  // ==========================================

  async addSkill(payload: SkillCreatePayload): Promise<CandidateSkill> {
    const response = await apiClient.post<CandidateSkill>("/profile/skills", payload);
    return response.data;
  },

  async updateSkill(skillId: string, payload: SkillUpdatePayload): Promise<CandidateSkill> {
    const response = await apiClient.patch<CandidateSkill>(`/profile/skills/${skillId}`, payload);
    return response.data;
  },

  async deleteSkill(skillId: string): Promise<void> {
    await apiClient.delete(`/profile/skills/${skillId}`);
  },

  async syncSkillRelationships(
    skillId: string,
    payload: SkillRelationshipsUpdatePayload
  ): Promise<CandidateSkill> {
    const response = await apiClient.put<CandidateSkill>(`/profile/skills/${skillId}/relationships`, payload);
    return response.data;
  },

  async linkSkillExperience(skillId: string, experienceId: string): Promise<void> {
    await apiClient.post(`/profile/skills/${skillId}/experiences/${experienceId}`);
  },

  async unlinkSkillExperience(skillId: string, experienceId: string): Promise<void> {
    await apiClient.delete(`/profile/skills/${skillId}/experiences/${experienceId}`);
  },

  async linkSkillProject(skillId: string, projectId: string): Promise<void> {
    await apiClient.post(`/profile/skills/${skillId}/projects/${projectId}`);
  },

  async unlinkSkillProject(skillId: string, projectId: string): Promise<void> {
    await apiClient.delete(`/profile/skills/${skillId}/projects/${projectId}`);
  },

  // ==========================================
  // Projects
  // ==========================================

  async addProject(payload: ProjectCreatePayload): Promise<ProjectRecord> {
    const response = await apiClient.post<ProjectRecord>("/profile/projects", payload);
    return response.data;
  },

  async updateProject(projectId: string, payload: ProjectUpdatePayload): Promise<ProjectRecord> {
    const response = await apiClient.patch<ProjectRecord>(`/profile/projects/${projectId}`, payload);
    return response.data;
  },

  async deleteProject(projectId: string): Promise<void> {
    await apiClient.delete(`/profile/projects/${projectId}`);
  },

  // ==========================================
  // Certifications
  // ==========================================

  async addCertification(payload: CertificationCreatePayload): Promise<Certification> {
    const response = await apiClient.post<Certification>("/profile/certifications", payload);
    return response.data;
  },

  async updateCertification(certId: string, payload: CertificationUpdatePayload): Promise<Certification> {
    const response = await apiClient.patch<Certification>(`/profile/certifications/${certId}`, payload);
    return response.data;
  },

  async deleteCertification(certId: string): Promise<void> {
    await apiClient.delete(`/profile/certifications/${certId}`);
  },

  // ==========================================
  // Achievements
  // ==========================================

  async addAchievement(payload: AchievementCreatePayload): Promise<AchievementRecord> {
    const response = await apiClient.post<AchievementRecord>("/profile/achievements", payload);
    return response.data;
  },

  async updateAchievement(achievementId: string, payload: AchievementUpdatePayload): Promise<AchievementRecord> {
    const response = await apiClient.patch<AchievementRecord>(`/profile/achievements/${achievementId}`, payload);
    return response.data;
  },

  async deleteAchievement(achievementId: string): Promise<void> {
    await apiClient.delete(`/profile/achievements/${achievementId}`);
  },

  // ==========================================
  // Languages
  // ==========================================

  async addLanguage(payload: LanguageCreatePayload): Promise<CandidateLanguage> {
    const response = await apiClient.post<CandidateLanguage>("/profile/languages", payload);
    return response.data;
  },

  async updateLanguage(langId: string, payload: LanguageUpdatePayload): Promise<CandidateLanguage> {
    const response = await apiClient.patch<CandidateLanguage>(`/profile/languages/${langId}`, payload);
    return response.data;
  },

  async deleteLanguage(langId: string): Promise<void> {
    await apiClient.delete(`/profile/languages/${langId}`);
  },

  // ==========================================
  // Career Preferences
  // ==========================================

  async getCareerPreferences(): Promise<CareerPreferences | null> {
    const response = await apiClient.get<CareerPreferences | null>("/profile/preferences");
    return response.data;
  },

  async updateCareerPreferences(payload: CareerPreferencesUpdatePayload): Promise<CareerPreferences> {
    const response = await apiClient.put<CareerPreferences>("/profile/preferences", payload);
    return response.data;
  },

  // ==========================================
  // Evidence & Provenance (Phase 1.1)
  // ==========================================

  async listEvidence(): Promise<EvidenceItem[]> {
    const response = await apiClient.get<EvidenceItem[]>("/profile/evidence");
    return response.data;
  },

  async getEvidence(evidenceId: string): Promise<EvidenceItem> {
    const response = await apiClient.get<EvidenceItem>(`/profile/evidence/${evidenceId}`);
    return response.data;
  },

  async createEvidence(payload: EvidenceCreatePayload): Promise<EvidenceItem> {
    const response = await apiClient.post<EvidenceItem>("/profile/evidence", payload);
    return response.data;
  },

  async updateEvidence(evidenceId: string, payload: EvidenceUpdatePayload): Promise<EvidenceItem> {
    const response = await apiClient.patch<EvidenceItem>(`/profile/evidence/${evidenceId}`, payload);
    return response.data;
  },

  async deleteEvidence(evidenceId: string): Promise<void> {
    await apiClient.delete(`/profile/evidence/${evidenceId}`);
  },

  async addEvidenceAssociation(
    evidenceId: string,
    payload: EvidenceAssociationCreatePayload
  ): Promise<EvidenceAssociation> {
    const response = await apiClient.post<EvidenceAssociation>(
      `/profile/evidence/${evidenceId}/associations`,
      payload
    );
    return response.data;
  },

  async deleteEvidenceAssociation(
    evidenceId: string,
    entityType: string,
    entityId: string
  ): Promise<void> {
    await apiClient.delete(`/profile/evidence/${evidenceId}/associations/${entityType}/${entityId}`);
  },
};
