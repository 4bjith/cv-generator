from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ==========================================
# CV Version Lifecycle Enums
# ==========================================

class CVVersionStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


# ==========================================
# Sub-models: Location & Profiles (JSON Resume Canonical)
# ==========================================

class CVLocation(BaseModel):
    address: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")
    city: Optional[str] = None
    country_code: Optional[str] = Field(None, alias="countryCode")
    region: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CVProfile(BaseModel):
    network: str = Field(default="")
    username: Optional[str] = None
    url: str = Field(default="")
    id: Optional[uuid.UUID] = None


# ==========================================
# Snapshot Section Models
# ==========================================

class CVLinkSnapshot(BaseModel):
    id: Optional[uuid.UUID] = None
    type: str = "other"
    label: str
    url: str
    order_index: int = 0


class CVBasicsSnapshot(BaseModel):
    # Canonical JSON Resume fields
    name: str = Field(default="")
    label: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[CVLocation] = None
    profiles: List[CVProfile] = Field(default_factory=list)

    # Legacy & product-specific fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    professional_headline: Optional[str] = None
    profile_photo: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    primary_title: Optional[str] = None
    secondary_titles: List[str] = Field(default_factory=list)
    career_level: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[float] = None
    specializations: List[str] = Field(default_factory=list)
    base_summary: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_basics(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        # 1. Name normalization & deterministic resolution
        first = d.get("first_name")
        last = d.get("last_name")
        legacy_full = " ".join(filter(None, [first, last])).strip() if (first or last) else None
        canonical_name = d.get("name")

        if legacy_full and canonical_name and legacy_full != canonical_name:
            # Deterministic resolution: if legacy full was modified/provided, propagate to canonical name
            final_name = legacy_full
        else:
            final_name = canonical_name or legacy_full or ""
        d["name"] = final_name
        if final_name:
            parts = final_name.split()
            d["first_name"] = first if first is not None else parts[0]
            d["last_name"] = last if last is not None else (" ".join(parts[1:]) if len(parts) > 1 else None)

        # 2. Label vs professional_headline
        label = d.get("label")
        headline = d.get("professional_headline") or d.get("primary_title")
        if headline and label and headline.strip() != label.strip():
            # Deterministic resolution: legacy headline update propagates to canonical label
            final_label = headline
        else:
            final_label = label or headline
        d["label"] = final_label
        d["professional_headline"] = final_label

        # 3. Image vs profile_photo
        img = d.get("image")
        photo = d.get("profile_photo")
        final_img = photo or img
        d["image"] = final_img
        d["profile_photo"] = final_img

        # 4. Summary vs base_summary
        summ = d.get("summary")
        base_summ = d.get("base_summary")
        if base_summ and summ and base_summ.strip() != summ.strip():
            final_summ = base_summ
        else:
            final_summ = summ or base_summ
        d["summary"] = final_summ
        d["base_summary"] = final_summ

        # 5. Location normalization
        loc = d.get("location")
        city = d.get("city")
        state = d.get("state")
        country = d.get("country")
        country_code = d.get("country_code")

        if loc and isinstance(loc, dict):
            loc_city = loc.get("city")
            loc_region = loc.get("region")
            loc_country = loc.get("country")
            loc_code = loc.get("countryCode") or loc.get("country_code")
            if city and loc_city and city.strip() != loc_city.strip():
                raise ValueError("Conflicting location city between canonical and legacy fields.")
            if state and loc_region and state.strip() != loc_region.strip():
                raise ValueError("Conflicting location state/region between canonical and legacy fields.")
            if country and loc_country and country.strip() != loc_country.strip():
                raise ValueError("Conflicting location country between canonical and legacy fields.")
            if country_code and loc_code and country_code.strip() != loc_code.strip():
                raise ValueError("Conflicting location countryCode between canonical and legacy fields.")
            if not d.get("city"):
                d["city"] = loc_city
            if not d.get("state"):
                d["state"] = loc_region
            if not d.get("country"):
                d["country"] = loc_country
            if not d.get("country_code"):
                d["country_code"] = loc_code
        elif any([city, state, country, country_code]):
            d["location"] = {
                "city": city,
                "region": state,
                "country": country,
                "countryCode": country_code,
            }

        return d


class CVWorkSnapshot(BaseModel):
    # Canonical JSON Resume fields
    name: str = Field(default="", description="Company or organization name")
    position: str = Field(default="", description="Role or position title")
    url: Optional[str] = None
    startDate: Optional[str] = Field(None, alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    summary: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    company: Optional[str] = None
    employment_type: str = "full_time"
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int = 0

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_work(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        # Name vs Company
        name = d.get("name")
        company = d.get("company")
        if name and company and name.strip() != company.strip():
            raise ValueError(f"Conflicting fields: 'name' ('{name}') conflicts with 'company' ('{company}').")
        final_name = name or company or ""
        d["name"] = final_name
        d["company"] = final_name

        # Start Date
        start = d.get("startDate") or d.get("start_date")
        if d.get("startDate") and d.get("start_date") and d.get("startDate") != d.get("start_date"):
            raise ValueError("Conflicting fields: 'startDate' conflicts with 'start_date'.")
        d["startDate"] = start
        d["start_date"] = start

        # End Date
        end = d.get("endDate") or d.get("end_date")
        if d.get("endDate") and d.get("end_date") and d.get("endDate") != d.get("end_date"):
            raise ValueError("Conflicting fields: 'endDate' conflicts with 'end_date'.")
        d["endDate"] = end
        d["end_date"] = end

        # Summary vs Description
        summ = d.get("summary")
        desc = d.get("description")
        if summ and desc and summ.strip() != desc.strip():
            raise ValueError("Conflicting fields: 'summary' conflicts with 'description'.")
        final_summ = summ or desc
        d["summary"] = final_summ
        d["description"] = final_summ

        # Highlights vs Responsibilities / Achievements
        highlights = d.get("highlights") or []
        resps = d.get("responsibilities") or []
        achieves = d.get("achievements") or []
        if not highlights and (resps or achieves):
            d["highlights"] = list(resps) + list(achieves)
        elif highlights and not resps and not achieves:
            d["responsibilities"] = list(highlights)

        return d


# Backward-compatible alias
CVExperienceSnapshot = CVWorkSnapshot


class CVEducationSnapshot(BaseModel):
    # Canonical JSON Resume fields
    institution: str = Field(default="")
    url: Optional[str] = None
    area: Optional[str] = None
    studyType: Optional[str] = Field(None, alias="studyType")
    startDate: Optional[str] = Field(None, alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    score: Optional[str] = None
    courses: List[str] = Field(default_factory=list)

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int = 0

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_education(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        deg = d.get("degree")
        st = d.get("studyType") or d.get("study_type")
        if deg and st and deg.strip() != st.strip():
            raise ValueError(f"Conflicting fields: 'degree' ('{deg}') conflicts with 'studyType' ('{st}').")
        final_degree = st or deg
        d["studyType"] = final_degree
        d["degree"] = final_degree

        fos = d.get("field_of_study")
        area = d.get("area")
        if fos and area and fos.strip() != area.strip():
            raise ValueError(f"Conflicting fields: 'field_of_study' ('{fos}') conflicts with 'area' ('{area}').")
        final_area = area or fos
        d["area"] = final_area
        d["field_of_study"] = final_area

        start = d.get("startDate") or d.get("start_date")
        if d.get("startDate") and d.get("start_date") and d.get("startDate") != d.get("start_date"):
            raise ValueError("Conflicting fields: 'startDate' conflicts with 'start_date'.")
        d["startDate"] = start
        d["start_date"] = start

        end = d.get("endDate") or d.get("end_date")
        if d.get("endDate") and d.get("end_date") and d.get("endDate") != d.get("end_date"):
            raise ValueError("Conflicting fields: 'endDate' conflicts with 'end_date'.")
        d["endDate"] = end
        d["end_date"] = end

        score = d.get("score")
        grade = d.get("grade")
        if score and grade and score.strip() != grade.strip():
            raise ValueError(f"Conflicting fields: 'score' ('{score}') conflicts with 'grade' ('{grade}').")
        final_score = score or grade
        d["score"] = final_score
        d["grade"] = final_score

        return d


class CVSkillSnapshot(BaseModel):
    # Canonical JSON Resume fields
    name: str = Field(default="")
    level: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = None
    last_used: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    provenance: str = "user_provided"
    experience_ids: List[uuid.UUID] = Field(default_factory=list)
    project_ids: List[uuid.UUID] = Field(default_factory=list)
    certification_ids: List[uuid.UUID] = Field(default_factory=list)
    achievement_ids: List[uuid.UUID] = Field(default_factory=list)
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_skill(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        lvl = d.get("level")
        prof = d.get("proficiency")
        if lvl and prof and lvl.strip() != prof.strip():
            raise ValueError(f"Conflicting fields: 'level' ('{lvl}') conflicts with 'proficiency' ('{prof}').")
        final_lvl = lvl or prof
        d["level"] = final_lvl
        d["proficiency"] = final_lvl
        return d


class CVProjectSnapshot(BaseModel):
    # Canonical JSON Resume fields
    name: str = Field(default="")
    description: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    startDate: Optional[str] = Field(None, alias="startDate")
    endDate: Optional[str] = Field(None, alias="endDate")
    url: Optional[str] = None
    roles: List[str] = Field(default_factory=list)

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    role: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    architecture: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_size: Optional[int] = None
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    featured: bool = False
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int = 0

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_project(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        start = d.get("startDate") or d.get("start_date")
        if d.get("startDate") and d.get("start_date") and d.get("startDate") != d.get("start_date"):
            raise ValueError("Conflicting fields: 'startDate' conflicts with 'start_date'.")
        d["startDate"] = start
        d["start_date"] = start

        end = d.get("endDate") or d.get("end_date")
        if d.get("endDate") and d.get("end_date") and d.get("endDate") != d.get("end_date"):
            raise ValueError("Conflicting fields: 'endDate' conflicts with 'end_date'.")
        d["endDate"] = end
        d["end_date"] = end

        url = d.get("url") or d.get("live_url")
        if d.get("url") and d.get("live_url") and d.get("url") != d.get("live_url"):
            raise ValueError("Conflicting fields: 'url' conflicts with 'live_url'.")
        d["url"] = url
        d["live_url"] = url

        techs = d.get("technologies") or []
        kws = d.get("keywords") or []
        if not kws and techs:
            d["keywords"] = list(techs)
        elif kws and not techs:
            d["technologies"] = list(kws)

        role = d.get("role")
        roles = d.get("roles") or []
        if role and not roles:
            d["roles"] = [role]
        elif roles and not role:
            d["role"] = roles[0]

        highlights = d.get("highlights") or []
        resps = d.get("responsibilities") or []
        achieves = d.get("achievements") or []
        if not highlights and (resps or achieves):
            d["highlights"] = list(resps) + list(achieves)
        elif highlights and not resps and not achieves:
            d["responsibilities"] = list(highlights)

        return d


class CVCertificateSnapshot(BaseModel):
    # Canonical JSON Resume fields
    name: str = Field(default="")
    date: Optional[str] = None
    issuer: Optional[str] = None
    url: Optional[str] = None

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int = 0

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_certificate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        date = d.get("date") or d.get("issue_date")
        if d.get("date") and d.get("issue_date") and d.get("date") != d.get("issue_date"):
            raise ValueError("Conflicting fields: 'date' conflicts with 'issue_date'.")
        d["date"] = date
        d["issue_date"] = date

        url = d.get("url") or d.get("credential_url")
        if d.get("url") and d.get("credential_url") and d.get("url") != d.get("credential_url"):
            raise ValueError("Conflicting fields: 'url' conflicts with 'credential_url'.")
        d["url"] = url
        d["credential_url"] = url
        return d


# Backward-compatible alias
CVCertificationSnapshot = CVCertificateSnapshot


class CVAwardSnapshot(BaseModel):
    # Canonical JSON Resume fields
    title: str = Field(default="")
    date: Optional[str] = None
    awarder: Optional[str] = None
    summary: Optional[str] = None

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    description: Optional[str] = None
    issuer: Optional[str] = None
    category: Optional[str] = None
    evidence_url: Optional[str] = None
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int = 0

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_award(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        awarder = d.get("awarder") or d.get("issuer")
        if d.get("awarder") and d.get("issuer") and d.get("awarder").strip() != d.get("issuer").strip():
            raise ValueError("Conflicting fields: 'awarder' conflicts with 'issuer'.")
        d["awarder"] = awarder
        d["issuer"] = awarder

        summary = d.get("summary") or d.get("description")
        if d.get("summary") and d.get("description") and d.get("summary").strip() != d.get("description").strip():
            raise ValueError("Conflicting fields: 'summary' conflicts with 'description'.")
        d["summary"] = summary
        d["description"] = summary
        return d


# Backward-compatible alias
CVAchievementSnapshot = CVAwardSnapshot


class CVLanguageSnapshot(BaseModel):
    # Canonical JSON Resume fields
    language: str = Field(default="")
    fluency: Optional[str] = None

    # Extended Application & Legacy fields
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    name: Optional[str] = None
    proficiency: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_language(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        lang = d.get("language") or d.get("name")
        if d.get("language") and d.get("name") and d.get("language").strip() != d.get("name").strip():
            raise ValueError("Conflicting fields: 'language' conflicts with 'name'.")
        final_lang = lang or ""
        d["language"] = final_lang
        d["name"] = final_lang

        fluency = d.get("fluency") or d.get("proficiency")
        if d.get("fluency") and d.get("proficiency") and d.get("fluency").strip() != d.get("proficiency").strip():
            raise ValueError("Conflicting fields: 'fluency' conflicts with 'proficiency'.")
        d["fluency"] = fluency
        d["proficiency"] = fluency or "proficient"
        return d


class CVCareerPreferencesSnapshot(BaseModel):
    target_roles: List[str] = Field(default_factory=list)
    target_industries: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: Optional[str] = None
    employment_types: List[str] = Field(default_factory=list)
    availability_status: Optional[str] = None
    available_from: Optional[str] = None
    notice_period_days: Optional[int] = None


class CVEvidenceItemSnapshot(BaseModel):
    id: Optional[uuid.UUID] = None
    title: str = Field(default="")
    description: Optional[str] = None
    source: str = Field(default="")
    source_type: str = "link"
    url: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None
    verification_status: str = "unverified"
    provenance: str = "user_provided"
    associated_entities: List[Dict[str, Any]] = Field(default_factory=list)


# ==========================================
# Presentation & Extensions
# ==========================================

class CVPresentationSnapshot(BaseModel):
    template: str = "modern"
    typography: Optional[str] = "sans"
    color_scheme: Optional[str] = "slate"
    page_size: Optional[str] = "a4"
    spacing: Optional[str] = "normal"
    section_order: List[str] = Field(
        default_factory=lambda: [
            "basics",
            "work",
            "skills",
            "projects",
            "education",
            "certificates",
            "awards",
            "languages",
        ]
    )
    section_visibility: Dict[str, bool] = Field(
        default_factory=lambda: {
            "basics": True,
            "work": True,
            "skills": True,
            "projects": True,
            "education": True,
            "certificates": True,
            "awards": True,
            "languages": True,
        }
    )
    item_visibility: Dict[str, bool] = Field(default_factory=dict)


class CVExtensionsSnapshot(BaseModel):
    career_preferences: Optional[CVCareerPreferencesSnapshot] = None
    evidence_items: List[CVEvidenceItemSnapshot] = Field(default_factory=list)
    custom_sections: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[CVLinkSnapshot] = Field(default_factory=list)
    basics_ext: Optional[Dict[str, Any]] = None


# ==========================================
# Canonical CV Content Snapshot
# ==========================================

class CVContentSnapshot(BaseModel):
    """Complete, canonical Hybrid JSON Resume snapshot with schema versioning and backward compatibility."""

    schema_version: str = Field(default="2.0.0")
    basics: Optional[CVBasicsSnapshot] = None
    work: List[CVWorkSnapshot] = Field(default_factory=list)
    education: List[CVEducationSnapshot] = Field(default_factory=list)
    skills: List[CVSkillSnapshot] = Field(default_factory=list)
    projects: List[CVProjectSnapshot] = Field(default_factory=list)
    certificates: List[CVCertificateSnapshot] = Field(default_factory=list)
    awards: List[CVAwardSnapshot] = Field(default_factory=list)
    languages: List[CVLanguageSnapshot] = Field(default_factory=list)
    presentation: CVPresentationSnapshot = Field(default_factory=CVPresentationSnapshot)
    extensions: CVExtensionsSnapshot = Field(default_factory=CVExtensionsSnapshot)

    # Legacy backward-compatible mirrors
    experiences: Optional[List[CVWorkSnapshot]] = None
    certifications: Optional[List[CVCertificateSnapshot]] = None
    achievements: Optional[List[CVAwardSnapshot]] = None
    links: List[CVLinkSnapshot] = Field(default_factory=list)
    career_preferences: Optional[CVCareerPreferencesSnapshot] = None
    evidence_items: List[CVEvidenceItemSnapshot] = Field(default_factory=list)
    section_order: Optional[List[str]] = None
    custom_sections: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_snapshot(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        # 1. Schema Version default to 2.0.0
        if "schema_version" not in d:
            d["schema_version"] = "2.0.0"

        # 2. Work vs Experiences conflict and normalization
        work = d.get("work")
        exps = d.get("experiences")
        if exps and not work:
            work_items = [dict(item) if isinstance(item, dict) else item for item in exps]
            for item in work_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["work"] = work_items
            d["experiences"] = [dict(item) if isinstance(item, dict) else item for item in work_items]
        elif work and not exps:
            work_items = [dict(item) if isinstance(item, dict) else item for item in work]
            for item in work_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["work"] = work_items
            d["experiences"] = [dict(item) if isinstance(item, dict) else item for item in work_items]
        elif work and exps:
            if len(work) != len(exps):
                raise ValueError(
                    "Conflicting fields: both canonical 'work' and legacy 'experiences' provided with conflicting values."
                )
            for w, e in zip(work, exps):
                w_name = (w.get("name") or w.get("company") or "").strip()
                e_name = (e.get("company") or e.get("name") or "").strip()
                if w_name and e_name and w_name != e_name:
                    raise ValueError(
                        "Conflicting fields: both canonical 'work' and legacy 'experiences' provided with conflicting values."
                    )
                if isinstance(w, dict) and isinstance(e, dict):
                    common_id = w.get("id") or e.get("id") or uuid.uuid4()
                    w["id"] = common_id
                    e["id"] = common_id
            d["experiences"] = [dict(item) if isinstance(item, dict) else item for item in work]

        # 3. Certificates vs Certifications conflict and normalization
        certs = d.get("certificates")
        certifs = d.get("certifications")
        if certifs and not certs:
            cert_items = [dict(item) if isinstance(item, dict) else item for item in certifs]
            for item in cert_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["certificates"] = cert_items
            d["certifications"] = [dict(item) if isinstance(item, dict) else item for item in cert_items]
        elif certs and not certifs:
            cert_items = [dict(item) if isinstance(item, dict) else item for item in certs]
            for item in cert_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["certificates"] = cert_items
            d["certifications"] = [dict(item) if isinstance(item, dict) else item for item in cert_items]
        elif certs and certifs:
            if len(certs) != len(certifs):
                raise ValueError(
                    "Conflicting fields: both canonical 'certificates' and legacy 'certifications' provided with conflicting values."
                )
            for c, cf in zip(certs, certifs):
                c_name = (c.get("name") or "").strip()
                cf_name = (cf.get("name") or "").strip()
                if c_name and cf_name and c_name != cf_name:
                    raise ValueError(
                        "Conflicting fields: both canonical 'certificates' and legacy 'certifications' provided with conflicting values."
                    )
                if isinstance(c, dict) and isinstance(cf, dict):
                    common_id = c.get("id") or cf.get("id") or uuid.uuid4()
                    c["id"] = common_id
                    cf["id"] = common_id
            d["certifications"] = [dict(item) if isinstance(item, dict) else item for item in certs]

        # 4. Awards vs Achievements conflict and normalization
        awards = d.get("awards")
        achieves = d.get("achievements")
        if achieves and not awards:
            award_items = [dict(item) if isinstance(item, dict) else item for item in achieves]
            for item in award_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["awards"] = award_items
            d["achievements"] = [dict(item) if isinstance(item, dict) else item for item in award_items]
        elif awards and not achieves:
            award_items = [dict(item) if isinstance(item, dict) else item for item in awards]
            for item in award_items:
                if isinstance(item, dict) and not item.get("id"):
                    item["id"] = uuid.uuid4()
            d["awards"] = award_items
            d["achievements"] = [dict(item) if isinstance(item, dict) else item for item in award_items]
        elif awards and achieves:
            if len(awards) != len(achieves):
                raise ValueError(
                    "Conflicting fields: both canonical 'awards' and legacy 'achievements' provided with conflicting values."
                )
            for a, ach in zip(awards, achieves):
                a_title = (a.get("title") or "").strip()
                ach_title = (ach.get("title") or "").strip()
                if a_title and ach_title and a_title != ach_title:
                    raise ValueError(
                        "Conflicting fields: both canonical 'awards' and legacy 'achievements' provided with conflicting values."
                    )
                if isinstance(a, dict) and isinstance(ach, dict):
                    common_id = a.get("id") or ach.get("id") or uuid.uuid4()
                    a["id"] = common_id
                    ach["id"] = common_id
            d["achievements"] = [dict(item) if isinstance(item, dict) else item for item in awards]

        # 5. Presentation normalization
        pres = d.get("presentation")
        if hasattr(pres, "model_dump"):
            pres = pres.model_dump()
        if pres is None or not isinstance(pres, dict):
            pres = {}
        else:
            pres = dict(pres)

        legacy_order = d.get("section_order")
        if legacy_order and not pres.get("section_order"):
            mapped_order = []
            name_map = {
                "summary": "basics",
                "experiences": "work",
                "certifications": "certificates",
                "achievements": "awards",
            }
            for s in legacy_order:
                mapped = name_map.get(s, s)
                if mapped not in mapped_order:
                    mapped_order.append(mapped)
            pres["section_order"] = mapped_order

        d["presentation"] = pres
        d["section_order"] = pres.get("section_order")

        # 6. Extensions normalization
        ext = d.get("extensions")
        if hasattr(ext, "model_dump"):
            ext = ext.model_dump()
        if ext is None or not isinstance(ext, dict):
            ext = {}
        else:
            ext = dict(ext)

        if "career_preferences" in d and "career_preferences" not in ext:
            ext["career_preferences"] = d["career_preferences"]
        if "evidence_items" in d and "evidence_items" not in ext:
            ext["evidence_items"] = d["evidence_items"]
        if "custom_sections" in d and "custom_sections" not in ext:
            ext["custom_sections"] = d["custom_sections"]
        if "links" in d and "links" not in ext:
            ext["links"] = d["links"]

        d["extensions"] = ext
        d["career_preferences"] = ext.get("career_preferences")
        d["evidence_items"] = ext.get("evidence_items", [])
        d["custom_sections"] = ext.get("custom_sections", [])
        d["links"] = ext.get("links", [])

        return d

    def to_json_resume(self, apply_visibility: bool = False) -> Dict[str, Any]:
        """Produce standard JSON Resume schema without application-specific extensions."""
        pres = self.presentation
        item_vis = pres.item_visibility if pres else {}
        sec_vis = pres.section_visibility if pres else {}

        # 1. Basics
        basics_dict: Dict[str, Any] = {}
        if self.basics and (not apply_visibility or sec_vis.get("basics", True)):
            b = self.basics
            loc_dict = None
            if b.location:
                loc_dict = {
                    "address": b.location.address,
                    "postalCode": b.location.postal_code,
                    "city": b.location.city,
                    "countryCode": b.location.country_code,
                    "region": b.location.region,
                }
                loc_dict = {k: v for k, v in loc_dict.items() if v is not None}

            profiles_list = [
                {"network": p.network, "username": p.username, "url": p.url}
                for p in (b.profiles or [])
            ]

            basics_dict = {
                "name": b.name,
                "label": b.label,
                "image": b.image,
                "email": b.email,
                "phone": b.phone,
                "url": b.url,
                "summary": b.summary,
                "location": loc_dict,
                "profiles": profiles_list,
            }
            basics_dict = {k: v for k, v in basics_dict.items() if v is not None}

        # 2. Work
        work_list = []
        if not apply_visibility or sec_vis.get("work", True):
            for w in self.work:
                if apply_visibility and w.id and item_vis.get(str(w.id)) is False:
                    continue
                item = {
                    "name": w.name,
                    "position": w.position,
                    "url": w.url,
                    "startDate": w.startDate,
                    "endDate": w.endDate,
                    "summary": w.summary,
                    "highlights": w.highlights or (list(w.responsibilities or []) + list(w.achievements or [])),
                }
                work_list.append({k: v for k, v in item.items() if v is not None})

        # 3. Education
        edu_list = []
        if not apply_visibility or sec_vis.get("education", True):
            for e in self.education:
                if apply_visibility and e.id and item_vis.get(str(e.id)) is False:
                    continue
                item = {
                    "institution": e.institution,
                    "url": e.url,
                    "area": e.area,
                    "studyType": e.studyType,
                    "startDate": e.startDate,
                    "endDate": e.endDate,
                    "score": e.score,
                    "courses": e.courses,
                }
                edu_list.append({k: v for k, v in item.items() if v is not None})

        # 4. Skills
        skills_list = []
        if not apply_visibility or sec_vis.get("skills", True):
            for s in self.skills:
                if apply_visibility and s.id and item_vis.get(str(s.id)) is False:
                    continue
                item = {
                    "name": s.name,
                    "level": s.level,
                    "keywords": s.keywords,
                }
                skills_list.append({k: v for k, v in item.items() if v is not None})

        # 5. Projects
        projects_list = []
        if not apply_visibility or sec_vis.get("projects", True):
            for p in self.projects:
                if apply_visibility and p.id and item_vis.get(str(p.id)) is False:
                    continue
                item = {
                    "name": p.name,
                    "description": p.description,
                    "highlights": p.highlights or (list(p.responsibilities or []) + list(p.achievements or [])),
                    "keywords": p.keywords or list(p.technologies or []),
                    "startDate": p.startDate,
                    "endDate": p.endDate,
                    "url": p.url or p.live_url,
                    "roles": p.roles or ([p.role] if p.role else []),
                }
                projects_list.append({k: v for k, v in item.items() if v is not None})

        # 6. Certificates
        certs_list = []
        if not apply_visibility or sec_vis.get("certificates", True):
            for c in self.certificates:
                if apply_visibility and c.id and item_vis.get(str(c.id)) is False:
                    continue
                item = {
                    "name": c.name,
                    "date": c.date,
                    "issuer": c.issuer,
                    "url": c.url,
                }
                certs_list.append({k: v for k, v in item.items() if v is not None})

        # 7. Awards
        awards_list = []
        if not apply_visibility or sec_vis.get("awards", True):
            for a in self.awards:
                if apply_visibility and a.id and item_vis.get(str(a.id)) is False:
                    continue
                item = {
                    "title": a.title,
                    "date": a.date,
                    "awarder": a.awarder,
                    "summary": a.summary,
                }
                awards_list.append({k: v for k, v in item.items() if v is not None})

        # 8. Languages
        langs_list = []
        if not apply_visibility or sec_vis.get("languages", True):
            for l in self.languages:
                if apply_visibility and l.id and item_vis.get(str(l.id)) is False:
                    continue
                item = {
                    "language": l.language,
                    "fluency": l.fluency,
                }
                langs_list.append({k: v for k, v in item.items() if v is not None})

        return {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": basics_dict,
            "work": work_list,
            "education": edu_list,
            "skills": skills_list,
            "projects": projects_list,
            "certificates": certs_list,
            "awards": awards_list,
            "languages": langs_list,
        }


# ==========================================
# CV Version Request & Response Schemas
# ==========================================

class CVVersionCreate(BaseModel):
    """Payload to create a new CV Version derived from the user's master CandidateProfile."""

    name: str = Field(..., min_length=1, max_length=200, description="Version name e.g. 'Senior Full-Stack Engineer - Stripe'")
    job_target_id: Optional[uuid.UUID] = Field(None, description="Optional job target opportunity to link")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Version name cannot be empty or whitespace.")
            return v_strip
        return v


class CVVersionUpdate(BaseModel):
    """Payload to update version metadata and/or version-specific content snapshot."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    job_target_id: Optional[uuid.UUID] = None
    status: Optional[CVVersionStatus] = None
    content_snapshot: Optional[CVContentSnapshot] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Version name cannot be empty or whitespace.")
            return v_strip
        return v


class CVVersionDuplicate(BaseModel):
    """Payload to duplicate an existing CV Version."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Optional custom name for duplicate")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            return v_strip if v_strip else None
        return v


class CVVersionSummaryResponse(BaseModel):
    """Lightweight response model for listing CV versions."""

    id: uuid.UUID
    user_id: uuid.UUID
    job_target_id: Optional[uuid.UUID] = None
    job_target_title: Optional[str] = None
    job_target_company: Optional[str] = None
    name: str
    status: CVVersionStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CVVersionResponse(BaseModel):
    """Full response model for a single CV version, containing full content snapshot."""

    id: uuid.UUID
    user_id: uuid.UUID
    job_target_id: Optional[uuid.UUID] = None
    job_target_title: Optional[str] = None
    job_target_company: Optional[str] = None
    name: str
    status: CVVersionStatus
    content_snapshot: CVContentSnapshot
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CVVersionListResponse(BaseModel):
    """Paginated list response model for CV versions."""

    items: List[CVVersionSummaryResponse]
    total: int
    limit: int
    offset: int
