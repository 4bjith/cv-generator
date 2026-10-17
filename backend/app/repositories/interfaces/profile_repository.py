import uuid
from abc import ABC, abstractmethod
from typing import Optional, Union

from app.models.profile import (
    Achievement,
    CandidateLanguage,
    CandidateLink,
    CandidateProfile,
    CandidateSkill,
    CareerPreferences,
    Certification,
    EducationRecord,
    Project,
    WorkExperience,
)


class IProfileRepository(ABC):
    """Abstract repository interface for Candidate Profile persistence operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> Optional[CandidateProfile]:
        """Retrieve full candidate profile by owning user_id with all eager-loaded relations."""
        pass

    @abstractmethod
    async def get_by_id(self, profile_id: Union[uuid.UUID, str]) -> Optional[CandidateProfile]:
        """Retrieve full candidate profile by profile primary key."""
        pass

    @abstractmethod
    async def create_profile(self, profile: CandidateProfile) -> CandidateProfile:
        """Persist a new candidate profile."""
        pass

    @abstractmethod
    async def update_profile(self, profile: CandidateProfile) -> CandidateProfile:
        """Update an existing candidate profile."""
        pass

    @abstractmethod
    async def delete_profile(self, profile: CandidateProfile) -> None:
        """Delete candidate profile and cascade children."""
        pass

    # --- Links ---
    @abstractmethod
    async def create_link(self, link: CandidateLink) -> CandidateLink:
        pass

    @abstractmethod
    async def get_link(self, profile_id: uuid.UUID, link_id: uuid.UUID) -> Optional[CandidateLink]:
        pass

    @abstractmethod
    async def update_link(self, link: CandidateLink) -> CandidateLink:
        pass

    @abstractmethod
    async def delete_link(self, link: CandidateLink) -> None:
        pass

    # --- Experiences ---
    @abstractmethod
    async def create_experience(self, experience: WorkExperience) -> WorkExperience:
        pass

    @abstractmethod
    async def get_experience(self, profile_id: uuid.UUID, experience_id: uuid.UUID) -> Optional[WorkExperience]:
        pass

    @abstractmethod
    async def update_experience(self, experience: WorkExperience) -> WorkExperience:
        pass

    @abstractmethod
    async def delete_experience(self, experience: WorkExperience) -> None:
        pass

    # --- Education ---
    @abstractmethod
    async def create_education(self, education: EducationRecord) -> EducationRecord:
        pass

    @abstractmethod
    async def get_education(self, profile_id: uuid.UUID, education_id: uuid.UUID) -> Optional[EducationRecord]:
        pass

    @abstractmethod
    async def update_education(self, education: EducationRecord) -> EducationRecord:
        pass

    @abstractmethod
    async def delete_education(self, education: EducationRecord) -> None:
        pass

    # --- Skills ---
    @abstractmethod
    async def create_skill(self, skill: CandidateSkill) -> CandidateSkill:
        pass

    @abstractmethod
    async def get_skill(self, profile_id: uuid.UUID, skill_id: uuid.UUID) -> Optional[CandidateSkill]:
        pass

    @abstractmethod
    async def get_skill_by_name(self, profile_id: uuid.UUID, name: str) -> Optional[CandidateSkill]:
        pass

    @abstractmethod
    async def update_skill(self, skill: CandidateSkill) -> CandidateSkill:
        pass

    @abstractmethod
    async def delete_skill(self, skill: CandidateSkill) -> None:
        pass

    # --- Projects ---
    @abstractmethod
    async def create_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def get_project(self, profile_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Project]:
        pass

    @abstractmethod
    async def update_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def delete_project(self, project: Project) -> None:
        pass

    # --- Certifications ---
    @abstractmethod
    async def create_certification(self, cert: Certification) -> Certification:
        pass

    @abstractmethod
    async def get_certification(self, profile_id: uuid.UUID, cert_id: uuid.UUID) -> Optional[Certification]:
        pass

    @abstractmethod
    async def update_certification(self, cert: Certification) -> Certification:
        pass

    @abstractmethod
    async def delete_certification(self, cert: Certification) -> None:
        pass

    # --- Achievements ---
    @abstractmethod
    async def create_achievement(self, achievement: Achievement) -> Achievement:
        pass

    @abstractmethod
    async def get_achievement(self, profile_id: uuid.UUID, achievement_id: uuid.UUID) -> Optional[Achievement]:
        pass

    @abstractmethod
    async def update_achievement(self, achievement: Achievement) -> Achievement:
        pass

    @abstractmethod
    async def delete_achievement(self, achievement: Achievement) -> None:
        pass

    # --- Languages ---
    @abstractmethod
    async def create_language(self, language: CandidateLanguage) -> CandidateLanguage:
        pass

    @abstractmethod
    async def get_language(self, profile_id: uuid.UUID, lang_id: uuid.UUID) -> Optional[CandidateLanguage]:
        pass

    @abstractmethod
    async def update_language(self, language: CandidateLanguage) -> CandidateLanguage:
        pass

    @abstractmethod
    async def delete_language(self, language: CandidateLanguage) -> None:
        pass

    # --- Career Preferences ---
    @abstractmethod
    async def get_preferences(self, profile_id: uuid.UUID) -> Optional[CareerPreferences]:
        pass

    @abstractmethod
    async def save_preferences(self, preferences: CareerPreferences) -> CareerPreferences:
        pass

    # --- Evidence ---
    @abstractmethod
    async def create_evidence(self, evidence: "EvidenceItem") -> "EvidenceItem":
        pass

    @abstractmethod
    async def get_evidence(self, profile_id: uuid.UUID, evidence_id: uuid.UUID) -> Optional["EvidenceItem"]:
        pass

    @abstractmethod
    async def list_evidence(self, profile_id: uuid.UUID) -> List["EvidenceItem"]:
        pass

    @abstractmethod
    async def update_evidence(self, evidence: "EvidenceItem") -> "EvidenceItem":
        pass

    @abstractmethod
    async def delete_evidence(self, evidence: "EvidenceItem") -> None:
        pass

    @abstractmethod
    async def create_evidence_association(self, association: "EvidenceAssociation") -> "EvidenceAssociation":
        pass

    @abstractmethod
    async def delete_evidence_association(self, evidence_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_evidence_associations_for_profile(self, profile_id: uuid.UUID) -> List["EvidenceAssociation"]:
        pass

    # --- Skill Relationships ---
    @abstractmethod
    async def link_skill_experience(self, skill_id: uuid.UUID, experience_id: uuid.UUID) -> "SkillExperienceAssociation":
        pass

    @abstractmethod
    async def unlink_skill_experience(self, skill_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def link_skill_project(self, skill_id: uuid.UUID, project_id: uuid.UUID) -> "SkillProjectAssociation":
        pass

    @abstractmethod
    async def unlink_skill_project(self, skill_id: uuid.UUID, project_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def link_skill_certification(self, skill_id: uuid.UUID, certification_id: uuid.UUID) -> "SkillCertificationAssociation":
        pass

    @abstractmethod
    async def unlink_skill_certification(self, skill_id: uuid.UUID, certification_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def link_skill_achievement(self, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> "SkillAchievementAssociation":
        pass

    @abstractmethod
    async def unlink_skill_achievement(self, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def sync_skill_relationships(
        self,
        skill_id: uuid.UUID,
        experience_ids: Optional[List[uuid.UUID]] = None,
        project_ids: Optional[List[uuid.UUID]] = None,
        certification_ids: Optional[List[uuid.UUID]] = None,
        achievement_ids: Optional[List[uuid.UUID]] = None,
    ) -> None:
        pass

