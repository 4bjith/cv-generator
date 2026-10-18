import copy
from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.cv_version import CVVersion
from app.models.job_target import JobTarget
from app.models.profile import CandidateProfile
from app.repositories.interfaces.cv_version_repository import ICVVersionRepository
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.cv_version_repository import PostgresCVVersionRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.ats import (
    ApplyATSSuggestionsRequest,
    ApplyATSSuggestionsResponse,
    ATSAnalysisResponse,
    ATSCheckCategory,
    ATSCheckItem,
    ATSCheckSeverity,
    ATSComponentScore,
    GroundedKeywordSuggestion,
    KeywordOccurrenceItem,
)
from app.schemas.cv import CVContentSnapshot, CVSkillSnapshot, CVVersionCreate

logger = get_logger("app.services.ats")

# Standard stop words to ignore when extracting job keywords
COMMON_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
    "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "will", "work", "experience", "role", "team", "looking", "responsibilities", "requirements",
    "qualifications", "company", "candidate", "years", "join", "apply", "opportunity",
}


class ATSService:
    """
    Explainable ATS Analysis Engine & Grounded Keyword Optimization Service.
    Evaluates CVVersion snapshots against optional JobTargets without mutating source records.
    """

    def __init__(
        self,
        cv_version_repository: ICVVersionRepository,
        job_target_repository: IJobTargetRepository,
        profile_repository: IProfileRepository,
        db_session: AsyncSession,
    ):
        self.cv_repo = cv_version_repository
        self.job_repo = job_target_repository
        self.profile_repo = profile_repository
        self.session = db_session

    async def analyze_cv_version(
        self,
        user_id: Union[uuid.UUID, str],
        cv_version_id: Union[uuid.UUID, str],
        job_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> ATSAnalysisResponse:
        """
        Run transparent, explainable ATS analysis evaluating CV structure, format friction,
        keyword density, and job requirement coverage.
        """
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        vid = uuid.UUID(str(cv_version_id)) if isinstance(cv_version_id, str) else cv_version_id

        # 1. Ownership & existence check for CVVersion
        cv_version = await self.cv_repo.get_by_id(version_id=vid, user_id=uid)
        if not cv_version:
            raise NotFoundError(
                message="CV version not found or you do not have permission to access it.",
                code="CV_VERSION_NOT_FOUND",
            )

        # 2. Ownership & existence check for JobTarget if specified
        job_target: Optional[JobTarget] = None
        target_job_id = job_id or cv_version.job_target_id
        if target_job_id:
            jid = uuid.UUID(str(target_job_id)) if isinstance(target_job_id, str) else target_job_id
            job_target = await self.job_repo.get_by_id(job_id=jid, user_id=uid)
            if not job_target and job_id:
                raise NotFoundError(
                    message="Target job not found or you do not have permission to access it.",
                    code="JOB_TARGET_NOT_FOUND",
                )

        snapshot: Dict[str, Any] = cv_version.content_snapshot or {}

        # 3. Text and section extraction
        section_texts, full_text, word_list = self._extract_cv_text(snapshot)
        total_words = len(word_list)

        # 4. Run structural, formatting, and parsing friction checks
        checks = self._run_parser_checks(snapshot, section_texts, word_list)

        # 5. Extract target keywords and run occurrence & density analysis
        keywords_analysis, keyword_checks = self._analyze_keywords(
            job_target=job_target,
            full_text=full_text,
            section_texts=section_texts,
            total_words=total_words,
        )
        checks.extend(keyword_checks)

        # 6. Calculate explainable component scores
        components, overall_score, scoring_mode = self._calculate_scores(
            job_target=job_target,
            checks=checks,
            keywords=keywords_analysis,
            snapshot=snapshot,
            total_words=total_words,
        )

        # 7. Generate candidate-grounded keyword optimization suggestions
        suggestions = await self._generate_grounded_suggestions(
            user_id=uid,
            job_target=job_target,
            keywords=keywords_analysis,
            snapshot=snapshot,
        )

        # Calculate coverage metric
        matched_kws = [k for k in keywords_analysis if k.is_present]
        coverage_pct = round((len(matched_kws) / max(len(keywords_analysis), 1)) * 100.0, 1)

        return ATSAnalysisResponse(
            id=f"ats-{vid}-{uuid.uuid4().hex[:8]}",
            cv_version_id=vid,
            cv_version_name=cv_version.name,
            job_id=job_target.id if job_target else None,
            job_title=job_target.title if job_target else None,
            company_name=job_target.company_name if job_target else None,
            overall_score=overall_score,
            scoring_mode=scoring_mode,
            components=components,
            keyword_coverage_percentage=coverage_pct,
            total_words=total_words,
            checks=checks,
            keywords=keywords_analysis,
            suggestions=suggestions,
            analyzed_at=datetime.now(timezone.utc),
        )

    async def apply_suggestions(
        self,
        user_id: Union[uuid.UUID, str],
        data: ApplyATSSuggestionsRequest,
    ) -> ApplyATSSuggestionsResponse:
        """
        Apply accepted keyword optimizations by creating a new independent CVVersion snapshot.
        Strictly prevents injecting ungrounded/hallucinated skills into the candidate's CV.
        """
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        vid = uuid.UUID(str(data.cv_version_id)) if isinstance(data.cv_version_id, str) else data.cv_version_id

        # 1. Validate ownership of source CVVersion
        source_version = await self.cv_repo.get_by_id(version_id=vid, user_id=uid)
        if not source_version:
            raise NotFoundError(
                message="Source CV version not found or unauthorized.",
                code="CV_VERSION_NOT_FOUND",
            )

        target_job_id = data.job_id or source_version.job_target_id

        # 2. Run analysis to retrieve valid grounded suggestions
        analysis = await self.analyze_cv_version(
            user_id=uid,
            cv_version_id=vid,
            job_id=target_job_id,
        )

        accepted_set = set(data.accepted_suggestion_ids)
        accepted_lower = {x.lower() for x in data.accepted_suggestion_ids}
        valid_suggestions = [
            s for s in analysis.suggestions
            if (s.id in accepted_set or s.keyword.lower() in accepted_lower or f"sugg-{s.keyword.lower()}" in accepted_lower)
            and s.is_grounded_in_profile
        ]

        if not valid_suggestions:
            raise ValidationError(
                message="No valid, profile-grounded suggestions selected for application.",
                code="NO_VALID_SUGGESTIONS",
            )

        # 3. Deep-clone snapshot to preserve source version immutability
        new_snapshot = copy.deepcopy(source_version.content_snapshot or {})
        existing_skills: List[Dict[str, Any]] = new_snapshot.get("skills") or []
        existing_skill_names = {
            s.get("name", "").strip().lower() for s in existing_skills if isinstance(s, dict)
        }

        applied_count = 0
        for suggestion in valid_suggestions:
            kw = suggestion.keyword.strip()
            if kw.lower() not in existing_skill_names:
                existing_skills.append({
                    "name": kw,
                    "level": "competent",
                    "proficiency": "competent",
                    "category": "Technologies",
                    "keywords": [kw],
                })
                existing_skill_names.add(kw.lower())
                applied_count += 1

        new_snapshot["skills"] = existing_skills

        # 4. Persist as an independent CVVersion
        new_name = data.new_version_name or f"{source_version.name} - ATS Optimized"
        new_version = CVVersion(
            id=uuid.uuid4(),
            user_id=uid,
            job_target_id=target_job_id,
            name=new_name,
            status="ready",
            content_snapshot=new_snapshot,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        created_version = await self.cv_repo.create(new_version)
        snapshot_model = CVContentSnapshot.model_validate(created_version.content_snapshot or {})

        logger.info(
            f"Created ATS-optimized CVVersion {created_version.id} with {applied_count} grounded suggestions."
        )

        return ApplyATSSuggestionsResponse(
            original_version_id=source_version.id,
            new_version_id=created_version.id,
            new_version_name=created_version.name,
            applied_suggestions_count=applied_count,
            content_snapshot=snapshot_model,
            created_at=created_version.created_at,
        )

    # -------------------------------------------------------------------------
    # Internal Engine Methods
    # -------------------------------------------------------------------------

    def _extract_cv_text(
        self, snapshot: Dict[str, Any]
    ) -> Tuple[Dict[str, str], str, List[str]]:
        """Extract structured text per section, overall text, and tokenized words."""
        section_texts: Dict[str, str] = {
            "basics": "",
            "summary": "",
            "work": "",
            "education": "",
            "skills": "",
            "projects": "",
            "certifications": "",
        }

        # Basics & summary
        basics = snapshot.get("basics") or {}
        basics_parts = [
            basics.get("name") or "",
            basics.get("label") or "",
            basics.get("email") or "",
            basics.get("phone") or "",
        ]
        loc = basics.get("location")
        if isinstance(loc, dict):
            basics_parts.extend([loc.get("city") or "", loc.get("country") or ""])
        section_texts["basics"] = " ".join(filter(None, basics_parts))

        summary = basics.get("summary") or basics.get("base_summary") or ""
        section_texts["summary"] = summary

        # Work
        work_entries = snapshot.get("work") or snapshot.get("work_experience") or []
        work_parts = []
        for w in work_entries:
            if isinstance(w, dict):
                work_parts.append(w.get("name") or w.get("company") or "")
                work_parts.append(w.get("position") or w.get("title") or "")
                work_parts.append(w.get("summary") or "")
                for hl in (w.get("highlights") or w.get("responsibilities") or []):
                    work_parts.append(str(hl))
                for ach in (w.get("achievements") or []):
                    work_parts.append(str(ach))
                for tech in (w.get("technologies") or []):
                    work_parts.append(str(tech))
        section_texts["work"] = " ".join(filter(None, work_parts))

        # Education
        edu_entries = snapshot.get("education") or []
        edu_parts = []
        for e in edu_entries:
            if isinstance(e, dict):
                edu_parts.append(e.get("institution") or "")
                edu_parts.append(e.get("area") or "")
                edu_parts.append(e.get("studyType") or "")
        section_texts["education"] = " ".join(filter(None, edu_parts))

        # Skills
        skills_entries = snapshot.get("skills") or []
        skills_parts = []
        for s in skills_entries:
            if isinstance(s, dict):
                skills_parts.append(s.get("name") or "")
                for kw in (s.get("keywords") or []):
                    skills_parts.append(str(kw))
        section_texts["skills"] = " ".join(filter(None, skills_parts))

        # Projects
        proj_entries = snapshot.get("projects") or []
        proj_parts = []
        for p in proj_entries:
            if isinstance(p, dict):
                proj_parts.append(p.get("name") or "")
                proj_parts.append(p.get("description") or "")
                for hl in (p.get("highlights") or []):
                    proj_parts.append(str(hl))
                for tech in (p.get("technologies") or []):
                    proj_parts.append(str(tech))
        section_texts["projects"] = " ".join(filter(None, proj_parts))

        # Certifications
        cert_entries = snapshot.get("certificates") or snapshot.get("certifications") or []
        cert_parts = []
        for c in cert_entries:
            if isinstance(c, dict):
                cert_parts.append(c.get("name") or "")
                cert_parts.append(c.get("issuer") or "")
        section_texts["certifications"] = " ".join(filter(None, cert_parts))

        full_text = " ".join(section_texts.values())
        words = re.findall(r"\b[A-Za-z0-9_+#.-]+\b", full_text)

        return section_texts, full_text, words

    def _run_parser_checks(
        self,
        snapshot: Dict[str, Any],
        section_texts: Dict[str, str],
        word_list: List[str],
    ) -> List[ATSCheckItem]:
        """Perform comprehensive deterministic checks on structure, headers, dates, and layout."""
        checks: List[ATSCheckItem] = []
        basics = snapshot.get("basics") or {}

        # 1. Contact Information Checks
        has_name = bool(basics.get("name", "").strip())
        has_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", basics.get("email") or ""))
        has_phone = bool(re.search(r"[\d+()\-\s]{7,}", basics.get("phone") or ""))
        loc = basics.get("location")
        has_location = bool(loc and (loc.get("city") or loc.get("country") or loc.get("address"))) or bool(basics.get("city") or basics.get("country"))

        if has_name and has_email and has_phone and has_location:
            checks.append(ATSCheckItem(
                id="contact-info-complete",
                label="Contact Information Presence",
                category=ATSCheckCategory.CONTACT_INFO,
                status=ATSCheckSeverity.PASS,
                detail="All essential contact fields (Full Name, Email, Phone, Location) are clearly defined.",
            ))
        else:
            missing_contact = []
            if not has_name: missing_contact.append("Full Name")
            if not has_email: missing_contact.append("Valid Email")
            if not has_phone: missing_contact.append("Phone Number")
            if not has_location: missing_contact.append("City / Location")

            checks.append(ATSCheckItem(
                id="contact-info-incomplete",
                label="Contact Information Gaps",
                category=ATSCheckCategory.CONTACT_INFO,
                status=ATSCheckSeverity.WARNING if (not has_email or not has_phone) else ATSCheckSeverity.REVIEW,
                detail=f"Missing recommended contact information: {', '.join(missing_contact)}.",
                recommendation="ATS parsers index candidates by email and phone; ensure both are populated.",
            ))

        # 2. Standard Section Headings
        work_entries = snapshot.get("work") or snapshot.get("work_experience") or []
        edu_entries = snapshot.get("education") or []
        skills_entries = snapshot.get("skills") or []
        summary = basics.get("summary") or basics.get("base_summary") or ""

        missing_sections = []
        if not work_entries: missing_sections.append("Work Experience")
        if not edu_entries: missing_sections.append("Education")
        if not skills_entries: missing_sections.append("Skills")
        if not summary: missing_sections.append("Professional Summary")

        if not missing_sections:
            checks.append(ATSCheckItem(
                id="headings-standard",
                label="Standard Section Headings",
                category=ATSCheckCategory.HEADINGS,
                status=ATSCheckSeverity.PASS,
                detail="All four core sections (Summary, Experience, Education, Skills) are present and standard.",
            ))
        else:
            checks.append(ATSCheckItem(
                id="headings-missing",
                label="Missing Standard Sections",
                category=ATSCheckCategory.HEADINGS,
                status=ATSCheckSeverity.WARNING if ("Work Experience" in missing_sections or "Skills" in missing_sections) else ATSCheckSeverity.REVIEW,
                detail=f"CV lacks standard section data for: {', '.join(missing_sections)}.",
                recommendation="Applicant tracking systems rely on recognized section headers to parse career chronologies.",
            ))

        # 3. Date Consistency & Chronology Check
        date_issues = []
        valid_dates = 0
        dates_order_valid = True
        previous_date = None

        for w in work_entries:
            if isinstance(w, dict):
                start = str(w.get("startDate") or w.get("start_date") or "").strip()
                end = str(w.get("endDate") or w.get("end_date") or "").strip()
                if not start:
                    date_issues.append(f"Missing start date for role '{w.get('position', 'Unknown')}'")
                else:
                    valid_dates += 1
                    # Simple YYYY or YYYY-MM order check
                    year_match = re.search(r"\b(19\d\d|20\d\d)\b", start)
                    if year_match:
                        current_year = int(year_match.group(1))
                        if previous_date and current_year > previous_date:
                            dates_order_valid = False
                        previous_date = current_year

                if start and end and end.lower() != "present":
                    start_yr = re.search(r"\b(19\d\d|20\d\d)\b", start)
                    end_yr = re.search(r"\b(19\d\d|20\d\d)\b", end)
                    if start_yr and end_yr and int(end_yr.group(1)) < int(start_yr.group(1)):
                        date_issues.append(f"End date earlier than start date for '{w.get('position', 'Role')}'")

        if valid_dates > 0 and not date_issues and dates_order_valid:
            checks.append(ATSCheckItem(
                id="dates-consistent",
                label="Date Consistency & Reverse Chronology",
                category=ATSCheckCategory.DATES,
                status=ATSCheckSeverity.PASS,
                detail="Career experiences feature valid dates organized in reverse chronological order.",
            ))
        else:
            detail_msg = "; ".join(date_issues) if date_issues else "Experiences appear out of chronological order."
            checks.append(ATSCheckItem(
                id="dates-issues",
                label="Date Inconsistencies Detected",
                category=ATSCheckCategory.DATES,
                status=ATSCheckSeverity.WARNING,
                detail=detail_msg,
                recommendation="Order work experiences with the most recent role at the top and verify start/end years.",
            ))

        # 4. Template & Layout Parsing Risk Check
        presentation = snapshot.get("presentation") or {}
        template_id = str(presentation.get("template") or "modern").lower()

        if template_id in ["ats-minimal", "minimal"]:
            checks.append(ATSCheckItem(
                id="template-optimal",
                label="Template Layout Compatibility",
                category=ATSCheckCategory.TEMPLATE_LAYOUT,
                status=ATSCheckSeverity.PASS,
                detail="Using ATS-Friendly Minimal single-column linear layout. Zero decorative tables or parser barriers.",
            ))
        elif template_id in ["two-column", "contemporary-two-column"]:
            checks.append(ATSCheckItem(
                id="template-two-column-warning",
                label="Two-Column Layout Friction Risk",
                category=ATSCheckCategory.TEMPLATE_LAYOUT,
                status=ATSCheckSeverity.WARNING,
                detail="Contemporary Two-Column layout detected. Multi-column structures can disrupt parser reading order in older enterprise ATS portals.",
                recommendation="For high-volume enterprise job applications, consider generating an export in the Single-Column ATS Minimal layout.",
            ))
        else:
            checks.append(ATSCheckItem(
                id="template-single-column",
                label="Template Layout Compatibility",
                category=ATSCheckCategory.TEMPLATE_LAYOUT,
                status=ATSCheckSeverity.PASS,
                detail=f"Using single-column '{template_id}' layout with strong vertical typographic flow.",
            ))

        # 5. Character & Symbol Cleanliness
        full_text = " ".join(section_texts.values())
        emojis_found = re.findall(r"[\U00010000-\U0010ffff]", full_text)
        if emojis_found:
            checks.append(ATSCheckItem(
                id="symbols-emojis-found",
                label="Decorative Unicode / Emojis Detected",
                category=ATSCheckCategory.SYMBOLS_AND_FORMATTING,
                status=ATSCheckSeverity.WARNING,
                detail=f"Detected {len(emojis_found)} emoji or complex unicode symbol(s). Many parsers corrupt these characters.",
                recommendation="Replace graphical icons and emojis with standard bullet points or alphanumeric labels.",
            ))
        else:
            checks.append(ATSCheckItem(
                id="symbols-clean",
                label="Symbol & Character Cleanliness",
                category=ATSCheckCategory.SYMBOLS_AND_FORMATTING,
                status=ATSCheckSeverity.PASS,
                detail="Clean standard character set without disruptive unicode glyphs or graphics.",
            ))

        # 6. Content Depth & Quantifiable Impact
        total_w = len(word_list)
        if 250 <= total_w <= 1100:
            checks.append(ATSCheckItem(
                id="content-length-optimal",
                label="Content Length & Depth",
                category=ATSCheckCategory.CONTENT_QUALITY,
                status=ATSCheckSeverity.PASS,
                detail=f"Total word count of {total_w} words is well within standard single/two-page parsing expectations.",
            ))
        elif total_w < 250:
            checks.append(ATSCheckItem(
                id="content-length-short",
                label="Content Length Too Brief",
                category=ATSCheckCategory.CONTENT_QUALITY,
                status=ATSCheckSeverity.WARNING,
                detail=f"Total word count is only {total_w} words, which may lack sufficient detail for keyword matching.",
                recommendation="Expand work experience achievements and core responsibilities.",
            ))
        else:
            checks.append(ATSCheckItem(
                id="content-length-long",
                label="Lengthy Document",
                category=ATSCheckCategory.CONTENT_QUALITY,
                status=ATSCheckSeverity.REVIEW,
                detail=f"Total word count is {total_w} words. Ensure content is concise and high-signal.",
            ))

        # 7. Measurable Impact & Metrics
        work_text = section_texts.get("work", "")
        metrics_found = re.findall(
            r"\b(?:\d+%(?:\s*(?:increase|reduction|growth|improvement|faster))?|\$\d+(?:,\d+)*(?:\.\d+)?(?:M|K|B)?|\b\d+\+?\s*(?:users|clients|engineers|teams|projects|services|requests|req/sec|ms|fold)\b)",
            work_text,
            flags=re.IGNORECASE,
        )
        if len(metrics_found) >= 2:
            checks.append(ATSCheckItem(
                id="metrics-present",
                label="Measurable Impact & Metrics",
                category=ATSCheckCategory.CONTENT_QUALITY,
                status=ATSCheckSeverity.PASS,
                detail=f"Found {len(metrics_found)} quantifiable achievement metrics (e.g., '{metrics_found[0]}').",
            ))
        else:
            checks.append(ATSCheckItem(
                id="metrics-sparse",
                label="Measurable Metrics Sparsity",
                category=ATSCheckCategory.CONTENT_QUALITY,
                status=ATSCheckSeverity.REVIEW,
                detail="Few quantifiable metrics detected in career descriptions.",
                recommendation="Add specific numbers, percentage improvements, throughput metrics, or team sizes to achievements.",
            ))

        return checks

    def _analyze_keywords(
        self,
        job_target: Optional[JobTarget],
        full_text: str,
        section_texts: Dict[str, str],
        total_words: int,
    ) -> Tuple[List[KeywordOccurrenceItem], List[ATSCheckItem]]:
        """Extract target keywords, calculate frequencies, detect keyword stuffing."""
        items: List[KeywordOccurrenceItem] = []
        checks: List[ATSCheckItem] = []
        raw_keywords: List[Tuple[str, bool]] = []  # (kw, is_mandatory)

        if job_target:
            # 1. Pull from existing JobAnalysisResult if available
            analysis_data = job_target.analysis_result or {}
            reqs = analysis_data.get("requirements") or []
            seen_kws: Set[str] = set()

            for r in reqs:
                if isinstance(r, dict):
                    req_text = r.get("requirement", "")
                    is_mand = bool(r.get("is_mandatory", True))
                    # Extract high-signal keywords from requirement statement
                    words = re.findall(r"\b[A-Za-z0-9_+#.-]{2,}\b", req_text)
                    for w in words:
                        clean_w = w.strip()
                        if clean_w.lower() not in COMMON_STOP_WORDS and clean_w.lower() not in seen_kws:
                            raw_keywords.append((clean_w, is_mand))
                            seen_kws.add(clean_w.lower())

            # 2. Extract from job description if requirements were empty
            if not raw_keywords and job_target.job_description:
                jd_words = re.findall(r"\b[A-Za-z0-9_+#.-]{3,}\b", job_target.job_description)
                freq: Dict[str, int] = {}
                for w in jd_words:
                    lw = w.lower()
                    if lw not in COMMON_STOP_WORDS and not lw.isnumeric():
                        freq[w] = freq.get(w, 0) + 1
                sorted_jd = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:25]
                for kw, _ in sorted_jd:
                    raw_keywords.append((kw, True))
        else:
            # Baseline mode: extract technical skills from CV's own skills/work
            skills_text = section_texts.get("skills", "") + " " + section_texts.get("work", "")
            found_kws = re.findall(r"\b[A-Za-z0-9_+#.-]{3,}\b", skills_text)
            freq: Dict[str, int] = {}
            for w in found_kws:
                lw = w.lower()
                if lw not in COMMON_STOP_WORDS and not lw.isnumeric():
                    freq[w] = freq.get(w, 0) + 1
            sorted_kws = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
            for kw, _ in sorted_kws:
                raw_keywords.append((kw, False))

        overused_count = 0
        for kw, is_mand in raw_keywords:
            pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            matches = pattern.findall(full_text)
            count = len(matches)

            locations: List[str] = []
            for sec_name, sec_text in section_texts.items():
                if pattern.search(sec_text):
                    locations.append(sec_name)

            kw_words_len = len(kw.split())
            density = round(((count * kw_words_len) / max(total_words, 1)) * 100.0, 2)
            is_overused = density > 3.5 and count >= 5

            if is_overused:
                overused_count += 1

            items.append(KeywordOccurrenceItem(
                keyword=kw,
                count=count,
                density_percentage=density,
                is_mandatory=is_mand,
                is_present=count > 0,
                is_overused=is_overused,
                locations_found=locations,
            ))

        # Add check item for keyword stuffing
        if overused_count > 0:
            checks.append(ATSCheckItem(
                id="keyword-stuffing-detected",
                label="Keyword Repetition / Stuffing Warning",
                category=ATSCheckCategory.KEYWORD_DENSITY,
                status=ATSCheckSeverity.WARNING,
                detail=f"Detected {overused_count} keyword(s) with density exceeding 3.5%. Excessive repetition triggers ATS spam filters.",
                recommendation="Reduce unnatural keyword repetition; integrate terms contextually in project and work narratives.",
            ))
        else:
            checks.append(ATSCheckItem(
                id="keyword-density-balanced",
                label="Keyword Density & Distribution",
                category=ATSCheckCategory.KEYWORD_DENSITY,
                status=ATSCheckSeverity.PASS,
                detail="Keywords are naturally distributed without spammy repetition or stuffing.",
            ))

        return items, checks

    def _calculate_scores(
        self,
        job_target: Optional[JobTarget],
        checks: List[ATSCheckItem],
        keywords: List[KeywordOccurrenceItem],
        snapshot: Dict[str, Any],
        total_words: int,
    ) -> Tuple[List[ATSComponentScore], int, str]:
        """Calculate documented, transparent component scores and explain point deductions."""
        components: List[ATSComponentScore] = []

        if job_target:
            scoring_mode = "job_targeted"

            # 1. Keyword Coverage (30 pts)
            total_kws = len(keywords)
            present_kws = [k for k in keywords if k.is_present]
            coverage_ratio = (len(present_kws) / max(total_kws, 1))
            kw_score = round(30.0 * coverage_ratio, 1)

            kw_deductions = []
            overused = [k.keyword for k in keywords if k.is_overused]
            if overused:
                penalty = min(len(overused) * 2.0, 8.0)
                kw_score = max(0.0, kw_score - penalty)
                kw_deductions.append(f"-{penalty:.1f} pts: Excessive repetition for {', '.join(overused)}")

            missing_top = [k.keyword for k in keywords if not k.is_present and k.is_mandatory][:4]
            if missing_top:
                kw_deductions.append(f"Missing mandatory keywords: {', '.join(missing_top)}")

            components.append(ATSComponentScore(
                name="Job Keyword Alignment",
                score=min(30.0, kw_score),
                max_score=30.0,
                weight_percentage=30.0,
                explanation=f"Matches {len(present_kws)} of {total_kws} targeted job keywords ({round(coverage_ratio * 100)}% match).",
                deductions=kw_deductions,
            ))

            # 2. Requirement Match (30 pts)
            mandatory_kws = [k for k in keywords if k.is_mandatory]
            preferred_kws = [k for k in keywords if not k.is_mandatory]

            mand_matched = [k for k in mandatory_kws if k.is_present]
            pref_matched = [k for k in preferred_kws if k.is_present]

            mand_ratio = len(mand_matched) / max(len(mandatory_kws), 1)
            pref_ratio = len(pref_matched) / max(len(preferred_kws), 1)

            req_score = round((20.0 * mand_ratio) + (10.0 * pref_ratio), 1)
            req_deductions = []
            if mand_ratio < 1.0:
                missing_m = [k.keyword for k in mandatory_kws if not k.is_present]
                req_deductions.append(f"Missing mandatory qualifications: {', '.join(missing_m[:3])}")

            components.append(ATSComponentScore(
                name="Requirement & Qualification Match",
                score=min(30.0, req_score),
                max_score=30.0,
                weight_percentage=30.0,
                explanation=f"Covers {round(mand_ratio * 100)}% of required criteria and {round(pref_ratio * 100)}% of preferred skills.",
                deductions=req_deductions,
            ))

            # 3. CV Structure & Content Completeness (20 pts)
            struct_score, struct_deductions, struct_expl = self._score_structure_completeness(
                snapshot, total_words, max_pts=20.0
            )
            components.append(ATSComponentScore(
                name="Structure & Content Completeness",
                score=struct_score,
                max_score=20.0,
                weight_percentage=20.0,
                explanation=struct_expl,
                deductions=struct_deductions,
            ))

            # 4. Formatting & Parsing Safety (20 pts)
            format_score, format_deductions, format_expl = self._score_format_safety(
                checks, max_pts=20.0
            )
            components.append(ATSComponentScore(
                name="Formatting & Parsing Safety",
                score=format_score,
                max_score=20.0,
                weight_percentage=20.0,
                explanation=format_expl,
                deductions=format_deductions,
            ))

        else:
            scoring_mode = "general_baseline"

            # 1. Skills & Terminology Depth (30 pts)
            skills = snapshot.get("skills") or []
            skills_count = len(skills)
            vocab_score = min(30.0, round((min(skills_count, 12) / 12.0) * 30.0, 1))
            vocab_deductions = []
            if skills_count < 6:
                vocab_deductions.append("Fewer than 6 distinct technical skills documented")

            components.append(ATSComponentScore(
                name="Skills & Terminology Depth",
                score=vocab_score,
                max_score=30.0,
                weight_percentage=30.0,
                explanation=f"{skills_count} documented technical skills with domain keyword depth.",
                deductions=vocab_deductions,
            ))

            # 2. Structure & Completeness (40 pts)
            struct_score, struct_deductions, struct_expl = self._score_structure_completeness(
                snapshot, total_words, max_pts=40.0
            )
            components.append(ATSComponentScore(
                name="Structure & Content Completeness",
                score=struct_score,
                max_score=40.0,
                weight_percentage=40.0,
                explanation=struct_expl,
                deductions=struct_deductions,
            ))

            # 3. Formatting & Parsing Safety (30 pts)
            format_score, format_deductions, format_expl = self._score_format_safety(
                checks, max_pts=30.0
            )
            components.append(ATSComponentScore(
                name="Formatting & Parsing Safety",
                score=format_score,
                max_score=30.0,
                weight_percentage=30.0,
                explanation=format_expl,
                deductions=format_deductions,
            ))

        total_pts = sum(c.score for c in components)
        overall_score = int(min(100, max(0, round(total_pts))))

        return components, overall_score, scoring_mode

    def _score_structure_completeness(
        self, snapshot: Dict[str, Any], total_words: int, max_pts: float
    ) -> Tuple[float, List[str], str]:
        """Score contact info, summary, experience depth, and metrics."""
        pts = 0.0
        deductions = []
        scale = max_pts / 20.0

        basics = snapshot.get("basics") or {}
        has_email = bool(basics.get("email"))
        has_phone = bool(basics.get("phone"))
        has_loc = bool(basics.get("location") or basics.get("city"))

        contact_pts = (2.0 if has_email else 0.0) + (2.0 if has_phone else 0.0) + (2.0 if has_loc else 0.0)
        pts += contact_pts * scale
        if not (has_email and has_phone and has_loc):
            deductions.append("Incomplete contact details (missing phone, email, or city)")

        # Summary
        summary = basics.get("summary") or basics.get("base_summary") or ""
        if len(summary.split()) >= 15:
            pts += 4.0 * scale
        else:
            deductions.append("Brief or missing professional summary")

        # Work & metrics
        work_entries = snapshot.get("work") or snapshot.get("work_experience") or []
        if len(work_entries) >= 2:
            pts += 4.0 * scale
        elif len(work_entries) == 1:
            pts += 2.0 * scale
        else:
            deductions.append("No professional work experience entries")

        # Metrics check
        full_work_text = " ".join([
            str(w.get("summary", "")) + " " + " ".join(map(str, w.get("highlights", [])))
            for w in work_entries if isinstance(w, dict)
        ])
        if re.search(r"\b\d+%(?:\s*(?:increase|reduction|growth))?|\$\d+|\b\d+\s*(?:users|teams|projects)\b", full_work_text):
            pts += 3.0 * scale
        else:
            deductions.append("Few quantifiable metrics in career achievements")

        # Education & skills
        edu = snapshot.get("education") or []
        skills = snapshot.get("skills") or []
        if edu and skills:
            pts += 3.0 * scale
        elif edu or skills:
            pts += 1.5 * scale

        final_score = round(min(max_pts, pts), 1)
        return final_score, deductions, f"Awarded {final_score}/{max_pts} points based on structural completeness and content detail."

    def _score_format_safety(
        self, checks: List[ATSCheckItem], max_pts: float
    ) -> Tuple[float, List[str], str]:
        """Score layout simplicity, standard headings, date logic, and symbols."""
        pts = max_pts
        deductions = []

        warnings = [c for c in checks if c.status == ATSCheckSeverity.WARNING]
        reviews = [c for c in checks if c.status == ATSCheckSeverity.REVIEW]

        for w in warnings:
            pts -= 3.5
            deductions.append(f"-3.5 pts: {w.label}")

        for r in reviews:
            pts -= 1.5
            deductions.append(f"-1.5 pts: {r.label}")

        final_score = round(max(0.0, pts), 1)
        return final_score, deductions, f"Scored {final_score}/{max_pts} based on layout simplicity and clean parsing flow."

    async def _generate_grounded_suggestions(
        self,
        user_id: uuid.UUID,
        job_target: Optional[JobTarget],
        keywords: List[KeywordOccurrenceItem],
        snapshot: Dict[str, Any],
    ) -> List[GroundedKeywordSuggestion]:
        """
        Generate grounded keyword optimization suggestions.
        Cross-checks missing keywords against CandidateProfile facts to prevent hallucination.
        """
        suggestions: List[GroundedKeywordSuggestion] = []
        if not job_target:
            return suggestions

        # 1. Fetch candidate master knowledge base
        profile = await self.profile_repo.get_by_user_id(user_id)
        candidate_facts: Set[str] = set()

        if profile:
            for s in (profile.skills or []):
                if s.name:
                    candidate_facts.add(s.name.strip().lower())
            for w in (profile.experiences or []):
                for tech in (w.technologies or []):
                    candidate_facts.add(str(tech).strip().lower())
                for hl in (w.responsibilities or []):
                    words = re.findall(r"\b[A-Za-z0-9_+#.-]+\b", str(hl).lower())
                    candidate_facts.update(words)
            for p in (profile.projects or []):
                for tech in (p.technologies or []):
                    candidate_facts.add(str(tech).strip().lower())

        # 2. Check missing or low-density keywords
        missing_or_weak = [k for k in keywords if not k.is_present or k.count <= 1]

        for item in missing_or_weak[:10]:
            kw = item.keyword
            kw_lower = kw.lower()
            clean_slug = re.sub(r"[^a-z0-9]+", "-", kw_lower).strip("-") or "item"
            suggestion_id = f"sugg-{clean_slug}"

            is_grounded = kw_lower in candidate_facts
            if is_grounded:
                suggestions.append(GroundedKeywordSuggestion(
                    id=suggestion_id,
                    keyword=kw,
                    is_mandatory=item.is_mandatory,
                    is_grounded_in_profile=True,
                    grounding_evidence="Found matching skill or tool in your verified Candidate Knowledge Base.",
                    suggested_action=f"Add '{kw}' to your Skills section or highlight in work experiences.",
                    target_section="skills",
                    sample_text=kw,
                    status="pending",
                ))
            else:
                suggestions.append(GroundedKeywordSuggestion(
                    id=suggestion_id,
                    keyword=kw,
                    is_mandatory=item.is_mandatory,
                    is_grounded_in_profile=False,
                    grounding_evidence=None,
                    suggested_action="Candidate gap: not documented in your profile.",
                    target_section="skills",
                    status="pending",
                    warning="This qualification was not found in your career profile. Zero-hallucination policy: do not fabricate this skill on your CV.",
                ))

        return suggestions


def get_ats_service(session: AsyncSession = Depends(get_db_session)) -> ATSService:
    """FastAPI dependency injecting ATSService with PostgreSQL repositories."""
    cv_repo = PostgresCVVersionRepository(session)
    job_repo = PostgresJobTargetRepository(session)
    profile_repo = PostgresProfileRepository(session)
    return ATSService(
        cv_version_repository=cv_repo,
        job_target_repository=job_repo,
        profile_repository=profile_repo,
        db_session=session,
    )
