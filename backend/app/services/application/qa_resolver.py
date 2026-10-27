from typing import Any, Dict, List, Optional, Tuple
import uuid

from app.models.autonomous_agent import QAMemoryBankItem
from app.models.profile import CandidateProfile
from app.repositories.postgres.autonomous_agent_repository import AutonomousAgentRepository


class QAResolverService:
    """Zero-hallucination QA Resolver for job application portal questions."""

    DEFAULT_QA_SEEDS = [
        {
            "category": "work_authorization",
            "question_pattern": "legally authorized to work in",
            "answer_value": "Yes",
            "user_notes": "Authorized to work in India without sponsorship",
        },
        {
            "category": "work_authorization",
            "question_pattern": "require sponsorship",
            "answer_value": "No",
            "user_notes": "Does not require visa sponsorship",
        },
        {
            "category": "notice_period",
            "question_pattern": "notice period",
            "answer_value": "Immediate / 0 days",
            "user_notes": "Available to join immediately",
        },
        {
            "category": "notice_period",
            "question_pattern": "earliest start date",
            "answer_value": "Immediate",
            "user_notes": "Immediate joining availability",
        },
        {
            "category": "compensation",
            "question_pattern": "salary expectation",
            "answer_value": "Negotiable / Industry standard for early-career developer",
            "user_notes": "Open to discussion based on role and location",
        },
        {
            "category": "relocation",
            "question_pattern": "willing to relocate",
            "answer_value": "Yes",
            "user_notes": "Open to relocation across South India (Karnataka, Tamil Nadu, Telangana, Kerala: Bangalore, Hyderabad, Chennai, Kochi, Kozhikode, Kannur) and remote across India",
        },
        {
            "category": "relocation",
            "question_pattern": "preferred location",
            "answer_value": "Bangalore, Hyderabad, Chennai, Kochi, Kozhikode, Kannur, or Remote",
            "user_notes": "Preferred tech hubs in South India (Karnataka, Telangana, Tamil Nadu, Kerala) and remote pan-India",
        },
        {
            "category": "links",
            "question_pattern": "github profile",
            "answer_value": "https://github.com/4bjith/",
            "user_notes": "Verified personal GitHub profile",
        },
        {
            "category": "links",
            "question_pattern": "portfolio website",
            "answer_value": "https://4bjith.github.io/Portfolio-Website/",
            "user_notes": "Verified personal portfolio website",
        },
        {
            "category": "links",
            "question_pattern": "linkedin profile",
            "answer_value": "https://www.linkedin.com/in/abhijith-4bjith/",
            "user_notes": "Verified LinkedIn profile",
        },
    ]

    def __init__(self, repo: AutonomousAgentRepository):
        self.repo = repo

    async def ensure_default_qa_seeds(self, user_id: uuid.UUID) -> None:
        """Seeds default confirmed QA answers if user has none configured."""
        existing = await self.repo.list_qa_items(user_id)
        if not existing:
            for seed in self.DEFAULT_QA_SEEDS:
                item = QAMemoryBankItem(
                    user_id=user_id,
                    category=seed["category"],
                    question_pattern=seed["question_pattern"],
                    answer_value=seed["answer_value"],
                    is_confirmed=True,
                    user_notes=seed["user_notes"],
                )
                await self.repo.create_qa_item(item)
        else:
            # Synchronize relocation answer if outdated
            for item in existing:
                if item.category == "relocation" and item.question_pattern == "willing to relocate":
                    if "South India" not in (item.user_notes or ""):
                        item.user_notes = (
                            "Open to relocation across South India (Karnataka, Tamil Nadu, Telangana, Kerala: Bangalore, Hyderabad, Chennai, Kochi, Kozhikode, Kannur) and remote across India"
                        )
                        await self.repo.create_qa_item(item)

    async def resolve_question(
        self,
        user_id: uuid.UUID,
        question_text: str,
        profile: Optional[CandidateProfile] = None,
    ) -> Tuple[Optional[str], bool, str]:
        """
        Resolves an application form question.
        Returns:
            (answer_value, is_resolved, provenance_source)
        """
        norm_q = question_text.strip().lower()

        # 1. Match from QA Memory Bank
        matched_item = await self.repo.find_matching_qa_answer(user_id, norm_q)
        if matched_item:
            return matched_item.answer_value, True, "qa_memory_bank"

        # 2. Match from Candidate Profile direct fields
        if profile:
            if any(term in norm_q for term in ["phone", "contact number", "mobile"]):
                if profile.phone:
                    return profile.phone, True, "candidate_profile"
            if any(term in norm_q for term in ["email", "email address"]):
                if profile.email:
                    return profile.email, True, "candidate_profile"
            if any(term in norm_q for term in ["first name"]):
                return profile.first_name, True, "candidate_profile"
            if any(term in norm_q for term in ["last name", "surname"]):
                return profile.last_name or "", True, "candidate_profile"
            if any(term in norm_q for term in ["full name"]):
                return f"{profile.first_name} {profile.last_name or ''}".strip(), True, "candidate_profile"
            if any(term in norm_q for term in ["city", "current location"]):
                return profile.city or "Kerala, India", True, "candidate_profile"

        # 3. Unresolved: return None with explicit provenance
        return None, False, "unresolved_missing_fact"
