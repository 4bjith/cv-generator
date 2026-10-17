import copy
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.export import (
    generate_cv_docx,
    generate_cv_pdf,
    get_candidate_name,
    get_sanitized_export_filename,
)

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.cv_version import CVVersion
from app.models.profile import CandidateProfile
from app.repositories.interfaces.cv_version_repository import ICVVersionRepository
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.cv_version_repository import PostgresCVVersionRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.cv import (
    CVAwardSnapshot,
    CVBasicsSnapshot,
    CVCareerPreferencesSnapshot,
    CVCertificateSnapshot,
    CVContentSnapshot,
    CVEducationSnapshot,
    CVEvidenceItemSnapshot,
    CVExtensionsSnapshot,
    CVLanguageSnapshot,
    CVLinkSnapshot,
    CVLocation,
    CVPresentationSnapshot,
    CVProfile,
    CVProjectSnapshot,
    CVSkillSnapshot,
    CVVersionCreate,
    CVVersionDuplicate,
    CVVersionListResponse,
    CVVersionResponse,
    CVVersionStatus,
    CVVersionSummaryResponse,
    CVVersionUpdate,
    CVWorkSnapshot,
)

logger = get_logger("app.services.cv")


class CVService:
    """Service layer managing CV versioning, point-in-time snapshotting, and lifecycle operations."""

    def __init__(
        self,
        cv_version_repository: ICVVersionRepository,
        profile_repository: IProfileRepository,
        job_target_repository: IJobTargetRepository,
    ) -> None:
        self.cv_repo = cv_version_repository
        self.profile_repo = profile_repository
        self.job_repo = job_target_repository

    # ==========================================
    # Snapshot Serialization
    # ==========================================

    @staticmethod
    def serialize_profile_to_snapshot(profile: CandidateProfile) -> CVContentSnapshot:
        """Create a point-in-time, independent canonical CV snapshot from a CandidateProfile."""
        # 1. Map evidence associations
        evidence_by_entity: Dict[str, List[uuid.UUID]] = {}
        for ev in profile.evidence_items or []:
            for assoc in ev.associations or []:
                key = f"{assoc.entity_type}:{assoc.entity_id}"
                if key not in evidence_by_entity:
                    evidence_by_entity[key] = []
                evidence_by_entity[key].append(ev.id)

        # 2. Links
        links = [
            CVLinkSnapshot(
                id=link.id,
                type=link.type,
                label=link.label,
                url=link.url,
                order_index=link.order_index,
            )
            for link in (profile.links or [])
        ]

        # 3. Basics
        full_name = " ".join(filter(None, [profile.first_name, profile.last_name])).strip()
        location_obj = None
        if any([profile.city, profile.state, profile.country, profile.country_code]):
            location_obj = CVLocation(
                city=profile.city,
                region=profile.state,
                country=profile.country,
                country_code=profile.country_code,
            )

        profiles_list = [
            CVProfile(
                network=link.type,
                username=link.label,
                url=link.url,
                id=link.id,
            )
            for link in (profile.links or [])
        ]

        basics = CVBasicsSnapshot(
            name=full_name,
            label=profile.professional_headline or profile.primary_title,
            image=profile.profile_photo,
            email=profile.email,
            phone=profile.phone,
            summary=profile.base_summary,
            location=location_obj,
            profiles=profiles_list,
            first_name=profile.first_name,
            last_name=profile.last_name,
            preferred_name=profile.preferred_name,
            professional_headline=profile.professional_headline,
            profile_photo=profile.profile_photo,
            city=profile.city,
            state=profile.state,
            country=profile.country,
            country_code=profile.country_code,
            primary_title=profile.primary_title,
            secondary_titles=list(profile.secondary_titles or []),
            career_level=profile.career_level,
            industry=profile.industry,
            years_of_experience=profile.years_of_experience,
            specializations=list(profile.specializations or []),
            base_summary=profile.base_summary,
        )

        # 4. Work Experiences (canonical work)
        work = [
            CVWorkSnapshot(
                id=exp.id,
                name=exp.company,
                position=exp.position,
                startDate=exp.start_date,
                endDate=exp.end_date,
                summary=exp.description,
                highlights=list(exp.responsibilities or []) + list(exp.achievements or []),
                company=exp.company,
                employment_type=exp.employment_type,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                responsibilities=list(exp.responsibilities or []),
                achievements=list(exp.achievements or []),
                technologies=list(exp.technologies or []),
                metrics=list(exp.metrics or []),
                provenance=getattr(exp, "provenance", "user_provided") or "user_provided",
                evidence_ids=evidence_by_entity.get(f"experience:{exp.id}", []),
                order_index=exp.order_index,
            )
            for exp in (profile.experiences or [])
        ]

        # 5. Education
        education = [
            CVEducationSnapshot(
                id=edu.id,
                institution=edu.institution,
                studyType=edu.degree,
                area=edu.field_of_study,
                startDate=edu.start_date,
                endDate=edu.end_date,
                score=edu.grade,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                location=edu.location,
                start_date=edu.start_date,
                end_date=edu.end_date,
                grade=edu.grade,
                description=edu.description,
                achievements=list(edu.achievements or []),
                provenance=getattr(edu, "provenance", "user_provided") or "user_provided",
                evidence_ids=evidence_by_entity.get(f"education:{edu.id}", []),
                order_index=edu.order_index,
            )
            for edu in (profile.education or [])
        ]

        # 6. Skills
        skills = [
            CVSkillSnapshot(
                id=s.id,
                name=s.name,
                level=s.proficiency,
                keywords=[s.category] if s.category else [],
                category=s.category,
                proficiency=s.proficiency,
                years_of_experience=s.years_of_experience,
                last_used=s.last_used,
                evidence_references=list(s.evidence_references or []),
                provenance=getattr(s, "provenance", "user_provided") or "user_provided",
                experience_ids=[a.experience_id for a in (s.experience_associations or [])],
                project_ids=[a.project_id for a in (s.project_associations or [])],
                certification_ids=[a.certification_id for a in (s.certification_associations or [])],
                achievement_ids=[a.achievement_id for a in (s.achievement_associations or [])],
                evidence_ids=evidence_by_entity.get(f"skill:{s.id}", []),
            )
            for s in (profile.skills or [])
        ]

        # 7. Projects
        projects = [
            CVProjectSnapshot(
                id=p.id,
                name=p.name,
                description=p.description,
                highlights=list(p.responsibilities or []) + list(p.achievements or []),
                keywords=list(p.technologies or []),
                startDate=p.start_date,
                endDate=p.end_date,
                url=p.live_url,
                roles=[p.role] if p.role else [],
                role=p.role,
                problem=p.problem,
                solution=p.solution,
                responsibilities=list(p.responsibilities or []),
                achievements=list(p.achievements or []),
                technologies=list(p.technologies or []),
                architecture=p.architecture,
                start_date=p.start_date,
                end_date=p.end_date,
                team_size=p.team_size,
                live_url=p.live_url,
                repository_url=p.repository_url,
                featured=p.featured,
                provenance=getattr(p, "provenance", "user_provided") or "user_provided",
                evidence_ids=evidence_by_entity.get(f"project:{p.id}", []),
                order_index=p.order_index,
            )
            for p in (profile.projects or [])
        ]

        # 8. Certificates
        certificates = [
            CVCertificateSnapshot(
                id=c.id,
                name=c.name,
                date=c.issue_date,
                issuer=c.issuer,
                url=c.credential_url,
                issue_date=c.issue_date,
                expiration_date=c.expiration_date,
                credential_id=c.credential_id,
                credential_url=c.credential_url,
                skills=list(c.skills or []),
                provenance=getattr(c, "provenance", "user_provided") or "user_provided",
                evidence_ids=evidence_by_entity.get(f"certification:{c.id}", []),
                order_index=c.order_index,
            )
            for c in (profile.certifications or [])
        ]

        # 9. Awards
        awards = [
            CVAwardSnapshot(
                id=a.id,
                title=a.title,
                date=a.date,
                awarder=a.issuer,
                summary=a.description,
                issuer=a.issuer,
                description=a.description,
                category=a.category,
                evidence_url=a.evidence_url,
                provenance=getattr(a, "provenance", "user_provided") or "user_provided",
                evidence_ids=evidence_by_entity.get(f"achievement:{a.id}", []),
                order_index=a.order_index,
            )
            for a in (profile.achievements or [])
        ]

        # 10. Languages
        languages = [
            CVLanguageSnapshot(
                id=lang.id,
                language=lang.name,
                fluency=lang.proficiency,
                name=lang.name,
                proficiency=lang.proficiency,
            )
            for lang in (profile.languages or [])
        ]

        # 11. Career Preferences
        prefs = None
        if profile.career_preferences:
            p = profile.career_preferences
            prefs = CVCareerPreferencesSnapshot(
                target_roles=list(p.target_roles or []),
                target_industries=list(p.target_industries or []),
                preferred_locations=list(p.preferred_locations or []),
                remote_preference=p.remote_preference,
                employment_types=list(p.employment_types or []),
                availability_status=p.availability_status,
                available_from=p.available_from,
                notice_period_days=p.notice_period_days,
            )

        # 12. Evidence items
        evidence_items = [
            CVEvidenceItemSnapshot(
                id=ev.id,
                title=ev.title,
                description=ev.description,
                source=ev.source,
                source_type=ev.source_type,
                url=ev.url,
                notes=ev.notes,
                date=ev.date,
                verification_status=ev.verification_status,
                provenance=getattr(ev, "provenance", "user_provided") or "user_provided",
                associated_entities=[
                    {"entity_type": assoc.entity_type, "entity_id": str(assoc.entity_id)}
                    for assoc in (ev.associations or [])
                ],
            )
            for ev in (profile.evidence_items or [])
        ]

        return CVContentSnapshot(
            schema_version="2.0.0",
            basics=basics,
            work=work,
            education=education,
            skills=skills,
            projects=projects,
            certificates=certificates,
            awards=awards,
            languages=languages,
            presentation=CVPresentationSnapshot(),
            extensions=CVExtensionsSnapshot(
                career_preferences=prefs,
                evidence_items=evidence_items,
                links=links,
            ),
        )

    # ==========================================
    # Response Mappers
    # ==========================================

    @staticmethod
    def _to_response(version: CVVersion) -> CVVersionResponse:
        snapshot_data = version.content_snapshot or {}
        snapshot = CVContentSnapshot.model_validate(snapshot_data)
        return CVVersionResponse(
            id=version.id,
            user_id=version.user_id,
            job_target_id=version.job_target_id,
            job_target_title=version.job_target.title if version.job_target else None,
            job_target_company=version.job_target.company_name if version.job_target else None,
            name=version.name,
            status=CVVersionStatus(version.status),
            content_snapshot=snapshot,
            created_at=version.created_at,
            updated_at=version.updated_at,
        )

    @staticmethod
    def _to_summary_response(version: CVVersion) -> CVVersionSummaryResponse:
        return CVVersionSummaryResponse(
            id=version.id,
            user_id=version.user_id,
            job_target_id=version.job_target_id,
            job_target_title=version.job_target.title if version.job_target else None,
            job_target_company=version.job_target.company_name if version.job_target else None,
            name=version.name,
            status=CVVersionStatus(version.status),
            created_at=version.created_at,
            updated_at=version.updated_at,
        )

    # ==========================================
    # Lifecycle Operations
    # ==========================================

    async def create_version_from_profile(
        self,
        user_id: Union[uuid.UUID, str],
        data: CVVersionCreate,
    ) -> CVVersionResponse:
        """Create a new independent CV Version from the user's CandidateProfile."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id

        # 1. Verify candidate profile exists
        profile = await self.profile_repo.get_by_user_id(uid)
        if not profile:
            raise NotFoundError(
                message="Candidate profile not found. Please create your profile before generating a CV version.",
                code="PROFILE_NOT_FOUND",
            )

        # 2. Verify job target ownership if linked
        if data.job_target_id:
            job = await self.job_repo.get_by_id(job_id=data.job_target_id, user_id=uid)
            if not job:
                raise NotFoundError(
                    message="Job target does not exist or you do not have permission to access it.",
                    code="JOB_TARGET_NOT_FOUND",
                )

        # 3. Create point-in-time content snapshot
        snapshot = self.serialize_profile_to_snapshot(profile)
        snapshot_dict = snapshot.model_dump(mode="json")

        # 4. Instantiate & persist CVVersion
        cv_version = CVVersion(
            id=uuid.uuid4(),
            user_id=uid,
            job_target_id=data.job_target_id,
            name=data.name,
            status=CVVersionStatus.DRAFT.value,
            content_snapshot=snapshot_dict,
        )

        saved = await self.cv_repo.create(cv_version)
        logger.info(f"Created CV Version {saved.id} ('{saved.name}') for user {uid}")
        return self._to_response(saved)

    async def get_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
    ) -> CVVersionResponse:
        """Retrieve a specific CV Version with full snapshot owned by user_id."""
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=user_id)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )
        return self._to_response(version)

    async def list_versions(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        job_target_id: Optional[Union[uuid.UUID, str]] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CVVersionListResponse:
        """List CV versions owned by user_id with search, filters and pagination."""
        items, total = await self.cv_repo.list_by_user(
            user_id=user_id,
            status=status,
            job_target_id=job_target_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return CVVersionListResponse(
            items=[self._to_summary_response(v) for v in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
        data: CVVersionUpdate,
    ) -> CVVersionResponse:
        """Update CV Version metadata and/or version-specific content snapshot."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        # If job_target_id is changed, verify ownership
        if data.job_target_id is not None and data.job_target_id != version.job_target_id:
            job = await self.job_repo.get_by_id(job_id=data.job_target_id, user_id=uid)
            if not job:
                raise NotFoundError(
                    message="Job target does not exist or you do not have permission to access it.",
                    code="JOB_TARGET_NOT_FOUND",
                )
            version.job_target_id = data.job_target_id

        if data.name is not None:
            version.name = data.name

        if data.status is not None:
            version.status = data.status.value if hasattr(data.status, "value") else str(data.status)

        if data.content_snapshot is not None:
            version.content_snapshot = data.content_snapshot.model_dump(mode="json")

        updated = await self.cv_repo.update(version)
        logger.info(f"Updated CV version {updated.id} for user {uid}")
        return self._to_response(updated)

    async def duplicate_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
        data: CVVersionDuplicate,
    ) -> CVVersionResponse:
        """Duplicate an existing CV version into an independent clone."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        original = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not original:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        new_name = data.name if data.name else f"{original.name} (Copy)"
        # Deep copy the snapshot dictionary to guarantee complete data isolation
        cloned_snapshot = copy.deepcopy(original.content_snapshot or {})

        duplicate = CVVersion(
            id=uuid.uuid4(),
            user_id=uid,
            job_target_id=original.job_target_id,
            name=new_name,
            status=CVVersionStatus.DRAFT.value,
            content_snapshot=cloned_snapshot,
        )

        saved = await self.cv_repo.create(duplicate)
        logger.info(f"Duplicated CV version {original.id} -> {saved.id} ('{saved.name}') for user {uid}")
        return self._to_response(saved)

    async def archive_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
    ) -> CVVersionResponse:
        """Archive a CV version."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        version.status = CVVersionStatus.ARCHIVED.value
        updated = await self.cv_repo.update(version)
        logger.info(f"Archived CV version {updated.id} for user {uid}")
        return self._to_response(updated)

    async def restore_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
    ) -> CVVersionResponse:
        """Restore an archived CV version to draft."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        version.status = CVVersionStatus.DRAFT.value
        updated = await self.cv_repo.update(version)
        logger.info(f"Restored CV version {updated.id} to draft for user {uid}")
        return self._to_response(updated)

    async def delete_version(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
    ) -> None:
        """Delete a CV version owned by user_id."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        await self.cv_repo.delete(version)
        logger.info(f"Deleted CV version {version_id} for user {uid}")

    async def export_json_resume(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
        apply_visibility: bool = False,
    ) -> Dict[str, Any]:
        """Export CV version into a clean, standard JSON Resume document."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )
        snapshot = CVContentSnapshot.model_validate(version.content_snapshot or {})
        return snapshot.to_json_resume(apply_visibility=apply_visibility)

    async def export_pdf(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bytes, str]:
        """Generate downloadable PDF representation of a CV version."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )
        snapshot = CVContentSnapshot.model_validate(version.content_snapshot or {})
        pdf_bytes = generate_cv_pdf(snapshot, overrides=overrides)
        candidate_name = get_candidate_name(snapshot)
        filename = get_sanitized_export_filename(candidate_name, "pdf")
        return pdf_bytes, filename

    async def export_docx(
        self,
        user_id: Union[uuid.UUID, str],
        version_id: Union[uuid.UUID, str],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bytes, str]:
        """Generate editable Microsoft Word (.docx) representation of a CV version."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        version = await self.cv_repo.get_by_id(version_id=version_id, user_id=uid)
        if not version:
            raise NotFoundError(
                message="CV version does not exist or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )
        snapshot = CVContentSnapshot.model_validate(version.content_snapshot or {})
        docx_bytes = generate_cv_docx(snapshot, overrides=overrides)
        candidate_name = get_candidate_name(snapshot)
        filename = get_sanitized_export_filename(candidate_name, "docx")
        return docx_bytes, filename


def get_cv_service(session: AsyncSession = Depends(get_db_session)) -> CVService:
    """FastAPI dependency injecting CVService initialized with Postgres repositories."""
    cv_repo = PostgresCVVersionRepository(session)
    profile_repo = PostgresProfileRepository(session)
    job_repo = PostgresJobTargetRepository(session)
    return CVService(
        cv_version_repository=cv_repo,
        profile_repository=profile_repo,
        job_target_repository=job_repo,
    )
