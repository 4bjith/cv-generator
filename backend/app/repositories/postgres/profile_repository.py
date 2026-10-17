import uuid
from typing import List, Optional, Union
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import (
    Achievement,
    CandidateLanguage,
    CandidateLink,
    CandidateProfile,
    CandidateSkill,
    CareerPreferences,
    Certification,
    EducationRecord,
    EvidenceAssociation,
    EvidenceItem,
    Project,
    SkillAchievementAssociation,
    SkillCertificationAssociation,
    SkillExperienceAssociation,
    SkillProjectAssociation,
    WorkExperience,
)
from app.repositories.interfaces.profile_repository import IProfileRepository


class PostgresProfileRepository(IProfileRepository):
    """PostgreSQL / SQLAlchemy implementation of IProfileRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _eager_options(self):
        return [
            selectinload(CandidateProfile.links),
            selectinload(CandidateProfile.experiences),
            selectinload(CandidateProfile.education),
            selectinload(CandidateProfile.skills).selectinload(CandidateSkill.experience_associations),
            selectinload(CandidateProfile.skills).selectinload(CandidateSkill.project_associations),
            selectinload(CandidateProfile.skills).selectinload(CandidateSkill.certification_associations),
            selectinload(CandidateProfile.skills).selectinload(CandidateSkill.achievement_associations),
            selectinload(CandidateProfile.projects),
            selectinload(CandidateProfile.certifications),
            selectinload(CandidateProfile.achievements),
            selectinload(CandidateProfile.languages),
            selectinload(CandidateProfile.career_preferences),
            selectinload(CandidateProfile.evidence_items).selectinload(EvidenceItem.associations),
        ]


    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> Optional[CandidateProfile]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        stmt = (
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .options(*self._eager_options())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, profile_id: Union[uuid.UUID, str]) -> Optional[CandidateProfile]:
        if isinstance(profile_id, str):
            try:
                profile_id = uuid.UUID(profile_id)
            except ValueError:
                return None

        stmt = (
            select(CandidateProfile)
            .where(CandidateProfile.id == profile_id)
            .options(*self._eager_options())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_profile(self, profile: CandidateProfile) -> CandidateProfile:
        self.session.add(profile)
        await self.session.flush()
        # Return full profile with eager relationships
        return await self.get_by_id(profile.id) or profile

    async def update_profile(self, profile: CandidateProfile) -> CandidateProfile:
        self.session.add(profile)
        await self.session.flush()
        return await self.get_by_id(profile.id) or profile

    async def delete_profile(self, profile: CandidateProfile) -> None:
        await self.session.delete(profile)
        await self.session.flush()

    # --- Links ---
    async def create_link(self, link: CandidateLink) -> CandidateLink:
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_link(self, profile_id: uuid.UUID, link_id: uuid.UUID) -> Optional[CandidateLink]:
        stmt = select(CandidateLink).where(
            CandidateLink.profile_id == profile_id,
            CandidateLink.id == link_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_link(self, link: CandidateLink) -> CandidateLink:
        self.session.add(link)
        await self.session.flush()
        return link

    async def delete_link(self, link: CandidateLink) -> None:
        await self.session.delete(link)
        await self.session.flush()

    # --- Experiences ---
    async def create_experience(self, experience: WorkExperience) -> WorkExperience:
        self.session.add(experience)
        await self.session.flush()
        return experience

    async def get_experience(self, profile_id: uuid.UUID, experience_id: uuid.UUID) -> Optional[WorkExperience]:
        stmt = select(WorkExperience).where(
            WorkExperience.profile_id == profile_id,
            WorkExperience.id == experience_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_experience(self, experience: WorkExperience) -> WorkExperience:
        self.session.add(experience)
        await self.session.flush()
        return experience

    async def delete_experience(self, experience: WorkExperience) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "experience",
                EvidenceAssociation.entity_id == experience.id,
            )
        )
        await self.session.delete(experience)
        await self.session.flush()

    # --- Education ---
    async def create_education(self, education: EducationRecord) -> EducationRecord:
        self.session.add(education)
        await self.session.flush()
        return education

    async def get_education(self, profile_id: uuid.UUID, education_id: uuid.UUID) -> Optional[EducationRecord]:
        stmt = select(EducationRecord).where(
            EducationRecord.profile_id == profile_id,
            EducationRecord.id == education_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_education(self, education: EducationRecord) -> EducationRecord:
        self.session.add(education)
        await self.session.flush()
        return education

    async def delete_education(self, education: EducationRecord) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "education",
                EvidenceAssociation.entity_id == education.id,
            )
        )
        await self.session.delete(education)
        await self.session.flush()

    # --- Skills ---
    async def create_skill(self, skill: CandidateSkill) -> CandidateSkill:
        self.session.add(skill)
        await self.session.flush()
        return await self.get_skill(skill.profile_id, skill.id) or skill

    async def get_skill(self, profile_id: uuid.UUID, skill_id: uuid.UUID) -> Optional[CandidateSkill]:
        stmt = (
            select(CandidateSkill)
            .where(
                CandidateSkill.profile_id == profile_id,
                CandidateSkill.id == skill_id,
            )
            .options(
                selectinload(CandidateSkill.experience_associations),
                selectinload(CandidateSkill.project_associations),
                selectinload(CandidateSkill.certification_associations),
                selectinload(CandidateSkill.achievement_associations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_skill_by_name(self, profile_id: uuid.UUID, name: str) -> Optional[CandidateSkill]:
        stmt = (
            select(CandidateSkill)
            .where(
                CandidateSkill.profile_id == profile_id,
                func.lower(CandidateSkill.name) == name.strip().lower(),
            )
            .options(
                selectinload(CandidateSkill.experience_associations),
                selectinload(CandidateSkill.project_associations),
                selectinload(CandidateSkill.certification_associations),
                selectinload(CandidateSkill.achievement_associations),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_skill(self, skill: CandidateSkill) -> CandidateSkill:
        self.session.add(skill)
        await self.session.flush()
        return await self.get_skill(skill.profile_id, skill.id) or skill

    async def delete_skill(self, skill: CandidateSkill) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "skill",
                EvidenceAssociation.entity_id == skill.id,
            )
        )
        await self.session.delete(skill)
        await self.session.flush()

    # --- Projects ---
    async def create_project(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_project(self, profile_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Project]:
        stmt = select(Project).where(
            Project.profile_id == profile_id,
            Project.id == project_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_project(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def delete_project(self, project: Project) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "project",
                EvidenceAssociation.entity_id == project.id,
            )
        )
        await self.session.delete(project)
        await self.session.flush()

    # --- Certifications ---
    async def create_certification(self, cert: Certification) -> Certification:
        self.session.add(cert)
        await self.session.flush()
        return cert

    async def get_certification(self, profile_id: uuid.UUID, cert_id: uuid.UUID) -> Optional[Certification]:
        stmt = select(Certification).where(
            Certification.profile_id == profile_id,
            Certification.id == cert_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_certification(self, cert: Certification) -> Certification:
        self.session.add(cert)
        await self.session.flush()
        return cert

    async def delete_certification(self, cert: Certification) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "certification",
                EvidenceAssociation.entity_id == cert.id,
            )
        )
        await self.session.delete(cert)
        await self.session.flush()

    # --- Achievements ---
    async def create_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.flush()
        return achievement

    async def get_achievement(self, profile_id: uuid.UUID, achievement_id: uuid.UUID) -> Optional[Achievement]:
        stmt = select(Achievement).where(
            Achievement.profile_id == profile_id,
            Achievement.id == achievement_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.flush()
        return achievement

    async def delete_achievement(self, achievement: Achievement) -> None:
        await self.session.execute(
            delete(EvidenceAssociation).where(
                EvidenceAssociation.entity_type == "achievement",
                EvidenceAssociation.entity_id == achievement.id,
            )
        )
        await self.session.delete(achievement)
        await self.session.flush()

    # --- Languages ---
    async def create_language(self, language: CandidateLanguage) -> CandidateLanguage:
        self.session.add(language)
        await self.session.flush()
        return language

    async def get_language(self, profile_id: uuid.UUID, lang_id: uuid.UUID) -> Optional[CandidateLanguage]:
        stmt = select(CandidateLanguage).where(
            CandidateLanguage.profile_id == profile_id,
            CandidateLanguage.id == lang_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_language(self, language: CandidateLanguage) -> CandidateLanguage:
        self.session.add(language)
        await self.session.flush()
        return language

    async def delete_language(self, language: CandidateLanguage) -> None:
        await self.session.delete(language)
        await self.session.flush()

    # --- Career Preferences ---
    async def get_preferences(self, profile_id: uuid.UUID) -> Optional[CareerPreferences]:
        stmt = select(CareerPreferences).where(CareerPreferences.profile_id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def save_preferences(self, preferences: CareerPreferences) -> CareerPreferences:
        self.session.add(preferences)
        await self.session.flush()
        return preferences

    # --- Evidence ---
    async def create_evidence(self, evidence: EvidenceItem) -> EvidenceItem:
        self.session.add(evidence)
        await self.session.flush()
        return await self.get_evidence(evidence.profile_id, evidence.id) or evidence

    async def get_evidence(self, profile_id: uuid.UUID, evidence_id: uuid.UUID) -> Optional[EvidenceItem]:
        stmt = (
            select(EvidenceItem)
            .where(
                EvidenceItem.profile_id == profile_id,
                EvidenceItem.id == evidence_id,
            )
            .options(selectinload(EvidenceItem.associations))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_evidence(self, profile_id: uuid.UUID) -> List[EvidenceItem]:
        stmt = (
            select(EvidenceItem)
            .where(EvidenceItem.profile_id == profile_id)
            .options(selectinload(EvidenceItem.associations))
            .order_by(EvidenceItem.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_evidence(self, evidence: EvidenceItem) -> EvidenceItem:
        self.session.add(evidence)
        await self.session.flush()
        return await self.get_evidence(evidence.profile_id, evidence.id) or evidence

    async def delete_evidence(self, evidence: EvidenceItem) -> None:
        await self.session.delete(evidence)
        await self.session.flush()

    async def create_evidence_association(self, association: EvidenceAssociation) -> EvidenceAssociation:
        # Check if already exists to prevent duplicate insertion error
        stmt = select(EvidenceAssociation).where(
            EvidenceAssociation.evidence_id == association.evidence_id,
            EvidenceAssociation.entity_type == association.entity_type,
            EvidenceAssociation.entity_id == association.entity_id,
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        self.session.add(association)
        await self.session.flush()
        return association

    async def delete_evidence_association(self, evidence_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID) -> None:
        stmt = delete(EvidenceAssociation).where(
            EvidenceAssociation.evidence_id == evidence_id,
            EvidenceAssociation.entity_type == entity_type,
            EvidenceAssociation.entity_id == entity_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_evidence_associations_for_profile(self, profile_id: uuid.UUID) -> List[EvidenceAssociation]:
        stmt = (
            select(EvidenceAssociation)
            .join(EvidenceItem, EvidenceItem.id == EvidenceAssociation.evidence_id)
            .where(EvidenceItem.profile_id == profile_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Skill Relationships ---
    async def link_skill_experience(self, skill_id: uuid.UUID, experience_id: uuid.UUID) -> SkillExperienceAssociation:
        stmt = select(SkillExperienceAssociation).where(
            SkillExperienceAssociation.skill_id == skill_id,
            SkillExperienceAssociation.experience_id == experience_id,
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        assoc = SkillExperienceAssociation(skill_id=skill_id, experience_id=experience_id)
        self.session.add(assoc)
        await self.session.flush()
        return assoc

    async def unlink_skill_experience(self, skill_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        stmt = delete(SkillExperienceAssociation).where(
            SkillExperienceAssociation.skill_id == skill_id,
            SkillExperienceAssociation.experience_id == experience_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def link_skill_project(self, skill_id: uuid.UUID, project_id: uuid.UUID) -> SkillProjectAssociation:
        stmt = select(SkillProjectAssociation).where(
            SkillProjectAssociation.skill_id == skill_id,
            SkillProjectAssociation.project_id == project_id,
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        assoc = SkillProjectAssociation(skill_id=skill_id, project_id=project_id)
        self.session.add(assoc)
        await self.session.flush()
        return assoc

    async def unlink_skill_project(self, skill_id: uuid.UUID, project_id: uuid.UUID) -> None:
        stmt = delete(SkillProjectAssociation).where(
            SkillProjectAssociation.skill_id == skill_id,
            SkillProjectAssociation.project_id == project_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def link_skill_certification(self, skill_id: uuid.UUID, certification_id: uuid.UUID) -> SkillCertificationAssociation:
        stmt = select(SkillCertificationAssociation).where(
            SkillCertificationAssociation.skill_id == skill_id,
            SkillCertificationAssociation.certification_id == certification_id,
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        assoc = SkillCertificationAssociation(skill_id=skill_id, certification_id=certification_id)
        self.session.add(assoc)
        await self.session.flush()
        return assoc

    async def unlink_skill_certification(self, skill_id: uuid.UUID, certification_id: uuid.UUID) -> None:
        stmt = delete(SkillCertificationAssociation).where(
            SkillCertificationAssociation.skill_id == skill_id,
            SkillCertificationAssociation.certification_id == certification_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def link_skill_achievement(self, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> SkillAchievementAssociation:
        stmt = select(SkillAchievementAssociation).where(
            SkillAchievementAssociation.skill_id == skill_id,
            SkillAchievementAssociation.achievement_id == achievement_id,
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        assoc = SkillAchievementAssociation(skill_id=skill_id, achievement_id=achievement_id)
        self.session.add(assoc)
        await self.session.flush()
        return assoc

    async def unlink_skill_achievement(self, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> None:
        stmt = delete(SkillAchievementAssociation).where(
            SkillAchievementAssociation.skill_id == skill_id,
            SkillAchievementAssociation.achievement_id == achievement_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def sync_skill_relationships(
        self,
        skill_id: uuid.UUID,
        experience_ids: Optional[List[uuid.UUID]] = None,
        project_ids: Optional[List[uuid.UUID]] = None,
        certification_ids: Optional[List[uuid.UUID]] = None,
        achievement_ids: Optional[List[uuid.UUID]] = None,
    ) -> None:
        if experience_ids is not None:
            await self.session.execute(
                delete(SkillExperienceAssociation).where(SkillExperienceAssociation.skill_id == skill_id)
            )
            for exp_id in set(experience_ids):
                self.session.add(SkillExperienceAssociation(skill_id=skill_id, experience_id=exp_id))

        if project_ids is not None:
            await self.session.execute(
                delete(SkillProjectAssociation).where(SkillProjectAssociation.skill_id == skill_id)
            )
            for proj_id in set(project_ids):
                self.session.add(SkillProjectAssociation(skill_id=skill_id, project_id=proj_id))

        if certification_ids is not None:
            await self.session.execute(
                delete(SkillCertificationAssociation).where(SkillCertificationAssociation.skill_id == skill_id)
            )
            for cert_id in set(certification_ids):
                self.session.add(SkillCertificationAssociation(skill_id=skill_id, certification_id=cert_id))

        if achievement_ids is not None:
            await self.session.execute(
                delete(SkillAchievementAssociation).where(SkillAchievementAssociation.skill_id == skill_id)
            )
            for ach_id in set(achievement_ids):
                self.session.add(SkillAchievementAssociation(skill_id=skill_id, achievement_id=ach_id))

        await self.session.flush()

