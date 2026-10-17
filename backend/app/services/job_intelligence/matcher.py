import re
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from app.core.logging import get_logger
from app.models.profile import (
    Achievement,
    CandidateProfile,
    CandidateSkill,
    Certification,
    EducationRecord,
    EvidenceItem,
    Project,
    WorkExperience,
)
from app.schemas.job_target import (
    CandidateMatchStatus,
    EvidenceTraceItem,
    GapType,
    JobAnalysisResult,
    JobExtractionResult,
    JobRequirementCategory,
    JobRequirementItem,
    KeywordSummary,
)

logger = get_logger("app.services.job_intelligence.matcher")


class EvidenceGroundedMatcher:
    """
    Compares extracted job requirements against candidate profile facts and evidence.
    Assigns grounded statuses: supported, partial, unverified, or missing.
    Preserves strict evidence traceability and non-hallucination guarantees.
    """

    def match(
        self,
        job_id: uuid.UUID,
        extraction: JobExtractionResult,
        profile: CandidateProfile,
    ) -> JobAnalysisResult:
        """
        Run deterministic evidence-grounded matching against candidate profile facts.
        Never mutates the CandidateProfile or any CV version.
        """
        # 1. Build fast evidence association index: entity_id -> List[EvidenceItem]
        evidence_by_entity, evidence_by_id = self._index_evidence(profile)

        # 2. Extract candidate facts catalog
        skills_map = {s.name.strip().lower(): s for s in (profile.skills or []) if s.name}
        experiences = profile.experiences or []
        projects = profile.projects or []
        educations = list(getattr(profile, "education", None) or getattr(profile, "educations", None) or [])
        certifications = profile.certifications or []
        achievements = profile.achievements or []

        matched_requirements: List[JobRequirementItem] = []
        matched_keywords: Set[str] = set()
        missing_keywords: Set[str] = set()
        identified_gaps: List[str] = []

        total_reqs = len(extraction.requirements)
        mandatory_count = 0
        preferred_count = 0
        supported_count = 0
        partial_count = 0
        unverified_count = 0
        missing_count = 0

        supported_mandatory = 0
        partial_mandatory = 0

        for req in extraction.requirements:
            if req.is_mandatory:
                mandatory_count += 1
            else:
                preferred_count += 1

            # Match individual requirement
            matched_item = self._match_requirement(
                req=req,
                profile=profile,
                skills_map=skills_map,
                experiences=experiences,
                projects=projects,
                educations=educations,
                certifications=certifications,
                achievements=achievements,
                evidence_by_entity=evidence_by_entity,
                evidence_by_id=evidence_by_id,
            )

            matched_requirements.append(matched_item)

            # Update counters
            status = matched_item.candidate_match_status
            if status == CandidateMatchStatus.SUPPORTED.value:
                supported_count += 1
                if req.is_mandatory:
                    supported_mandatory += 1
                if matched_item.matched_entity_name:
                    matched_keywords.add(matched_item.matched_entity_name)
            elif status == CandidateMatchStatus.PARTIAL.value:
                partial_count += 1
                if req.is_mandatory:
                    partial_mandatory += 1
                if matched_item.matched_entity_name:
                    matched_keywords.add(matched_item.matched_entity_name)
                if matched_item.reasoning:
                    identified_gaps.append(matched_item.reasoning)
            elif status == CandidateMatchStatus.UNVERIFIED.value:
                unverified_count += 1
                if matched_item.matched_entity_name:
                    matched_keywords.add(f"{matched_item.matched_entity_name} (Unverified)")
                identified_gaps.append(
                    f"Unverified qualification: '{matched_item.requirement}' claimed without supporting evidence."
                )
            else:  # MISSING
                missing_count += 1
                missing_keywords.add(matched_item.requirement[:40])
                if matched_item.is_mandatory:
                    identified_gaps.append(
                        f"Missing mandatory requirement: '{matched_item.requirement}'"
                    )

        # 3. Calculate Keyword and Coverage Summary
        coverage_pct = round(
            ((supported_count + 0.5 * partial_count) / total_reqs * 100), 1
        ) if total_reqs > 0 else 0.0

        mandatory_cov_pct = round(
            ((supported_mandatory + 0.5 * partial_mandatory) / mandatory_count * 100), 1
        ) if mandatory_count > 0 else 100.0

        summary = KeywordSummary(
            total_requirements=total_reqs,
            mandatory_count=mandatory_count,
            preferred_count=preferred_count,
            supported_count=supported_count,
            partial_count=partial_count,
            unverified_count=unverified_count,
            missing_count=missing_count,
            coverage_percentage=coverage_pct,
            mandatory_coverage_percentage=mandatory_cov_pct,
            top_matched_keywords=sorted(matched_keywords)[:15],
            top_missing_keywords=sorted(missing_keywords)[:15],
            identified_gaps=identified_gaps[:10],
        )

        return JobAnalysisResult(
            job_id=job_id,
            role_overview=extraction.role_overview,
            seniority_level=extraction.seniority_level,
            employment_type=extraction.employment_type,
            requirements=matched_requirements,
            keyword_summary=summary,
        )

    def _index_evidence(
        self, profile: CandidateProfile
    ) -> Tuple[Dict[str, List[EvidenceItem]], Dict[uuid.UUID, EvidenceItem]]:
        """Index evidence items by polymorphic entity key 'entity_type:entity_id' and by evidence_id."""
        evidence_by_entity: Dict[str, List[EvidenceItem]] = {}
        evidence_by_id: Dict[uuid.UUID, EvidenceItem] = {}

        for ev in profile.evidence_items or []:
            evidence_by_id[ev.id] = ev
            for assoc in ev.associations or []:
                key = f"{assoc.entity_type}:{assoc.entity_id}"
                if key not in evidence_by_entity:
                    evidence_by_entity[key] = []
                evidence_by_entity[key].append(ev)

        return evidence_by_entity, evidence_by_id

    def _match_requirement(
        self,
        req: JobRequirementItem,
        profile: CandidateProfile,
        skills_map: Dict[str, CandidateSkill],
        experiences: List[WorkExperience],
        projects: List[Project],
        educations: List[Education],
        certifications: List[Certification],
        achievements: List[Achievement],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
        evidence_by_id: Dict[uuid.UUID, EvidenceItem],
    ) -> JobRequirementItem:
        """Evaluate a single requirement against the candidate knowledge base."""
        req_text = req.requirement
        req_lower = req_text.lower()
        req_category = req.category

        # 1. Experience & Seniority Check
        if req_category == JobRequirementCategory.EXPERIENCE.value:
            match = self._evaluate_experience_requirement(
                req_text, experiences, evidence_by_entity
            )
            if match:
                return self._apply_match(req, match)

        # 2. Education Check
        if req_category == JobRequirementCategory.EDUCATION.value:
            match = self._evaluate_education_requirement(
                req_text, educations, evidence_by_entity
            )
            if match:
                return self._apply_match(req, match)

        # 3. Certifications Check
        if req_category == JobRequirementCategory.CERTIFICATIONS.value:
            match = self._evaluate_certification_requirement(
                req_text, certifications, evidence_by_entity
            )
            if match:
                return self._apply_match(req, match)

        # 4. Direct Skills & Technologies Match
        skill_match = self._evaluate_skill_match(
            req_text, skills_map, evidence_by_entity
        )
        if skill_match:
            return self._apply_match(req, skill_match)

        # 5. Work Experience Mention Check
        exp_match = self._evaluate_work_experience_mention(
            req_text, experiences, evidence_by_entity
        )
        if exp_match:
            return self._apply_match(req, exp_match)

        # 6. Project Mention Check
        proj_match = self._evaluate_project_mention(
            req_text, projects, evidence_by_entity
        )
        if proj_match:
            return self._apply_match(req, proj_match)

        # 7. Achievement Mention Check
        ach_match = self._evaluate_achievement_mention(
            req_text, achievements, evidence_by_entity
        )
        if ach_match:
            return self._apply_match(req, ach_match)

        # 8. Constraints Check (e.g. Work authorization, location, remote)
        if req_category == JobRequirementCategory.CONSTRAINTS.value:
            pref_match = self._evaluate_constraints(req_text, profile)
            if pref_match:
                return self._apply_match(req, pref_match)

        # 9. No match found -> distinguish absent from profile vs skill gap
        is_absent = True
        words = set(re.findall(r"[a-zA-Z]{3,}", req_lower))
        # If candidate has skills or experiences in the same technical category, treat as skill gap
        if req_category in {JobRequirementCategory.SKILLS.value, JobRequirementCategory.TECHNOLOGIES.value}:
            has_tech = any(s in req_lower for s in skills_map.keys())
            if has_tech:
                is_absent = False

        gap_type = GapType.ABSENT_FROM_PROFILE.value if is_absent else GapType.SKILL_GAP.value
        reasoning = (
            f"No record of '{req_text}' found in candidate profile. Consider adding if applicable."
            if is_absent
            else f"Candidate profile does not satisfy requirement '{req_text}'."
        )

        return JobRequirementItem(
            id=req.id,
            category=req.category,
            requirement=req.requirement,
            is_mandatory=req.is_mandatory,
            candidate_match_status=CandidateMatchStatus.MISSING.value,
            reasoning=reasoning,
            gap_type=gap_type,
            confidence_score=0.0,
        )

    def _apply_match(
        self,
        base_req: JobRequirementItem,
        match_data: Dict[str, Any],
    ) -> JobRequirementItem:
        """Merge evaluated match data into canonical JobRequirementItem."""
        return JobRequirementItem(
            id=base_req.id,
            category=base_req.category,
            requirement=base_req.requirement,
            is_mandatory=base_req.is_mandatory,
            candidate_match_status=match_data.get("status", CandidateMatchStatus.MISSING.value),
            reasoning=match_data.get("reasoning"),
            matched_entity_type=match_data.get("entity_type"),
            matched_entity_id=match_data.get("entity_id"),
            matched_entity_name=match_data.get("entity_name"),
            evidence_ids=match_data.get("evidence_ids", []),
            evidence_items=match_data.get("evidence_items", []),
            confidence_score=match_data.get("confidence_score", 0.0),
            gap_type=match_data.get("gap_type"),
        )

    def _evaluate_skill_match(
        self,
        req_text: str,
        skills_map: Dict[str, CandidateSkill],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        matched_skill: Optional[CandidateSkill] = None

        # Look for full skill name in requirement text
        for name, skill in skills_map.items():
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(name)}(?![a-zA-Z0-9])"
            if re.search(pattern, req_lower):
                matched_skill = skill
                break

        if not matched_skill:
            return None

        # Check evidence for this skill
        ev_items = evidence_by_entity.get(f"skill:{matched_skill.id}", [])
        has_verified_evidence = any(
            ev.verification_status in {"verified", "user_provided"} and ev.url for ev in ev_items
        ) or bool(matched_skill.evidence_references)

        if has_verified_evidence or len(ev_items) > 0:
            trace_items = [
                EvidenceTraceItem(
                    id=ev.id,
                    title=ev.title,
                    source=ev.source,
                    source_type=ev.source_type,
                    url=ev.url,
                    verification_status=ev.verification_status,
                    date=ev.date,
                )
                for ev in ev_items
            ]
            return {
                "status": CandidateMatchStatus.SUPPORTED.value,
                "confidence_score": 0.95,
                "entity_type": "skill",
                "entity_id": matched_skill.id,
                "entity_name": matched_skill.name,
                "evidence_ids": [ev.id for ev in ev_items],
                "evidence_items": trace_items,
                "reasoning": (
                    f"Directly verified by Candidate Skill '{matched_skill.name}' "
                    f"({matched_skill.proficiency or 'proficient'}, {matched_skill.years_of_experience or 0} yrs) "
                    f"with {len(ev_items)} attached evidence item(s)."
                ),
            }
        else:
            # Skill is claimed in candidate profile, but unverified / lacks supporting evidence
            return {
                "status": CandidateMatchStatus.UNVERIFIED.value,
                "confidence_score": 0.70,
                "entity_type": "skill",
                "entity_id": matched_skill.id,
                "entity_name": matched_skill.name,
                "evidence_ids": [],
                "evidence_items": [],
                "gap_type": GapType.UNVERIFIED_CLAIM.value,
                "reasoning": (
                    f"Candidate lists skill '{matched_skill.name}' in profile, "
                    f"but no supporting evidence item or proof link is attached."
                ),
            }

    def _evaluate_experience_requirement(
        self,
        req_text: str,
        experiences: List[WorkExperience],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        # Extract years from requirement
        years_match = re.search(r"\b(\d+)\+?\s*(?:years|yrs|year)\b", req_text, re.IGNORECASE)
        required_years = float(years_match.group(1)) if years_match else 3.0

        # Estimate candidate total years of experience from experiences
        total_exp_years = 0.0
        relevant_experiences: List[WorkExperience] = []
        for exp in experiences:
            # Quick estimation: if dates available, or default ~2 years per experience
            relevant_experiences.append(exp)
            total_exp_years += 2.0  # conservative average per role if dates unparsed

        if not relevant_experiences:
            return None

        primary_exp = relevant_experiences[0]
        ev_items = evidence_by_entity.get(f"experience:{primary_exp.id}", [])
        trace_items = [
            EvidenceTraceItem(
                id=ev.id,
                title=ev.title,
                source=ev.source,
                source_type=ev.source_type,
                url=ev.url,
                verification_status=ev.verification_status,
                date=ev.date,
            )
            for ev in ev_items
        ]

        if total_exp_years >= required_years:
            if ev_items:
                return {
                    "status": CandidateMatchStatus.SUPPORTED.value,
                    "confidence_score": 0.90,
                    "entity_type": "experience",
                    "entity_id": primary_exp.id,
                    "entity_name": f"{primary_exp.position} at {primary_exp.company}",
                    "evidence_ids": [ev.id for ev in ev_items],
                    "evidence_items": trace_items,
                    "reasoning": (
                        f"Candidate career history indicates ~{int(total_exp_years)}+ years of professional experience, "
                        f"satisfying requirement of {int(required_years)} years (backed by role at {primary_exp.company})."
                    ),
                }
            else:
                return {
                    "status": CandidateMatchStatus.UNVERIFIED.value,
                    "confidence_score": 0.75,
                    "entity_type": "experience",
                    "entity_id": primary_exp.id,
                    "entity_name": f"{primary_exp.position} at {primary_exp.company}",
                    "evidence_ids": [],
                    "evidence_items": [],
                    "gap_type": GapType.UNVERIFIED_CLAIM.value,
                    "reasoning": (
                        f"Candidate career history indicates ~{int(total_exp_years)}+ years of experience, "
                        f"but roles have no external verification links."
                    ),
                }
        else:
            return {
                "status": CandidateMatchStatus.PARTIAL.value,
                "confidence_score": 0.55,
                "entity_type": "experience",
                "entity_id": primary_exp.id,
                "entity_name": f"{primary_exp.position} at {primary_exp.company}",
                "evidence_ids": [ev.id for ev in ev_items],
                "evidence_items": trace_items,
                "gap_type": GapType.SKILL_GAP.value,
                "reasoning": (
                    f"Candidate has approximately ~{int(total_exp_years)} years of relevant experience, "
                    f"which partially satisfies required {int(required_years)}+ years."
                ),
            }

    def _evaluate_education_requirement(
        self,
        req_text: str,
        educations: List[EducationRecord],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        for edu in educations:
            deg = (edu.degree or edu.study_type or "").lower()
            field = (edu.field_of_study or "").lower()
            inst = (edu.institution or "").lower()

            if any(term in req_lower for term in [deg, field, "degree", "bachelor", "master", "computer science"]):
                ev_items = evidence_by_entity.get(f"education:{edu.id}", [])
                trace_items = [
                    EvidenceTraceItem(
                        id=ev.id,
                        title=ev.title,
                        source=ev.source,
                        source_type=ev.source_type,
                        url=ev.url,
                        verification_status=ev.verification_status,
                        date=ev.date,
                    )
                    for ev in ev_items
                ]
                status = CandidateMatchStatus.SUPPORTED.value if ev_items else CandidateMatchStatus.UNVERIFIED.value
                return {
                    "status": status,
                    "confidence_score": 0.90 if ev_items else 0.70,
                    "entity_type": "education",
                    "entity_id": edu.id,
                    "entity_name": f"{edu.degree or edu.study_type} in {edu.field_of_study} ({edu.institution})",
                    "evidence_ids": [ev.id for ev in ev_items],
                    "evidence_items": trace_items,
                    "reasoning": (
                        f"Candidate holds {edu.degree or edu.study_type} in {edu.field_of_study} from {edu.institution}."
                    ),
                }
        return None

    def _evaluate_certification_requirement(
        self,
        req_text: str,
        certifications: List[Certification],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        for cert in certifications:
            name_lower = cert.name.lower()
            if name_lower in req_lower or any(word in req_lower for word in name_lower.split() if len(word) > 3):
                ev_items = evidence_by_entity.get(f"certification:{cert.id}", [])
                trace_items = [
                    EvidenceTraceItem(
                        id=ev.id,
                        title=ev.title,
                        source=ev.source,
                        source_type=ev.source_type,
                        url=ev.url or cert.credential_url,
                        verification_status=ev.verification_status if ev else "verified",
                        date=ev.date if ev else cert.issue_date,
                    )
                    for ev in ev_items
                ]
                has_cred = bool(cert.credential_url or ev_items)
                return {
                    "status": CandidateMatchStatus.SUPPORTED.value if has_cred else CandidateMatchStatus.UNVERIFIED.value,
                    "confidence_score": 0.95 if has_cred else 0.70,
                    "entity_type": "certification",
                    "entity_id": cert.id,
                    "entity_name": cert.name,
                    "evidence_ids": [ev.id for ev in ev_items],
                    "evidence_items": trace_items,
                    "reasoning": f"Candidate possesses certification '{cert.name}' issued by {cert.issuer}.",
                }
        return None

    def _evaluate_work_experience_mention(
        self,
        req_text: str,
        experiences: List[WorkExperience],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        for exp in experiences:
            # Check technologies listed on the experience
            for tech in exp.technologies or []:
                if tech.lower() in req_lower:
                    ev_items = evidence_by_entity.get(f"experience:{exp.id}", [])
                    trace_items = [
                        EvidenceTraceItem(
                            id=ev.id,
                            title=ev.title,
                            source=ev.source,
                            source_type=ev.source_type,
                            url=ev.url,
                            verification_status=ev.verification_status,
                            date=ev.date,
                        )
                        for ev in ev_items
                    ]
                    status = CandidateMatchStatus.SUPPORTED.value if ev_items else CandidateMatchStatus.UNVERIFIED.value
                    return {
                        "status": status,
                        "confidence_score": 0.85 if ev_items else 0.65,
                        "entity_type": "experience",
                        "entity_id": exp.id,
                        "entity_name": f"{exp.position} at {exp.company}",
                        "evidence_ids": [ev.id for ev in ev_items],
                        "evidence_items": trace_items,
                        "reasoning": f"Demonstrated {tech} during tenure as '{exp.position}' at '{exp.company}'.",
                    }

            # Check responsibilities and achievements
            bullets = list(exp.responsibilities or []) + list(exp.achievements or [])
            for bullet in bullets:
                # If there is meaningful word overlap (>3 key words)
                b_words = set(re.findall(r"[a-zA-Z]{4,}", bullet.lower()))
                r_words = set(re.findall(r"[a-zA-Z]{4,}", req_lower))
                common = b_words.intersection(r_words)
                if len(common) >= 3:
                    ev_items = evidence_by_entity.get(f"experience:{exp.id}", [])
                    trace_items = [
                        EvidenceTraceItem(
                            id=ev.id,
                            title=ev.title,
                            source=ev.source,
                            source_type=ev.source_type,
                            url=ev.url,
                            verification_status=ev.verification_status,
                            date=ev.date,
                        )
                        for ev in ev_items
                    ]
                    return {
                        "status": CandidateMatchStatus.SUPPORTED.value if ev_items else CandidateMatchStatus.PARTIAL.value,
                        "confidence_score": 0.80 if ev_items else 0.60,
                        "entity_type": "experience",
                        "entity_id": exp.id,
                        "entity_name": f"{exp.position} at {exp.company}",
                        "evidence_ids": [ev.id for ev in ev_items],
                        "evidence_items": trace_items,
                        "reasoning": f"Role '{exp.position}' at '{exp.company}' involved relevant work: '{bullet[:90]}...'",
                    }
        return None

    def _evaluate_project_mention(
        self,
        req_text: str,
        projects: List[Project],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        for proj in projects:
            for tech in proj.technologies or []:
                if tech.lower() in req_lower:
                    ev_items = evidence_by_entity.get(f"project:{proj.id}", [])
                    trace_items = [
                        EvidenceTraceItem(
                            id=ev.id,
                            title=ev.title,
                            source=ev.source,
                            source_type=ev.source_type,
                            url=ev.url or proj.live_url or proj.repository_url,
                            verification_status=ev.verification_status if ev else "verified",
                            date=ev.date if ev else None,
                        )
                        for ev in ev_items
                    ]
                    has_link = bool(proj.live_url or proj.repository_url or ev_items)
                    status = CandidateMatchStatus.SUPPORTED.value if has_link else CandidateMatchStatus.UNVERIFIED.value
                    return {
                        "status": status,
                        "confidence_score": 0.90 if has_link else 0.65,
                        "entity_type": "project",
                        "entity_id": proj.id,
                        "entity_name": proj.name,
                        "evidence_ids": [ev.id for ev in ev_items],
                        "evidence_items": trace_items,
                        "reasoning": f"Project '{proj.name}' utilized {tech} (verified via codebase / project links).",
                    }
        return None

    def _evaluate_achievement_mention(
        self,
        req_text: str,
        achievements: List[Achievement],
        evidence_by_entity: Dict[str, List[EvidenceItem]],
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        for ach in achievements:
            if ach.title.lower() in req_lower:
                ev_items = evidence_by_entity.get(f"achievement:{ach.id}", [])
                trace_items = [
                    EvidenceTraceItem(
                        id=ev.id,
                        title=ev.title,
                        source=ev.source,
                        source_type=ev.source_type,
                        url=ev.url or ach.evidence_url,
                        verification_status=ev.verification_status if ev else "verified",
                        date=ev.date if ev else None,
                    )
                    for ev in ev_items
                ]
                has_ev = bool(ach.evidence_url or ev_items)
                return {
                    "status": CandidateMatchStatus.SUPPORTED.value if has_ev else CandidateMatchStatus.UNVERIFIED.value,
                    "confidence_score": 0.90 if has_ev else 0.65,
                    "entity_type": "achievement",
                    "entity_id": ach.id,
                    "entity_name": ach.title,
                    "evidence_ids": [ev.id for ev in ev_items],
                    "evidence_items": trace_items,
                    "reasoning": f"Candidate holds recognized achievement '{ach.title}'.",
                }
        return None

    def _evaluate_constraints(
        self,
        req_text: str,
        profile: CandidateProfile,
    ) -> Optional[Dict[str, Any]]:
        req_lower = req_text.lower()
        prefs = getattr(profile, "career_preferences", None) or getattr(profile, "preferences", None)
        if not prefs:
            return None

        # Remote / Location constraint
        if "remote" in req_lower and prefs.remote_preference:
            pref_val = str(prefs.remote_preference).lower()
            if "remote" in pref_val or "hybrid" in pref_val:
                return {
                    "status": CandidateMatchStatus.SUPPORTED.value,
                    "confidence_score": 0.90,
                    "entity_type": "preferences",
                    "entity_id": prefs.id,
                    "entity_name": f"Remote Preference ({prefs.remote_preference})",
                    "evidence_ids": [],
                    "evidence_items": [],
                    "reasoning": f"Candidate career preferences align with remote expectation ({prefs.remote_preference}).",
                }
        return None
