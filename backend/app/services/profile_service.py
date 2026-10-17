import uuid
from typing import Any, Dict, List, Optional, Set, Union
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
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
    WorkExperience,
)
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.profile import (
    AchievementCreate,
    AchievementResponse,
    AchievementUpdate,
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    CareerPreferencesResponse,
    CareerPreferencesUpdate,
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    EvidenceAssociationCreate,
    EvidenceAssociationResponse,
    EvidenceCreate,
    EvidenceResponse,
    EvidenceUpdate,
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
    LinkCreate,
    LinkResponse,
    LinkUpdate,
    ProfileQualityBreakdown,
    ProfileStrengthResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    SkillCreate,
    SkillRelationshipsUpdate,
    SkillResponse,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)

logger = get_logger("app.services.profile")


class ProfileService:
    """Service layer managing candidate master profile and career data."""

    def __init__(self, profile_repository: IProfileRepository) -> None:
        self.profile_repo = profile_repository

    # ==========================================
    # Profile Strength & Quality Calculation
    # ==========================================

    @staticmethod
    def calculate_strength(profile: CandidateProfile) -> ProfileStrengthResponse:
        """Deterministic profile quality scoring, section completion, and actionable recommendations."""
        sections = {
            "personal_info": bool(profile.first_name and (profile.professional_headline or profile.preferred_name)),
            "contact": bool(profile.email and (profile.phone or profile.city or (profile.links and len(profile.links) > 0))),
            "professional_identity": bool(profile.primary_title and profile.career_level),
            "summary": bool(profile.base_summary and len(profile.base_summary.strip()) >= 30),
            "experience": bool(profile.experiences and len(profile.experiences) >= 1),
            "skills": bool(profile.skills and len(profile.skills) >= 3),
            "projects": bool(profile.projects and len(profile.projects) >= 1),
            "education": bool(profile.education and len(profile.education) >= 1),
            "certifications": bool(profile.certifications and len(profile.certifications) >= 1),
            "achievements": bool(profile.achievements and len(profile.achievements) >= 1),
            "languages": bool(profile.languages and len(profile.languages) >= 1),
            "career_preferences": bool(
                profile.career_preferences and len(profile.career_preferences.target_roles or []) >= 1
            ),
        }

        # 1. Base Completeness Score (0-100)
        comp_score = 0
        if sections["personal_info"]:
            comp_score += 15
        elif profile.first_name:
            comp_score += 8

        if sections["contact"]:
            comp_score += 10
        elif profile.email:
            comp_score += 5

        if sections["professional_identity"]:
            comp_score += 10
        elif profile.primary_title or profile.career_level:
            comp_score += 5

        if sections["summary"]:
            comp_score += 10
        elif profile.base_summary:
            comp_score += 4

        if sections["experience"]:
            comp_score += 20
        if sections["skills"]:
            comp_score += 15
        elif profile.skills and len(profile.skills) > 0:
            comp_score += 5

        if sections["projects"]:
            comp_score += 10
        if sections["education"]:
            comp_score += 10

        completeness_pct = min(100, comp_score)
        completed_count = sum(1 for v in sections.values() if v)

        # 2. Evidence Coverage (0-100)
        # Collect evidence association counts across candidate profile facts
        evidence_items = profile.evidence_items or []
        associated_entity_ids: Set[str] = set()
        for item in evidence_items:
            for assoc in item.associations or []:
                associated_entity_ids.add(str(assoc.entity_id))

        total_provable_entities = (
            len(profile.experiences or [])
            + len(profile.projects or [])
            + len(profile.achievements or [])
            + len(profile.certifications or [])
        )

        proven_entities_count = 0
        for exp in profile.experiences or []:
            if str(exp.id) in associated_entity_ids:
                proven_entities_count += 1
        for proj in profile.projects or []:
            if str(proj.id) in associated_entity_ids:
                proven_entities_count += 1
        for ach in profile.achievements or []:
            if str(ach.id) in associated_entity_ids or ach.evidence_url:
                proven_entities_count += 1
        for cert in profile.certifications or []:
            if str(cert.id) in associated_entity_ids or cert.credential_url:
                proven_entities_count += 1

        if total_provable_entities > 0:
            evidence_coverage_pct = int(min(100, (proven_entities_count / total_provable_entities) * 100))
        elif len(evidence_items) > 0:
            evidence_coverage_pct = 50
        else:
            evidence_coverage_pct = 0

        # 3. Skill Validation (0-100)
        # Skills backed by linked experiences or projects
        skills = profile.skills or []
        validated_skills_count = 0
        for s in skills:
            has_exp = len(s.experience_associations or []) > 0
            has_proj = len(s.project_associations or []) > 0
            has_cert = len(s.certification_associations or []) > 0
            has_ach = len(s.achievement_associations or []) > 0
            if has_exp or has_proj or has_cert or has_ach or len(s.evidence_references or []) > 0:
                validated_skills_count += 1

        if len(skills) > 0:
            skill_validation_pct = int(min(100, (validated_skills_count / len(skills)) * 100))
        else:
            skill_validation_pct = 0

        # 4. Experience Quality (0-100)
        exp_quality = 0
        if profile.experiences and len(profile.experiences) > 0:
            exp_quality += 30
            has_metrics = any(len(e.metrics or []) > 0 for e in profile.experiences)
            has_resp = any(len(e.responsibilities or []) >= 2 for e in profile.experiences)
            has_tech = any(len(e.technologies or []) >= 2 for e in profile.experiences)
            has_evidence = any(str(e.id) in associated_entity_ids for e in profile.experiences)
            if has_metrics:
                exp_quality += 25
            if has_resp:
                exp_quality += 20
            if has_tech:
                exp_quality += 15
            if has_evidence:
                exp_quality += 10
        experience_quality_pct = min(100, exp_quality)

        # 5. Project Quality (0-100)
        proj_quality = 0
        if profile.projects and len(profile.projects) > 0:
            proj_quality += 30
            has_deep_desc = any(bool(p.problem or p.solution or p.architecture) for p in profile.projects)
            has_urls = any(bool(p.live_url or p.repository_url) for p in profile.projects)
            has_tech = any(len(p.technologies or []) >= 2 for p in profile.projects)
            has_evidence = any(str(p.id) in associated_entity_ids for p in profile.projects)
            if has_deep_desc:
                proj_quality += 25
            if has_urls:
                proj_quality += 20
            if has_tech:
                proj_quality += 15
            if has_evidence:
                proj_quality += 10
        project_quality_pct = min(100, proj_quality)

        # 6. Achievement Quality (0-100)
        ach_quality = 0
        if profile.achievements and len(profile.achievements) > 0:
            ach_quality += 35
            has_issuer = any(bool(a.issuer and a.date) for a in profile.achievements)
            has_evidence = any(bool(a.evidence_url or str(a.id) in associated_entity_ids) for a in profile.achievements)
            has_cat = any(bool(a.category) for a in profile.achievements)
            if has_issuer:
                ach_quality += 25
            if has_evidence:
                ach_quality += 25
            if has_cat:
                ach_quality += 15
        elif completeness_pct >= 50:
            ach_quality = 50
        achievement_quality_pct = min(100, ach_quality)

        # Composite Quality Score (0-100)
        # Weights: Completeness 30%, Evidence 25%, Skill Validation 20%, Experience 15%, Project 10%
        composite_score = int(
            (completeness_pct * 0.30)
            + (evidence_coverage_pct * 0.25)
            + (skill_validation_pct * 0.20)
            + (experience_quality_pct * 0.15)
            + (project_quality_pct * 0.10)
        )
        composite_score = min(100, max(0, composite_score))

        # Recommendations Generation
        recommendations: List[str] = []
        suggestions: List[str] = []

        if not sections["personal_info"]:
            suggestions.append("Add a professional headline describing your core specialization.")
        if not sections["summary"]:
            suggestions.append("Write a comprehensive base summary of at least 30 characters.")
        if not sections["experience"]:
            suggestions.append("Add at least one relevant work experience with measurable metrics.")
        if not sections["skills"]:
            suggestions.append(f"Add at least {max(1, 3 - len(profile.skills or []))} more skill(s) with categories.")
        if not sections["projects"]:
            suggestions.append("Add at least one key project detailing technical architecture and achievements.")
        if not sections["education"]:
            suggestions.append("Add your formal education or academic credentials.")
        if not sections["career_preferences"]:
            suggestions.append("Set your career preferences including target roles and remote preference.")

        # Quality-specific actionable recommendations
        if evidence_coverage_pct < 60 and total_provable_entities > 0:
            unproven_exps = [e for e in profile.experiences or [] if str(e.id) not in associated_entity_ids]
            if unproven_exps:
                recommendations.append(f"Attach evidence or verification links to '{unproven_exps[0].company}' ({unproven_exps[0].position}).")
            unproven_projs = [p for p in profile.projects or [] if str(p.id) not in associated_entity_ids and not p.live_url]
            if unproven_projs:
                recommendations.append(f"Add live URLs, repo links, or evidence to project '{unproven_projs[0].name}'.")
        
        if skill_validation_pct < 70 and len(skills) > 0:
            unlinked_skills = [
                s.name for s in skills
                if not (s.experience_associations or s.project_associations or s.certification_associations or s.achievement_associations)
            ]
            if unlinked_skills:
                preview = ", ".join(unlinked_skills[:2])
                recommendations.append(f"Connect skill(s) [{preview}] to the experiences or projects where you applied them.")

        if experience_quality_pct < 70 and profile.experiences:
            exps_no_metrics = [e for e in profile.experiences if not e.metrics]
            if exps_no_metrics:
                recommendations.append(f"Add quantifiable metrics (e.g., % improvement, revenue, scale) to your role at '{exps_no_metrics[0].company}'.")

        if project_quality_pct < 70 and profile.projects:
            projs_no_arch = [p for p in profile.projects if not (p.problem or p.solution or p.architecture)]
            if projs_no_arch:
                recommendations.append(f"Detail the problem, solution, and architecture for '{projs_no_arch[0].name}'.")

        if len(recommendations) == 0 and len(suggestions) > 0:
            recommendations.extend(suggestions[:3])

        quality_breakdown = ProfileQualityBreakdown(
            score=composite_score,
            completeness=completeness_pct,
            evidence_coverage=evidence_coverage_pct,
            skill_validation=skill_validation_pct,
            experience_quality=experience_quality_pct,
            project_quality=project_quality_pct,
            achievement_quality=achievement_quality_pct,
            recommendations=recommendations,
        )

        return ProfileStrengthResponse(
            completion_percentage=completeness_pct,
            sections_breakdown=sections,
            completed_sections_count=completed_count,
            total_sections_count=len(sections),
            suggestions=suggestions,
            score=composite_score,
            completeness=completeness_pct,
            evidence_coverage=evidence_coverage_pct,
            skill_validation=skill_validation_pct,
            experience_quality=experience_quality_pct,
            project_quality=project_quality_pct,
            achievement_quality=achievement_quality_pct,
            recommendations=recommendations,
            quality=quality_breakdown,
        )

    def _to_response(self, profile: CandidateProfile) -> CandidateProfileResponse:
        """Convert CandidateProfile model and eager relationships into CandidateProfileResponse."""
        strength = self.calculate_strength(profile)

        # Build entity -> evidence_ids mapping
        evidence_by_entity: Dict[str, List[uuid.UUID]] = {}
        for ev in profile.evidence_items or []:
            for assoc in ev.associations or []:
                key = f"{assoc.entity_type}:{assoc.entity_id}"
                if key not in evidence_by_entity:
                    evidence_by_entity[key] = []
                evidence_by_entity[key].append(ev.id)

        pref_response = None
        if profile.career_preferences:
            pref_response = CareerPreferencesResponse.model_validate(profile.career_preferences)

        # Map experiences
        experiences_resp: List[WorkExperienceResponse] = []
        for e in profile.experiences or []:
            ev_ids = evidence_by_entity.get(f"experience:{e.id}", [])
            resp = WorkExperienceResponse(
                id=e.id,
                profile_id=e.profile_id,
                company=e.company,
                position=e.position,
                employment_type=e.employment_type,
                location=e.location,
                start_date=e.start_date,
                end_date=e.end_date,
                is_current=e.is_current,
                description=e.description,
                responsibilities=e.responsibilities or [],
                achievements=e.achievements or [],
                technologies=e.technologies or [],
                metrics=e.metrics or [],
                provenance=getattr(e, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                order_index=e.order_index,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            experiences_resp.append(resp)

        # Map education
        education_resp: List[EducationResponse] = []
        for edu in profile.education or []:
            ev_ids = evidence_by_entity.get(f"education:{edu.id}", [])
            resp = EducationResponse(
                id=edu.id,
                profile_id=edu.profile_id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                location=edu.location,
                start_date=edu.start_date,
                end_date=edu.end_date,
                grade=edu.grade,
                description=edu.description,
                achievements=edu.achievements or [],
                provenance=getattr(edu, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                order_index=edu.order_index,
                created_at=edu.created_at,
                updated_at=edu.updated_at,
            )
            education_resp.append(resp)

        # Map skills
        skills_resp: List[SkillResponse] = []
        for s in profile.skills or []:
            ev_ids = evidence_by_entity.get(f"skill:{s.id}", [])
            exp_ids = [a.experience_id for a in s.experience_associations or []]
            proj_ids = [a.project_id for a in s.project_associations or []]
            cert_ids = [a.certification_id for a in s.certification_associations or []]
            ach_ids = [a.achievement_id for a in s.achievement_associations or []]
            resp = SkillResponse(
                id=s.id,
                profile_id=s.profile_id,
                name=s.name,
                category=s.category,
                proficiency=s.proficiency,
                years_of_experience=s.years_of_experience,
                last_used=s.last_used,
                evidence_references=s.evidence_references or [],
                provenance=getattr(s, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                experience_ids=exp_ids,
                project_ids=proj_ids,
                certification_ids=cert_ids,
                achievement_ids=ach_ids,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            skills_resp.append(resp)

        # Map projects
        projects_resp: List[ProjectResponse] = []
        for p in profile.projects or []:
            ev_ids = evidence_by_entity.get(f"project:{p.id}", [])
            resp = ProjectResponse(
                id=p.id,
                profile_id=p.profile_id,
                name=p.name,
                role=p.role,
                description=p.description,
                problem=p.problem,
                solution=p.solution,
                responsibilities=p.responsibilities or [],
                achievements=p.achievements or [],
                technologies=p.technologies or [],
                architecture=p.architecture,
                start_date=p.start_date,
                end_date=p.end_date,
                team_size=p.team_size,
                live_url=p.live_url,
                repository_url=p.repository_url,
                featured=p.featured,
                provenance=getattr(p, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                order_index=p.order_index,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            projects_resp.append(resp)

        # Map certifications
        certifications_resp: List[CertificationResponse] = []
        for c in profile.certifications or []:
            ev_ids = evidence_by_entity.get(f"certification:{c.id}", [])
            resp = CertificationResponse(
                id=c.id,
                profile_id=c.profile_id,
                name=c.name,
                issuer=c.issuer,
                issue_date=c.issue_date,
                expiration_date=c.expiration_date,
                credential_id=c.credential_id,
                credential_url=c.credential_url,
                skills=c.skills or [],
                provenance=getattr(c, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                order_index=c.order_index,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            certifications_resp.append(resp)

        # Map achievements
        achievements_resp: List[AchievementResponse] = []
        for a in profile.achievements or []:
            ev_ids = evidence_by_entity.get(f"achievement:{a.id}", [])
            resp = AchievementResponse(
                id=a.id,
                profile_id=a.profile_id,
                title=a.title,
                description=a.description,
                date=a.date,
                issuer=a.issuer,
                category=a.category,
                evidence_url=a.evidence_url,
                provenance=getattr(a, "provenance", "user_provided") or "user_provided",
                evidence_ids=ev_ids,
                order_index=a.order_index,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            achievements_resp.append(resp)

        # Map evidence items
        evidence_resp: List[EvidenceResponse] = []
        for ev in profile.evidence_items or []:
            assoc_resps = [
                EvidenceAssociationResponse(
                    id=assoc.id,
                    evidence_id=assoc.evidence_id,
                    entity_type=assoc.entity_type,
                    entity_id=assoc.entity_id,
                    created_at=assoc.created_at,
                )
                for assoc in ev.associations or []
            ]
            ev_item_resp = EvidenceResponse(
                id=ev.id,
                profile_id=ev.profile_id,
                title=ev.title,
                description=ev.description,
                source=ev.source,
                source_type=ev.source_type,
                url=ev.url,
                notes=ev.notes,
                date=ev.date,
                verification_status=ev.verification_status,
                provenance=ev.provenance,
                associations=assoc_resps,
                created_at=ev.created_at,
                updated_at=ev.updated_at,
            )
            evidence_resp.append(ev_item_resp)

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            preferred_name=profile.preferred_name,
            professional_headline=profile.professional_headline,
            profile_photo=profile.profile_photo,
            email=profile.email,
            phone=profile.phone,
            city=profile.city,
            state=profile.state,
            country=profile.country,
            country_code=profile.country_code,
            primary_title=profile.primary_title,
            secondary_titles=profile.secondary_titles or [],
            career_level=profile.career_level,
            industry=profile.industry,
            years_of_experience=profile.years_of_experience,
            specializations=profile.specializations or [],
            base_summary=profile.base_summary,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            links=[LinkResponse.model_validate(l) for l in profile.links or []],
            experiences=experiences_resp,
            education=education_resp,
            skills=skills_resp,
            projects=projects_resp,
            certifications=certifications_resp,
            achievements=achievements_resp,
            languages=[LanguageResponse.model_validate(l) for l in profile.languages or []],
            career_preferences=pref_response,
            evidence_items=evidence_resp,
            strength=strength,
            quality=strength.quality,
        )

    async def _get_profile_or_raise(self, user_id: Union[uuid.UUID, str]) -> CandidateProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError(
                message="Candidate profile does not exist for this user. Create a profile first.",
                code="PROFILE_NOT_FOUND",
            )
        return profile

    # ==========================================
    # Root Profile CRUD
    # ==========================================

    async def get_profile(self, user_id: uuid.UUID) -> CandidateProfileResponse:
        profile = await self._get_profile_or_raise(user_id)
        return self._to_response(profile)

    async def create_profile(
        self,
        user_id: uuid.UUID,
        data: CandidateProfileCreate,
    ) -> CandidateProfileResponse:
        user_uuid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
        existing = await self.profile_repo.get_by_user_id(user_uuid)
        if existing:
            raise ConflictError(
                message="Candidate profile already exists for this user. Use PATCH to update.",
                code="PROFILE_ALREADY_EXISTS",
            )

        profile = CandidateProfile(
            id=uuid.uuid4(),
            user_id=user_uuid,
            first_name=data.first_name,
            last_name=data.last_name,
            preferred_name=data.preferred_name,
            professional_headline=data.professional_headline,
            profile_photo=data.profile_photo,
            email=data.email,
            phone=data.phone,
            city=data.city,
            state=data.state,
            country=data.country,
            country_code=data.country_code,
            primary_title=data.primary_title,
            secondary_titles=data.secondary_titles or [],
            career_level=data.career_level,
            industry=data.industry,
            years_of_experience=data.years_of_experience,
            specializations=data.specializations or [],
            base_summary=data.base_summary,
        )

        saved = await self.profile_repo.create_profile(profile)
        logger.info(f"Created candidate master profile for user {user_id}")
        return self._to_response(saved)

    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: CandidateProfileUpdate,
    ) -> CandidateProfileResponse:
        profile = await self._get_profile_or_raise(user_id)

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)

        saved = await self.profile_repo.update_profile(profile)
        return self._to_response(saved)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        await self.profile_repo.delete_profile(profile)
        logger.info(f"Deleted candidate master profile for user {user_id}")

    async def get_strength(self, user_id: uuid.UUID) -> ProfileStrengthResponse:
        profile = await self._get_profile_or_raise(user_id)
        return self.calculate_strength(profile)

    # ==========================================
    # Links CRUD
    # ==========================================

    async def create_link(self, user_id: uuid.UUID, data: LinkCreate) -> LinkResponse:
        profile = await self._get_profile_or_raise(user_id)
        link = CandidateLink(
            id=uuid.uuid4(),
            profile_id=profile.id,
            type=data.type,
            label=data.label,
            url=data.url,
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_link(link)
        return LinkResponse.model_validate(saved)

    async def update_link(
        self,
        user_id: uuid.UUID,
        link_id: uuid.UUID,
        data: LinkUpdate,
    ) -> LinkResponse:
        profile = await self._get_profile_or_raise(user_id)
        link = await self.profile_repo.get_link(profile.id, link_id)
        if not link:
            raise NotFoundError("Link not found.", code="LINK_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(link, key, value)

        saved = await self.profile_repo.update_link(link)
        return LinkResponse.model_validate(saved)

    async def delete_link(self, user_id: uuid.UUID, link_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        link = await self.profile_repo.get_link(profile.id, link_id)
        if not link:
            raise NotFoundError("Link not found.", code="LINK_NOT_FOUND")
        await self.profile_repo.delete_link(link)

    # ==========================================
    # Work Experience CRUD
    # ==========================================

    async def create_experience(self, user_id: uuid.UUID, data: WorkExperienceCreate) -> WorkExperienceResponse:
        profile = await self._get_profile_or_raise(user_id)
        metrics_data = [m.model_dump() for m in data.metrics]
        experience = WorkExperience(
            id=uuid.uuid4(),
            profile_id=profile.id,
            company=data.company,
            position=data.position,
            employment_type=data.employment_type,
            location=data.location,
            start_date=data.start_date,
            end_date=data.end_date,
            is_current=data.is_current,
            description=data.description,
            responsibilities=data.responsibilities,
            achievements=data.achievements,
            technologies=data.technologies,
            metrics=metrics_data,
            provenance=data.provenance or "user_provided",
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_experience(experience)
        return WorkExperienceResponse.model_validate(saved)

    async def update_experience(
        self,
        user_id: uuid.UUID,
        experience_id: uuid.UUID,
        data: WorkExperienceUpdate,
    ) -> WorkExperienceResponse:
        profile = await self._get_profile_or_raise(user_id)
        experience = await self.profile_repo.get_experience(profile.id, experience_id)
        if not experience:
            raise NotFoundError("Work experience record not found.", code="EXPERIENCE_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        if "metrics" in update_dict and update_dict["metrics"] is not None:
            update_dict["metrics"] = [m.model_dump() if hasattr(m, "model_dump") else m for m in update_dict["metrics"]]

        for key, value in update_dict.items():
            setattr(experience, key, value)

        saved = await self.profile_repo.update_experience(experience)
        return WorkExperienceResponse.model_validate(saved)

    async def delete_experience(self, user_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        experience = await self.profile_repo.get_experience(profile.id, experience_id)
        if not experience:
            raise NotFoundError("Work experience record not found.", code="EXPERIENCE_NOT_FOUND")
        await self.profile_repo.delete_experience(experience)

    # ==========================================
    # Education CRUD
    # ==========================================

    async def create_education(self, user_id: uuid.UUID, data: EducationCreate) -> EducationResponse:
        profile = await self._get_profile_or_raise(user_id)
        education = EducationRecord(
            id=uuid.uuid4(),
            profile_id=profile.id,
            institution=data.institution,
            degree=data.degree,
            field_of_study=data.field_of_study,
            location=data.location,
            start_date=data.start_date,
            end_date=data.end_date,
            grade=data.grade,
            description=data.description,
            achievements=data.achievements,
            provenance=data.provenance or "user_provided",
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_education(education)
        return EducationResponse.model_validate(saved)

    async def update_education(
        self,
        user_id: uuid.UUID,
        education_id: uuid.UUID,
        data: EducationUpdate,
    ) -> EducationResponse:
        profile = await self._get_profile_or_raise(user_id)
        education = await self.profile_repo.get_education(profile.id, education_id)
        if not education:
            raise NotFoundError("Education record not found.", code="EDUCATION_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(education, key, value)

        saved = await self.profile_repo.update_education(education)
        return EducationResponse.model_validate(saved)

    async def delete_education(self, user_id: uuid.UUID, education_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        education = await self.profile_repo.get_education(profile.id, education_id)
        if not education:
            raise NotFoundError("Education record not found.", code="EDUCATION_NOT_FOUND")
        await self.profile_repo.delete_education(education)

    # ==========================================
    # Skills CRUD & Relationships
    # ==========================================

    async def create_skill(self, user_id: uuid.UUID, data: SkillCreate) -> SkillResponse:
        profile = await self._get_profile_or_raise(user_id)
        existing = await self.profile_repo.get_skill_by_name(profile.id, data.name)
        if existing:
            raise ConflictError(
                message=f"Skill '{data.name}' already exists in your profile.",
                code="DUPLICATE_SKILL",
            )

        skill = CandidateSkill(
            id=uuid.uuid4(),
            profile_id=profile.id,
            name=data.name,
            category=data.category,
            proficiency=data.proficiency,
            years_of_experience=data.years_of_experience,
            last_used=data.last_used,
            evidence_references=data.evidence_references,
            provenance=data.provenance or "user_provided",
        )
        saved = await self.profile_repo.create_skill(skill)

        # Sync any initial relationships
        if any([data.experience_ids, data.project_ids, data.certification_ids, data.achievement_ids]):
            await self._validate_and_sync_skill_links(
                profile,
                saved.id,
                data.experience_ids,
                data.project_ids,
                data.certification_ids,
                data.achievement_ids,
            )
            saved = await self.profile_repo.get_skill(profile.id, saved.id) or saved

        exp_ids = [a.experience_id for a in saved.experience_associations or []]
        proj_ids = [a.project_id for a in saved.project_associations or []]
        cert_ids = [a.certification_id for a in saved.certification_associations or []]
        ach_ids = [a.achievement_id for a in saved.achievement_associations or []]

        return SkillResponse(
            id=saved.id,
            profile_id=saved.profile_id,
            name=saved.name,
            category=saved.category,
            proficiency=saved.proficiency,
            years_of_experience=saved.years_of_experience,
            last_used=saved.last_used,
            evidence_references=saved.evidence_references or [],
            provenance=saved.provenance,
            experience_ids=exp_ids,
            project_ids=proj_ids,
            certification_ids=cert_ids,
            achievement_ids=ach_ids,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def update_skill(
        self,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
        data: SkillUpdate,
    ) -> SkillResponse:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")

        if data.name and data.name.strip().lower() != skill.name.strip().lower():
            dup = await self.profile_repo.get_skill_by_name(profile.id, data.name)
            if dup and dup.id != skill_id:
                raise ConflictError(
                    message=f"Skill '{data.name}' already exists in your profile.",
                    code="DUPLICATE_SKILL",
                )

        update_dict = data.model_dump(
            exclude_unset=True,
            exclude={"experience_ids", "project_ids", "certification_ids", "achievement_ids"},
        )
        for key, value in update_dict.items():
            setattr(skill, key, value)

        saved = await self.profile_repo.update_skill(skill)

        # Sync relationships if explicitly provided
        if any(x is not None for x in [data.experience_ids, data.project_ids, data.certification_ids, data.achievement_ids]):
            await self._validate_and_sync_skill_links(
                profile,
                skill_id,
                data.experience_ids,
                data.project_ids,
                data.certification_ids,
                data.achievement_ids,
            )
            saved = await self.profile_repo.get_skill(profile.id, skill_id) or saved

        exp_ids = [a.experience_id for a in saved.experience_associations or []]
        proj_ids = [a.project_id for a in saved.project_associations or []]
        cert_ids = [a.certification_id for a in saved.certification_associations or []]
        ach_ids = [a.achievement_id for a in saved.achievement_associations or []]

        return SkillResponse(
            id=saved.id,
            profile_id=saved.profile_id,
            name=saved.name,
            category=saved.category,
            proficiency=saved.proficiency,
            years_of_experience=saved.years_of_experience,
            last_used=saved.last_used,
            evidence_references=saved.evidence_references or [],
            provenance=saved.provenance,
            experience_ids=exp_ids,
            project_ids=proj_ids,
            certification_ids=cert_ids,
            achievement_ids=ach_ids,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def delete_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        await self.profile_repo.delete_skill(skill)

    async def _validate_and_sync_skill_links(
        self,
        profile: CandidateProfile,
        skill_id: uuid.UUID,
        experience_ids: Optional[List[uuid.UUID]],
        project_ids: Optional[List[uuid.UUID]],
        certification_ids: Optional[List[uuid.UUID]],
        achievement_ids: Optional[List[uuid.UUID]],
    ) -> None:
        """Enforce strict profile-level ownership for all linked entities."""
        if experience_ids:
            owned_exp_ids = {e.id for e in profile.experiences or []}
            for exp_id in experience_ids:
                if exp_id not in owned_exp_ids:
                    raise NotFoundError(f"Experience {exp_id} does not belong to your profile.", code="EXPERIENCE_NOT_FOUND")

        if project_ids:
            owned_proj_ids = {p.id for p in profile.projects or []}
            for proj_id in project_ids:
                if proj_id not in owned_proj_ids:
                    raise NotFoundError(f"Project {proj_id} does not belong to your profile.", code="PROJECT_NOT_FOUND")

        if certification_ids:
            owned_cert_ids = {c.id for c in profile.certifications or []}
            for cert_id in certification_ids:
                if cert_id not in owned_cert_ids:
                    raise NotFoundError(f"Certification {cert_id} does not belong to your profile.", code="CERTIFICATION_NOT_FOUND")

        if achievement_ids:
            owned_ach_ids = {a.id for a in profile.achievements or []}
            for ach_id in achievement_ids:
                if ach_id not in owned_ach_ids:
                    raise NotFoundError(f"Achievement {ach_id} does not belong to your profile.", code="ACHIEVEMENT_NOT_FOUND")

        await self.profile_repo.sync_skill_relationships(
            skill_id=skill_id,
            experience_ids=experience_ids,
            project_ids=project_ids,
            certification_ids=certification_ids,
            achievement_ids=achievement_ids,
        )

    async def sync_skill_relationships(
        self,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
        data: SkillRelationshipsUpdate,
    ) -> SkillResponse:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")

        await self._validate_and_sync_skill_links(
            profile,
            skill_id,
            data.experience_ids,
            data.project_ids,
            data.certification_ids,
            data.achievement_ids,
        )

        current_exp_ids = (
            data.experience_ids
            if data.experience_ids is not None
            else [a.experience_id for a in skill.experience_associations or []]
        )
        current_proj_ids = (
            data.project_ids
            if data.project_ids is not None
            else [a.project_id for a in skill.project_associations or []]
        )
        current_cert_ids = (
            data.certification_ids
            if data.certification_ids is not None
            else [a.certification_id for a in skill.certification_associations or []]
        )
        current_ach_ids = (
            data.achievement_ids
            if data.achievement_ids is not None
            else [a.achievement_id for a in skill.achievement_associations or []]
        )

        return SkillResponse(
            id=skill.id,
            profile_id=skill.profile_id,
            name=skill.name,
            category=skill.category,
            proficiency=skill.proficiency,
            years_of_experience=skill.years_of_experience,
            last_used=skill.last_used,
            evidence_references=skill.evidence_references or [],
            provenance=skill.provenance,
            experience_ids=current_exp_ids,
            project_ids=current_proj_ids,
            certification_ids=current_cert_ids,
            achievement_ids=current_ach_ids,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )

    async def link_skill_experience(self, user_id: uuid.UUID, skill_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        exp = await self.profile_repo.get_experience(profile.id, experience_id)
        if not exp:
            raise NotFoundError("Experience not found.", code="EXPERIENCE_NOT_FOUND")
        await self.profile_repo.link_skill_experience(skill_id, experience_id)

    async def unlink_skill_experience(self, user_id: uuid.UUID, skill_id: uuid.UUID, experience_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        await self.profile_repo.unlink_skill_experience(skill_id, experience_id)

    async def link_skill_project(self, user_id: uuid.UUID, skill_id: uuid.UUID, project_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        proj = await self.profile_repo.get_project(profile.id, project_id)
        if not proj:
            raise NotFoundError("Project not found.", code="PROJECT_NOT_FOUND")
        await self.profile_repo.link_skill_project(skill_id, project_id)

    async def unlink_skill_project(self, user_id: uuid.UUID, skill_id: uuid.UUID, project_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        await self.profile_repo.unlink_skill_project(skill_id, project_id)

    async def link_skill_certification(self, user_id: uuid.UUID, skill_id: uuid.UUID, certification_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        cert = await self.profile_repo.get_certification(profile.id, certification_id)
        if not cert:
            raise NotFoundError("Certification not found.", code="CERTIFICATION_NOT_FOUND")
        await self.profile_repo.link_skill_certification(skill_id, certification_id)

    async def unlink_skill_certification(self, user_id: uuid.UUID, skill_id: uuid.UUID, certification_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        await self.profile_repo.unlink_skill_certification(skill_id, certification_id)

    async def link_skill_achievement(self, user_id: uuid.UUID, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        ach = await self.profile_repo.get_achievement(profile.id, achievement_id)
        if not ach:
            raise NotFoundError("Achievement not found.", code="ACHIEVEMENT_NOT_FOUND")
        await self.profile_repo.link_skill_achievement(skill_id, achievement_id)

    async def unlink_skill_achievement(self, user_id: uuid.UUID, skill_id: uuid.UUID, achievement_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        skill = await self.profile_repo.get_skill(profile.id, skill_id)
        if not skill:
            raise NotFoundError("Skill not found.", code="SKILL_NOT_FOUND")
        await self.profile_repo.unlink_skill_achievement(skill_id, achievement_id)

    # ==========================================
    # Projects CRUD
    # ==========================================

    async def create_project(self, user_id: uuid.UUID, data: ProjectCreate) -> ProjectResponse:
        profile = await self._get_profile_or_raise(user_id)
        project = Project(
            id=uuid.uuid4(),
            profile_id=profile.id,
            name=data.name,
            role=data.role,
            description=data.description,
            problem=data.problem,
            solution=data.solution,
            responsibilities=data.responsibilities,
            achievements=data.achievements,
            technologies=data.technologies,
            architecture=data.architecture,
            start_date=data.start_date,
            end_date=data.end_date,
            team_size=data.team_size,
            live_url=data.live_url,
            repository_url=data.repository_url,
            featured=data.featured,
            provenance=data.provenance or "user_provided",
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_project(project)
        return ProjectResponse.model_validate(saved)

    async def update_project(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        data: ProjectUpdate,
    ) -> ProjectResponse:
        profile = await self._get_profile_or_raise(user_id)
        project = await self.profile_repo.get_project(profile.id, project_id)
        if not project:
            raise NotFoundError("Project not found.", code="PROJECT_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)

        saved = await self.profile_repo.update_project(project)
        return ProjectResponse.model_validate(saved)

    async def delete_project(self, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        project = await self.profile_repo.get_project(profile.id, project_id)
        if not project:
            raise NotFoundError("Project not found.", code="PROJECT_NOT_FOUND")
        await self.profile_repo.delete_project(project)

    # ==========================================
    # Certifications CRUD
    # ==========================================

    async def create_certification(self, user_id: uuid.UUID, data: CertificationCreate) -> CertificationResponse:
        profile = await self._get_profile_or_raise(user_id)
        cert = Certification(
            id=uuid.uuid4(),
            profile_id=profile.id,
            name=data.name,
            issuer=data.issuer,
            issue_date=data.issue_date,
            expiration_date=data.expiration_date,
            credential_id=data.credential_id,
            credential_url=data.credential_url,
            skills=data.skills,
            provenance=data.provenance or "user_provided",
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_certification(cert)
        return CertificationResponse.model_validate(saved)

    async def update_certification(
        self,
        user_id: uuid.UUID,
        cert_id: uuid.UUID,
        data: CertificationUpdate,
    ) -> CertificationResponse:
        profile = await self._get_profile_or_raise(user_id)
        cert = await self.profile_repo.get_certification(profile.id, cert_id)
        if not cert:
            raise NotFoundError("Certification not found.", code="CERTIFICATION_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(cert, key, value)

        saved = await self.profile_repo.update_certification(cert)
        return CertificationResponse.model_validate(saved)

    async def delete_certification(self, user_id: uuid.UUID, cert_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        cert = await self.profile_repo.get_certification(profile.id, cert_id)
        if not cert:
            raise NotFoundError("Certification not found.", code="CERTIFICATION_NOT_FOUND")
        await self.profile_repo.delete_certification(cert)

    # ==========================================
    # Achievements CRUD
    # ==========================================

    async def create_achievement(self, user_id: uuid.UUID, data: AchievementCreate) -> AchievementResponse:
        profile = await self._get_profile_or_raise(user_id)
        achievement = Achievement(
            id=uuid.uuid4(),
            profile_id=profile.id,
            title=data.title,
            description=data.description,
            date=data.date,
            issuer=data.issuer,
            category=data.category,
            evidence_url=data.evidence_url,
            provenance=data.provenance or "user_provided",
            order_index=data.order_index,
        )
        saved = await self.profile_repo.create_achievement(achievement)
        return AchievementResponse.model_validate(saved)

    async def update_achievement(
        self,
        user_id: uuid.UUID,
        achievement_id: uuid.UUID,
        data: AchievementUpdate,
    ) -> AchievementResponse:
        profile = await self._get_profile_or_raise(user_id)
        achievement = await self.profile_repo.get_achievement(profile.id, achievement_id)
        if not achievement:
            raise NotFoundError("Achievement not found.", code="ACHIEVEMENT_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(achievement, key, value)

        saved = await self.profile_repo.update_achievement(achievement)
        return AchievementResponse.model_validate(saved)

    async def delete_achievement(self, user_id: uuid.UUID, achievement_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        achievement = await self.profile_repo.get_achievement(profile.id, achievement_id)
        if not achievement:
            raise NotFoundError("Achievement not found.", code="ACHIEVEMENT_NOT_FOUND")
        await self.profile_repo.delete_achievement(achievement)

    # ==========================================
    # Languages CRUD
    # ==========================================

    async def create_language(self, user_id: uuid.UUID, data: LanguageCreate) -> LanguageResponse:
        profile = await self._get_profile_or_raise(user_id)
        language = CandidateLanguage(
            id=uuid.uuid4(),
            profile_id=profile.id,
            name=data.name,
            proficiency=data.proficiency,
        )
        saved = await self.profile_repo.create_language(language)
        return LanguageResponse.model_validate(saved)

    async def update_language(
        self,
        user_id: uuid.UUID,
        lang_id: uuid.UUID,
        data: LanguageUpdate,
    ) -> LanguageResponse:
        profile = await self._get_profile_or_raise(user_id)
        language = await self.profile_repo.get_language(profile.id, lang_id)
        if not language:
            raise NotFoundError("Language not found.", code="LANGUAGE_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(language, key, value)

        saved = await self.profile_repo.update_language(language)
        return LanguageResponse.model_validate(saved)

    async def delete_language(self, user_id: uuid.UUID, lang_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        language = await self.profile_repo.get_language(profile.id, lang_id)
        if not language:
            raise NotFoundError("Language not found.", code="LANGUAGE_NOT_FOUND")
        await self.profile_repo.delete_language(language)

    # ==========================================
    # Career Preferences
    # ==========================================

    async def get_preferences(self, user_id: uuid.UUID) -> Optional[CareerPreferencesResponse]:
        profile = await self._get_profile_or_raise(user_id)
        prefs = await self.profile_repo.get_preferences(profile.id)
        if not prefs:
            return None
        return CareerPreferencesResponse.model_validate(prefs)

    async def update_preferences(
        self,
        user_id: uuid.UUID,
        data: CareerPreferencesUpdate,
    ) -> CareerPreferencesResponse:
        profile = await self._get_profile_or_raise(user_id)
        prefs = await self.profile_repo.get_preferences(profile.id)
        if not prefs:
            prefs = CareerPreferences(
                id=uuid.uuid4(),
                profile_id=profile.id,
                target_roles=data.target_roles or [],
                target_industries=data.target_industries or [],
                preferred_locations=data.preferred_locations or [],
                remote_preference=data.remote_preference,
                employment_types=data.employment_types or [],
                availability_status=data.availability_status,
                available_from=data.available_from,
                notice_period_days=data.notice_period_days,
            )
        else:
            update_dict = data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(prefs, key, value)

        saved = await self.profile_repo.save_preferences(prefs)
        return CareerPreferencesResponse.model_validate(saved)

    # ==========================================
    # Phase 1.1: Evidence CRUD & Associations
    # ==========================================

    def _validate_entity_ownership(self, profile: CandidateProfile, entity_type: str, entity_id: uuid.UUID) -> None:
        """Verify that an associated entity exists and strictly belongs to the user's candidate profile."""
        clean_type = entity_type.strip().lower()
        if clean_type == "experience":
            owned_ids = {e.id for e in profile.experiences or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Work experience {entity_id} not found in user profile.", code="EXPERIENCE_NOT_FOUND")
        elif clean_type == "project":
            owned_ids = {p.id for p in profile.projects or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Project {entity_id} not found in user profile.", code="PROJECT_NOT_FOUND")
        elif clean_type == "skill":
            owned_ids = {s.id for s in profile.skills or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Skill {entity_id} not found in user profile.", code="SKILL_NOT_FOUND")
        elif clean_type == "achievement":
            owned_ids = {a.id for a in profile.achievements or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Achievement {entity_id} not found in user profile.", code="ACHIEVEMENT_NOT_FOUND")
        elif clean_type == "certification":
            owned_ids = {c.id for c in profile.certifications or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Certification {entity_id} not found in user profile.", code="CERTIFICATION_NOT_FOUND")
        elif clean_type == "education":
            owned_ids = {edu.id for edu in profile.education or []}
            if entity_id not in owned_ids:
                raise NotFoundError(f"Education record {entity_id} not found in user profile.", code="EDUCATION_NOT_FOUND")
        else:
            raise NotFoundError(f"Unsupported entity type '{entity_type}'.", code="INVALID_ENTITY_TYPE")

    async def list_evidence(self, user_id: uuid.UUID) -> List[EvidenceResponse]:
        profile = await self._get_profile_or_raise(user_id)
        items = await self.profile_repo.list_evidence(profile.id)
        resps = []
        for it in items:
            assoc_resps = [
                EvidenceAssociationResponse(
                    id=a.id,
                    evidence_id=a.evidence_id,
                    entity_type=a.entity_type,
                    entity_id=a.entity_id,
                    created_at=a.created_at,
                )
                for a in it.associations or []
            ]
            resps.append(
                EvidenceResponse(
                    id=it.id,
                    profile_id=it.profile_id,
                    title=it.title,
                    description=it.description,
                    source=it.source,
                    source_type=it.source_type,
                    url=it.url,
                    notes=it.notes,
                    date=it.date,
                    verification_status=it.verification_status,
                    provenance=it.provenance,
                    associations=assoc_resps,
                    created_at=it.created_at,
                    updated_at=it.updated_at,
                )
            )
        return resps

    async def get_evidence(self, user_id: uuid.UUID, evidence_id: uuid.UUID) -> EvidenceResponse:
        profile = await self._get_profile_or_raise(user_id)
        item = await self.profile_repo.get_evidence(profile.id, evidence_id)
        if not item:
            raise NotFoundError("Evidence record not found.", code="EVIDENCE_NOT_FOUND")

        assoc_resps = [
            EvidenceAssociationResponse(
                id=a.id,
                evidence_id=a.evidence_id,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                created_at=a.created_at,
            )
            for a in item.associations or []
        ]
        return EvidenceResponse(
            id=item.id,
            profile_id=item.profile_id,
            title=item.title,
            description=item.description,
            source=item.source,
            source_type=item.source_type,
            url=item.url,
            notes=item.notes,
            date=item.date,
            verification_status=item.verification_status,
            provenance=item.provenance,
            associations=assoc_resps,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def create_evidence(self, user_id: uuid.UUID, data: EvidenceCreate) -> EvidenceResponse:
        profile = await self._get_profile_or_raise(user_id)

        evidence = EvidenceItem(
            id=uuid.uuid4(),
            profile_id=profile.id,
            title=data.title,
            description=data.description,
            source=data.source,
            source_type=data.source_type,
            url=data.url,
            notes=data.notes,
            date=data.date,
            verification_status=data.verification_status or "unverified",
            provenance=data.provenance or "user_provided",
        )
        saved = await self.profile_repo.create_evidence(evidence)

        # Create any initial entity associations
        created_assocs: List[EvidenceAssociation] = []
        for assoc_data in data.associated_entities or []:
            self._validate_entity_ownership(profile, assoc_data.entity_type, assoc_data.entity_id)
            assoc = EvidenceAssociation(
                id=uuid.uuid4(),
                evidence_id=saved.id,
                entity_type=assoc_data.entity_type.strip().lower(),
                entity_id=assoc_data.entity_id,
            )
            created = await self.profile_repo.create_evidence_association(assoc)
            created_assocs.append(created)

        assoc_resps = [
            EvidenceAssociationResponse(
                id=a.id,
                evidence_id=a.evidence_id,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                created_at=a.created_at or datetime.now(timezone.utc),
            )
            for a in created_assocs
        ]
        return EvidenceResponse(
            id=saved.id,
            profile_id=saved.profile_id,
            title=saved.title,
            description=saved.description,
            source=saved.source,
            source_type=saved.source_type,
            url=saved.url,
            notes=saved.notes,
            date=saved.date,
            verification_status=saved.verification_status,
            provenance=saved.provenance,
            associations=assoc_resps,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def update_evidence(
        self,
        user_id: uuid.UUID,
        evidence_id: uuid.UUID,
        data: EvidenceUpdate,
    ) -> EvidenceResponse:
        profile = await self._get_profile_or_raise(user_id)
        evidence = await self.profile_repo.get_evidence(profile.id, evidence_id)
        if not evidence:
            raise NotFoundError("Evidence record not found.", code="EVIDENCE_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(evidence, key, value)

        saved = await self.profile_repo.update_evidence(evidence)
        assoc_resps = [
            EvidenceAssociationResponse(
                id=a.id,
                evidence_id=a.evidence_id,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                created_at=a.created_at,
            )
            for a in saved.associations or []
        ]
        return EvidenceResponse(
            id=saved.id,
            profile_id=saved.profile_id,
            title=saved.title,
            description=saved.description,
            source=saved.source,
            source_type=saved.source_type,
            url=saved.url,
            notes=saved.notes,
            date=saved.date,
            verification_status=saved.verification_status,
            provenance=saved.provenance,
            associations=assoc_resps,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def delete_evidence(self, user_id: uuid.UUID, evidence_id: uuid.UUID) -> None:
        profile = await self._get_profile_or_raise(user_id)
        evidence = await self.profile_repo.get_evidence(profile.id, evidence_id)
        if not evidence:
            raise NotFoundError("Evidence record not found.", code="EVIDENCE_NOT_FOUND")
        await self.profile_repo.delete_evidence(evidence)

    async def create_evidence_association(
        self,
        user_id: uuid.UUID,
        evidence_id: uuid.UUID,
        data: EvidenceAssociationCreate,
    ) -> EvidenceAssociationResponse:
        profile = await self._get_profile_or_raise(user_id)
        evidence = await self.profile_repo.get_evidence(profile.id, evidence_id)
        if not evidence:
            raise NotFoundError("Evidence record not found.", code="EVIDENCE_NOT_FOUND")

        self._validate_entity_ownership(profile, data.entity_type, data.entity_id)

        assoc = EvidenceAssociation(
            id=uuid.uuid4(),
            evidence_id=evidence_id,
            entity_type=data.entity_type.strip().lower(),
            entity_id=data.entity_id,
        )
        saved = await self.profile_repo.create_evidence_association(assoc)
        return EvidenceAssociationResponse(
            id=saved.id,
            evidence_id=saved.evidence_id,
            entity_type=saved.entity_type,
            entity_id=saved.entity_id,
            created_at=saved.created_at,
        )

    async def delete_evidence_association(
        self,
        user_id: uuid.UUID,
        evidence_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> None:
        profile = await self._get_profile_or_raise(user_id)
        evidence = await self.profile_repo.get_evidence(profile.id, evidence_id)
        if not evidence:
            raise NotFoundError("Evidence record not found.", code="EVIDENCE_NOT_FOUND")

        await self.profile_repo.delete_evidence_association(
            evidence_id=evidence_id,
            entity_type=entity_type.strip().lower(),
            entity_id=entity_id,
        )


def get_profile_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProfileService:
    """FastAPI dependency injecting ProfileService with PostgresProfileRepository."""
    repo = PostgresProfileRepository(session)
    return ProfileService(repo)
