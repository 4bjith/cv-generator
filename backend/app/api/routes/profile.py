import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.schemas.auth import UserResponse
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
from app.services.profile_service import ProfileService, get_profile_service


router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


# ==========================================
# Root Profile
# ==========================================

@router.get(
    "",
    response_model=CandidateProfileResponse,
    summary="Get candidate profile",
    description="Retrieve the complete master candidate career profile for the authenticated user.",
)
async def get_profile(
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CandidateProfileResponse:
    return await service.get_profile(current_user.id)


@router.post(
    "",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create candidate profile",
    description="Initialize the master career profile for the authenticated user.",
)
async def create_profile(
    data: CandidateProfileCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CandidateProfileResponse:
    return await service.create_profile(current_user.id, data)


@router.patch(
    "",
    response_model=CandidateProfileResponse,
    summary="Update candidate profile",
    description="Update top-level identity, contact, professional identity, or summary fields.",
)
async def update_profile(
    data: CandidateProfileUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CandidateProfileResponse:
    return await service.update_profile(current_user.id, data)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete candidate profile",
    description="Permanently delete the candidate profile and all nested career data.",
)
async def delete_profile(
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_profile(current_user.id)


@router.get(
    "/strength",
    response_model=ProfileStrengthResponse,
    summary="Get profile strength and completion",
    description="Get deterministic completion score, breakdown by section, and actionable suggestions.",
)
async def get_profile_strength(
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileStrengthResponse:
    return await service.get_strength(current_user.id)


# ==========================================
# External Links
# ==========================================

@router.post(
    "/links",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add professional link",
)
async def add_link(
    data: LinkCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> LinkResponse:
    return await service.create_link(current_user.id, data)


@router.patch(
    "/links/{link_id}",
    response_model=LinkResponse,
    summary="Update professional link",
)
async def update_link(
    link_id: uuid.UUID,
    data: LinkUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> LinkResponse:
    return await service.update_link(current_user.id, link_id, data)


@router.delete(
    "/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete professional link",
)
async def delete_link(
    link_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_link(current_user.id, link_id)


# ==========================================
# Work Experience
# ==========================================

@router.post(
    "/experience",
    response_model=WorkExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add work experience",
)
async def add_experience(
    data: WorkExperienceCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> WorkExperienceResponse:
    return await service.create_experience(current_user.id, data)


@router.patch(
    "/experience/{experience_id}",
    response_model=WorkExperienceResponse,
    summary="Update work experience",
)
async def update_experience(
    experience_id: uuid.UUID,
    data: WorkExperienceUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> WorkExperienceResponse:
    return await service.update_experience(current_user.id, experience_id, data)


@router.delete(
    "/experience/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete work experience",
)
async def delete_experience(
    experience_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_experience(current_user.id, experience_id)


# ==========================================
# Education
# ==========================================

@router.post(
    "/education",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add education record",
)
async def add_education(
    data: EducationCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EducationResponse:
    return await service.create_education(current_user.id, data)


@router.patch(
    "/education/{education_id}",
    response_model=EducationResponse,
    summary="Update education record",
)
async def update_education(
    education_id: uuid.UUID,
    data: EducationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EducationResponse:
    return await service.update_education(current_user.id, education_id, data)


@router.delete(
    "/education/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete education record",
)
async def delete_education(
    education_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_education(current_user.id, education_id)


# ==========================================
# Skills
# ==========================================

@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add skill",
)
async def add_skill(
    data: SkillCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> SkillResponse:
    return await service.create_skill(current_user.id, data)


@router.patch(
    "/skills/{skill_id}",
    response_model=SkillResponse,
    summary="Update skill",
)
async def update_skill(
    skill_id: uuid.UUID,
    data: SkillUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> SkillResponse:
    return await service.update_skill(current_user.id, skill_id, data)


@router.delete(
    "/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete skill",
)
async def delete_skill(
    skill_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_skill(current_user.id, skill_id)


@router.put(
    "/skills/{skill_id}/relationships",
    response_model=SkillResponse,
    summary="Sync all relationships for a skill",
)
async def sync_skill_relationships(
    skill_id: uuid.UUID,
    data: SkillRelationshipsUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> SkillResponse:
    return await service.sync_skill_relationships(current_user.id, skill_id, data)


@router.post(
    "/skills/{skill_id}/experiences/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Link skill to experience",
)
async def link_skill_experience(
    skill_id: uuid.UUID,
    experience_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.link_skill_experience(current_user.id, skill_id, experience_id)


@router.delete(
    "/skills/{skill_id}/experiences/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink skill from experience",
)
async def unlink_skill_experience(
    skill_id: uuid.UUID,
    experience_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.unlink_skill_experience(current_user.id, skill_id, experience_id)


@router.post(
    "/skills/{skill_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Link skill to project",
)
async def link_skill_project(
    skill_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.link_skill_project(current_user.id, skill_id, project_id)


@router.delete(
    "/skills/{skill_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink skill from project",
)
async def unlink_skill_project(
    skill_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.unlink_skill_project(current_user.id, skill_id, project_id)


@router.post(
    "/skills/{skill_id}/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Link skill to certification",
)
async def link_skill_certification(
    skill_id: uuid.UUID,
    certification_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.link_skill_certification(current_user.id, skill_id, certification_id)


@router.delete(
    "/skills/{skill_id}/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink skill from certification",
)
async def unlink_skill_certification(
    skill_id: uuid.UUID,
    certification_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.unlink_skill_certification(current_user.id, skill_id, certification_id)


@router.post(
    "/skills/{skill_id}/achievements/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Link skill to achievement",
)
async def link_skill_achievement(
    skill_id: uuid.UUID,
    achievement_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.link_skill_achievement(current_user.id, skill_id, achievement_id)


@router.delete(
    "/skills/{skill_id}/achievements/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink skill from achievement",
)
async def unlink_skill_achievement(
    skill_id: uuid.UUID,
    achievement_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.unlink_skill_achievement(current_user.id, skill_id, achievement_id)



# ==========================================
# Projects
# ==========================================

@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add project",
)
async def add_project(
    data: ProjectCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProjectResponse:
    return await service.create_project(current_user.id, data)


@router.patch(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProjectResponse:
    return await service.update_project(current_user.id, project_id, data)


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_project(current_user.id, project_id)


# ==========================================
# Certifications
# ==========================================

@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add certification",
)
async def add_certification(
    data: CertificationCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CertificationResponse:
    return await service.create_certification(current_user.id, data)


@router.patch(
    "/certifications/{cert_id}",
    response_model=CertificationResponse,
    summary="Update certification",
)
async def update_certification(
    cert_id: uuid.UUID,
    data: CertificationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CertificationResponse:
    return await service.update_certification(current_user.id, cert_id, data)


@router.delete(
    "/certifications/{cert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete certification",
)
async def delete_certification(
    cert_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_certification(current_user.id, cert_id)


# ==========================================
# Achievements
# ==========================================

@router.post(
    "/achievements",
    response_model=AchievementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add achievement",
)
async def add_achievement(
    data: AchievementCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> AchievementResponse:
    return await service.create_achievement(current_user.id, data)


@router.patch(
    "/achievements/{achievement_id}",
    response_model=AchievementResponse,
    summary="Update achievement",
)
async def update_achievement(
    achievement_id: uuid.UUID,
    data: AchievementUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> AchievementResponse:
    return await service.update_achievement(current_user.id, achievement_id, data)


@router.delete(
    "/achievements/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete achievement",
)
async def delete_achievement(
    achievement_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_achievement(current_user.id, achievement_id)


# ==========================================
# Languages
# ==========================================

@router.post(
    "/languages",
    response_model=LanguageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add language",
)
async def add_language(
    data: LanguageCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> LanguageResponse:
    return await service.create_language(current_user.id, data)


@router.patch(
    "/languages/{lang_id}",
    response_model=LanguageResponse,
    summary="Update language",
)
async def update_language(
    lang_id: uuid.UUID,
    data: LanguageUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> LanguageResponse:
    return await service.update_language(current_user.id, lang_id, data)


@router.delete(
    "/languages/{lang_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete language",
)
async def delete_language(
    lang_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_language(current_user.id, lang_id)


# ==========================================
# Career Preferences
# ==========================================

@router.get(
    "/preferences",
    response_model=Optional[CareerPreferencesResponse],
    summary="Get career preferences",
)
async def get_career_preferences(
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> Optional[CareerPreferencesResponse]:
    return await service.get_preferences(current_user.id)


@router.put(
    "/preferences",
    response_model=CareerPreferencesResponse,
    summary="Save career preferences",
)
@router.patch(
    "/preferences",
    response_model=CareerPreferencesResponse,
    summary="Update career preferences",
)
async def update_career_preferences(
    data: CareerPreferencesUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> CareerPreferencesResponse:
    return await service.update_preferences(current_user.id, data)


# ==========================================
# Phase 1.1: Evidence Catalog & Associations
# ==========================================

@router.get(
    "/evidence",
    response_model=List[EvidenceResponse],
    summary="List all evidence items",
    description="Retrieve all evidence artifacts and their associations for the authenticated user.",
)
async def list_evidence(
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> List[EvidenceResponse]:
    return await service.list_evidence(current_user.id)


@router.post(
    "/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create evidence item",
    description="Add a new verifiable evidence record with optional initial entity associations.",
)
async def create_evidence(
    data: EvidenceCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EvidenceResponse:
    return await service.create_evidence(current_user.id, data)


@router.get(
    "/evidence/{evidence_id}",
    response_model=EvidenceResponse,
    summary="Get evidence item",
)
async def get_evidence(
    evidence_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EvidenceResponse:
    return await service.get_evidence(current_user.id, evidence_id)


@router.patch(
    "/evidence/{evidence_id}",
    response_model=EvidenceResponse,
    summary="Update evidence item",
)
async def update_evidence(
    evidence_id: uuid.UUID,
    data: EvidenceUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EvidenceResponse:
    return await service.update_evidence(current_user.id, evidence_id, data)


@router.delete(
    "/evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete evidence item",
)
async def delete_evidence(
    evidence_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_evidence(current_user.id, evidence_id)


@router.post(
    "/evidence/{evidence_id}/associations",
    response_model=EvidenceAssociationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Associate evidence with a profile fact",
)
async def associate_evidence(
    evidence_id: uuid.UUID,
    data: EvidenceAssociationCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> EvidenceAssociationResponse:
    return await service.create_evidence_association(current_user.id, evidence_id, data)


@router.delete(
    "/evidence/{evidence_id}/associations/{entity_type}/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disassociate evidence from a profile fact",
)
async def disassociate_evidence(
    evidence_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    await service.delete_evidence_association(current_user.id, evidence_id, entity_type, entity_id)

