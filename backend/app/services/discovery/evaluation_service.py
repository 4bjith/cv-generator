from typing import Any, Dict, List, Tuple
from app.models.autonomous_agent import JobSearchProfile
from app.models.profile import CandidateProfile
from app.services.discovery.models import RawDiscoveredJob


class JobEvaluationService:
    """Intelligent, evidence-grounded, fresher-aware evaluation and shortlisting service."""

    @staticmethod
    def evaluate_job(
        job: RawDiscoveredJob,
        search_profile: JobSearchProfile,
        candidate_profile: Optional[CandidateProfile] = None,
    ) -> Tuple[float, str, str]:
        """
        Evaluates a raw discovered job against candidate preferences and verified evidence.
        Returns:
            match_score (0.0 to 100.0)
            eligibility_status ("eligible", "ineligible", "needs_review")
            fit_reasoning (detailed explainable rationale)
        """
        title_lower = job.title.strip().lower()
        desc_lower = job.raw_description.strip().lower()
        location_lower = job.location.strip().lower()

        # ----------------------------------------------------------------------
        # 1. Negative Filters & Ineligibility Checks
        # ----------------------------------------------------------------------
        senior_indicators = ["senior", "lead", "principal", "architect", "staff", "head of", "director", "vp ", "manager"]
        if any(indicator in title_lower for indicator in senior_indicators):
            if "junior" not in title_lower and not search_profile.fresher_mode:
                pass
            elif any(indicator in title_lower for indicator in ["staff", "principal", "director", "architect"]):
                return (
                    15.0,
                    "ineligible",
                    f"Rejected: Position level '{job.title}' exceeds early-career target scope.",
                )

        # ----------------------------------------------------------------------
        # 2. Location & Remote Compatibility Check
        # ----------------------------------------------------------------------
        location_matched = False
        if job.is_remote:
            location_matched = True
        else:
            for loc in search_profile.target_locations:
                if loc.strip().lower() in location_lower:
                    location_matched = True
                    break

        # If purely onsite in an unapproved region
        if not location_matched and not job.is_remote:
            sample_locs = ", ".join(search_profile.target_locations[:8])
            return (
                30.0,
                "ineligible",
                f"Rejected: Onsite location '{job.location}' outside target regions ({sample_locs}).",
            )

        # ----------------------------------------------------------------------
        # 3. Role Title Alignment (40 points max)
        # ----------------------------------------------------------------------
        role_score = 0.0
        matched_role = None
        for role in search_profile.target_roles:
            role_parts = [p.lower() for p in role.split() if len(p) > 2]
            if any(part in title_lower for part in role_parts):
                role_score = 40.0
                matched_role = role
                break

        if not matched_role and any(term in title_lower for term in ["developer", "engineer", "intern", "trainee", "software"]):
            role_score = 25.0
            matched_role = "General Software Development"

        # ----------------------------------------------------------------------
        # 4. Tech Stack & Skill Overlap (40 points max)
        # ----------------------------------------------------------------------
        candidate_skills = [s.strip().lower() for s in search_profile.primary_skills]
        if candidate_profile and candidate_profile.skills:
            candidate_skills = list(set(candidate_skills + [s.name.strip().lower() for s in candidate_profile.skills]))

        matched_skills: List[str] = []
        for skill in candidate_skills:
            if skill in desc_lower or skill in title_lower:
                matched_skills.append(skill.title())

        # Proportional skill score
        if matched_skills:
            # 4 or more core skills matched = full 40 points
            skill_score = min(40.0, (len(matched_skills) / 4.0) * 40.0)
        else:
            skill_score = 10.0

        # ----------------------------------------------------------------------
        # 5. Fresher & Early Career Friendliness Bonus (20 points max)
        # ----------------------------------------------------------------------
        fresher_score = 0.0
        fresher_signals: List[str] = []

        if job.employment_type == "internship" or "intern" in title_lower:
            fresher_score = 20.0
            fresher_signals.append("Internship opportunity")
        elif any(term in desc_lower or term in title_lower for term in ["fresher", "trainee", "entry level", "junior", "0-1", "0 to 1", "0-2 years"]):
            fresher_score = 20.0
            fresher_signals.append("Fresher / Early-career explicitly accepted")
        elif "experience" not in desc_lower or any(phrase in desc_lower for phrase in ["project experience", "portfolio", "github", "equivalent"]):
            fresher_score = 15.0
            fresher_signals.append("Values project experience and GitHub portfolio")
        else:
            fresher_score = 10.0

        # Total Match Score Calculation
        total_score = round(role_score + skill_score + fresher_score, 1)

        # Build explainable fit reasoning
        reasoning_parts = []
        if matched_role:
            reasoning_parts.append(f"Role match: {matched_role} (+{int(role_score)}%)")
        if matched_skills:
            reasoning_parts.append(f"Matched skills: {', '.join(matched_skills[:5])} (+{int(skill_score)}%)")
        if fresher_signals:
            reasoning_parts.append(f"Fresher fit: {', '.join(fresher_signals)} (+{int(fresher_score)}%)")
        if job.is_remote:
            reasoning_parts.append("Location: Remote verified")
        else:
            reasoning_parts.append(f"Location: {job.location}")

        fit_reasoning = "; ".join(reasoning_parts)

        # Eligibility threshold
        if total_score >= 70.0:
            eligibility = "eligible"
        elif total_score >= 50.0:
            eligibility = "needs_review"
        else:
            eligibility = "ineligible"

        return total_score, eligibility, fit_reasoning
