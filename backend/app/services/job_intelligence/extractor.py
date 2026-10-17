import re
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from app.core.logging import get_logger
from app.schemas.job_target import (
    CandidateMatchStatus,
    JobExtractionResult,
    JobRequirementCategory,
    JobRequirementItem,
)
from app.services.job_intelligence.extractor_interface import IJobExtractor

logger = get_logger("app.services.job_intelligence.extractor")

# Curated catalog of tech stacks, tools, languages, and frameworks for deterministic recognition
TECH_CATALOG = {
    "python", "javascript", "typescript", "golang", "go", "rust", "java", "c++", "c#", "ruby", "php", "swift", "kotlin",
    "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte", "html", "css", "tailwind", "sass", "redux",
    "fastapi", "django", "flask", "node.js", "nodejs", "express", "express.js", "nest.js", "spring", "spring boot", "ruby on rails",
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
    "aws", "amazon web services", "gcp", "google cloud", "azure", "docker", "kubernetes", "k8s", "terraform", "ansible",
    "ci/cd", "github actions", "gitlab ci", "jenkins", "git", "linux", "graphql", "rest", "restful api", "grpc",
    "kafka", "rabbitmq", "celery", "airflow", "spark", "hadoop", "pandas", "numpy", "pytorch", "tensorflow",
    "scikit-learn", "langchain", "llamaindex", "openai", "gemini", "anthropic", "alembic", "sqlalchemy", "prisma",
}

SENIORITY_PATTERNS = [
    (r"\b(principal|staff|distinguished)\b", "Staff / Principal"),
    (r"\b(lead|architect)\b", "Lead / Architect"),
    (r"\b(senior|sr\.?)\b", "Senior"),
    (r"\b(mid-level|mid level|intermediate)\b", "Mid-Level"),
    (r"\b(junior|jr\.?|associate|entry-level|entry level|graduate)\b", "Junior / Entry-Level"),
    (r"\b(intern|internship)\b", "Internship"),
]

EMPLOYMENT_PATTERNS = [
    (r"\b(full-time|full time|fte)\b", "Full-time"),
    (r"\b(part-time|part time)\b", "Part-time"),
    (r"\b(contract|contractor|freelance|c2c|w2)\b", "Contract"),
    (r"\b(internship|intern)\b", "Internship"),
]


class RuleBasedJobExtractor(IJobExtractor):
    """
    Robust deterministic NLP extractor that parses unstructured job descriptions into
    canonical JobRequirementItem records, categorized by skills, technologies, experience,
    education, certifications, responsibilities, and constraints with mandatory vs preferred classification.
    """

    async def extract(
        self,
        text: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
    ) -> JobExtractionResult:
        if not text or not text.strip():
            return JobExtractionResult(
                role_overview=title or "Target Position",
                requirements=[],
                extracted_keywords=[],
            )

        clean_text = text.strip()
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

        # 1. Detect Seniority and Employment Type
        seniority = self._detect_seniority(clean_text, title)
        emp_type = self._detect_employment_type(clean_text)

        # 2. Extract sections
        sections = self._segment_sections(lines)

        # 3. Extract requirements from sections
        requirements: List[JobRequirementItem] = []
        seen_requirements: Set[str] = set()

        for section_type, section_lines, is_mandatory in sections:
            for line in section_lines:
                cleaned_line = self._clean_bullet(line)
                if not cleaned_line or len(cleaned_line) < 3:
                    continue

                norm_key = cleaned_line.lower()
                if norm_key in seen_requirements:
                    continue
                seen_requirements.add(norm_key)

                category = self._classify_requirement_category(cleaned_line, section_type)
                
                # Check for explicit mandatory / preferred indicators within the line itself
                line_mandatory = is_mandatory
                if re.search(r"\b(preferred|bonus|nice to have|plus|ideal|optional)\b", cleaned_line, re.IGNORECASE):
                    line_mandatory = False
                elif re.search(r"\b(must have|required|mandatory|essential|minimum)\b", cleaned_line, re.IGNORECASE):
                    line_mandatory = True

                item = JobRequirementItem(
                    id=uuid.uuid4(),
                    category=category.value if hasattr(category, "value") else str(category),
                    requirement=cleaned_line,
                    is_mandatory=line_mandatory,
                    candidate_match_status=CandidateMatchStatus.MISSING.value,
                )
                requirements.append(item)

        # 4. Extract explicit constraints if not already captured
        self._extract_explicit_constraints(clean_text, requirements, seen_requirements)

        # 5. Extract keywords
        extracted_keywords = self._extract_keywords(clean_text)

        # 6. Build overview
        overview = self._build_role_overview(lines, title, company)

        logger.info(
            f"Extracted {len(requirements)} requirements ({sum(1 for r in requirements if r.is_mandatory)} mandatory) "
            f"and {len(extracted_keywords)} keywords for '{title or 'Job'}'"
        )

        return JobExtractionResult(
            role_overview=overview,
            seniority_level=seniority,
            employment_type=emp_type,
            requirements=requirements,
            extracted_keywords=extracted_keywords,
        )

    def _detect_seniority(self, text: str, title: Optional[str] = None) -> Optional[str]:
        target = f"{title or ''} {text[:500]}"
        for pattern, label in SENIORITY_PATTERNS:
            if re.search(pattern, target, re.IGNORECASE):
                return label
        return None

    def _detect_employment_type(self, text: str) -> Optional[str]:
        for pattern, label in EMPLOYMENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return label
        return None

    def _clean_bullet(self, line: str) -> str:
        # Strip bullets like '-', '*', '•', '▪', '1.', '1)', etc.
        cleaned = re.sub(r"^[\s\-\*\•\▪\–\—\>]+", "", line).strip()
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned).strip()
        return cleaned

    def _segment_sections(self, lines: List[str]) -> List[Tuple[str, List[str], bool]]:
        """
        Segment lines into classified sections:
        Returns list of (section_type, lines, is_mandatory)
        """
        sections: List[Tuple[str, List[str], bool]] = []
        current_section = "general"
        current_lines: List[str] = []
        current_mandatory = True

        for line in lines:
            header_type, is_mandatory = self._identify_header(line)
            if header_type is not None:
                if current_lines:
                    sections.append((current_section, current_lines, current_mandatory))
                    current_lines = []
                current_section = header_type
                current_mandatory = is_mandatory
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_section, current_lines, current_mandatory))

        return sections

    def _identify_header(self, line: str) -> Tuple[Optional[str], bool]:
        """
        Check if a line functions as a section header.
        Returns (section_type, is_mandatory) or (None, False).
        """
        lower = line.strip().lower()
        if len(lower) > 70:
            return None, False

        # Preferred / Nice to have
        if any(h in lower for h in [
            "preferred qualifications", "preferred skills", "nice to have", "bonus points",
            "desired qualifications", "desired skills", "what would be nice", "good to have",
            "preferred experience", "plus points", "standout qualifications",
        ]):
            return "preferred", False

        # Mandatory / Minimum requirements
        if any(h in lower for h in [
            "minimum qualifications", "basic qualifications", "requirements", "what you need",
            "must have", "what you bring", "required qualifications", "required skills",
            "key requirements", "qualifications", "who you are", "about you", "what we're looking for",
        ]):
            return "mandatory", True

        # Responsibilities
        if any(h in lower for h in [
            "responsibilities", "what you'll do", "what you will do", "the role",
            "day to day", "your mission", "key responsibilities", "duties", "scope of work",
        ]):
            return "responsibilities", True

        # Tech stack / Tools
        if any(h in lower for h in [
            "tech stack", "technologies", "tools", "technology stack", "our stack",
        ]):
            return "technologies", True

        # Education & Certifications
        if any(h in lower for h in [
            "education", "certifications", "degrees",
        ]):
            return "education", True

        return None, False

    def _classify_requirement_category(self, requirement: str, section_type: str) -> JobRequirementCategory:
        lower = requirement.lower()

        # Education
        if any(w in lower for w in ["bachelor", "master", "phd", "degree", "bs in", "ms in", "b.s.", "m.s.", "computer science", "bootcamp"]):
            return JobRequirementCategory.EDUCATION

        # Certifications
        if any(w in lower for w in ["certified", "certification", "aws certified", "pmp", "cissp", "cka", "ckad"]):
            return JobRequirementCategory.CERTIFICATIONS

        # Experience
        if re.search(r"\b(\d+\+?|\d+-\d+)\s*(years|yrs|year)\b", lower):
            return JobRequirementCategory.EXPERIENCE

        # Constraints
        if any(w in lower for w in [
            "authorized to work", "visa", "sponsorship", "security clearance", "citizen",
            "relocate", "relocation", "timezone", "on-site", "hybrid", "background check"
        ]):
            return JobRequirementCategory.CONSTRAINTS

        # Section-driven classification
        if section_type == "responsibilities":
            return JobRequirementCategory.RESPONSIBILITIES

        if section_type == "technologies":
            return JobRequirementCategory.TECHNOLOGIES

        # Check for technical tools in requirement
        words = set(re.findall(r"[a-zA-Z0-9\+\#\.\/]+", lower))
        if words.intersection(TECH_CATALOG):
            return JobRequirementCategory.TECHNOLOGIES

        return JobRequirementCategory.SKILLS

    def _extract_explicit_constraints(
        self,
        text: str,
        requirements: List[JobRequirementItem],
        seen_requirements: Set[str],
    ) -> None:
        """Find explicit constraints (work authorization, clearance, timezone) across the text."""
        constraint_regexes = [
            r"([^\.\n]*?(?:authorized to work|visa sponsorship|security clearance|must be located|timezone)[^\.\n]*)",
        ]
        for pattern in constraint_regexes:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                cand = m.group(1).strip()
                cleaned = self._clean_bullet(cand)
                if cleaned and len(cleaned) > 15 and cleaned.lower() not in seen_requirements:
                    seen_requirements.add(cleaned.lower())
                    requirements.append(
                        JobRequirementItem(
                            id=uuid.uuid4(),
                            category=JobRequirementCategory.CONSTRAINTS.value,
                            requirement=cleaned,
                            is_mandatory=True,
                            candidate_match_status=CandidateMatchStatus.MISSING.value,
                        )
                    )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract unique recognized technical and industry keywords."""
        lower = text.lower()
        found: Set[str] = set()

        for tech in TECH_CATALOG:
            # Pattern with word boundaries, supporting tech terms with punctuation like c++, c#, .net
            escaped = re.escape(tech)
            pattern = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
            if re.search(pattern, lower):
                found.add(tech)

        # Standard capitalization formatting
        capitalized = []
        for kw in sorted(found):
            if kw in {"aws", "gcp", "k8s", "sql", "css", "html", "ci/cd", "rest", "api", "pmp", "grpc"}:
                capitalized.append(kw.upper())
            elif kw in {"react", "react.js", "next.js", "fastapi", "vue", "vue.js", "node.js", "nodejs", "express", "django", "flask", "docker", "kubernetes", "postgresql", "redis", "mongodb", "python", "typescript", "javascript", "golang", "rust", "terraform", "graphql"}:
                # Capitalize nicely
                parts = kw.split(".")
                cap_part = ".".join(p.capitalize() for p in parts)
                capitalized.append(cap_part)
            else:
                capitalized.append(kw.capitalize())

        return capitalized

    def _build_role_overview(
        self,
        lines: List[str],
        title: Optional[str] = None,
        company: Optional[str] = None,
    ) -> str:
        """Construct a concise 1-2 sentence role overview from introductory paragraphs."""
        prefix = f"{title} at {company}" if title and company else (title or company or "Target Role")
        intro_candidates = []
        for line in lines[:8]:
            clean = self._clean_bullet(line)
            if len(clean) > 40 and not any(h in clean.lower() for h in ["requirement", "qualification", "responsibilit", "about us", "who we are"]):
                intro_candidates.append(clean)
                if len(intro_candidates) >= 2:
                    break

        if intro_candidates:
            return f"{prefix} — " + " ".join(intro_candidates)
        return f"{prefix} opportunity."
