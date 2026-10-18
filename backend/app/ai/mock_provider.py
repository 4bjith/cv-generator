import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

from app.ai.interface import AIProviderInterface
from app.core.logging import get_logger

logger = get_logger("app.ai.mock_provider")

T = TypeVar("T", bound=BaseModel)


class MockAIProvider(AIProviderInterface):
    """
    Deterministic mock AI provider for automated unit/integration tests and offline development.
    Produces repeatable, high-quality, evidence-grounded outputs without network latency or external credentials.
    """

    def __init__(self, model_name: str = "mock-gemini-2.0") -> None:
        self.model_name = model_name

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Deterministic text generation tailored to common CV generation prompts."""
        logger.debug("MockAIProvider generating text for prompt snippet", prompt_snippet=prompt[:80])

        prompt_lower = prompt.lower()
        if "summary" in prompt_lower or "professional summary" in prompt_lower:
            return (
                "Accomplished software engineer with proven expertise in building high-performance, "
                "distributed systems, scalable backend architectures, and mission-critical cloud services. "
                "Track record of reducing latency, enhancing reliability, and mentoring engineering teams."
            )
        elif "bullet" in prompt_lower or "rewrite" in prompt_lower:
            return (
                "Architected and deployed distributed event streaming pipelines handling high throughput, "
                "improving overall end-to-end processing latency by 35%."
            )
        elif "clarification" in prompt_lower or "question" in prompt_lower:
            return "Could you provide details on your production experience with the required technology stack?"
        else:
            return f"Mock response generated deterministically from prompt context for {self.model_name}."

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured Pydantic object deterministically based on schema fields."""
        logger.debug("MockAIProvider generating structured output", schema_name=schema.__name__)

        # Specialized handling for StructuredTailoringOutput
        if schema.__name__ == "StructuredTailoringOutput":
            # Extract skills mentioned in prompt if available
            extracted_skills = []
            m_skills = re.search(r"CANDIDATE SKILLS:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_skills:
                extracted_skills = [s.strip() for s in m_skills.group(1).split(",") if s.strip()]
            if not extracted_skills:
                extracted_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "TypeScript", "React"]

            # Extract target role from prompt
            target_role = "Senior Software Engineer"
            m_role = re.search(r"TARGET ROLE:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_role:
                target_role = m_role.group(1).strip()

            mock_tailoring = {
                "tailored_summary": (
                    f"Results-driven engineering professional tailored for the {target_role} position. "
                    "Demonstrated expertise in architecting high-throughput distributed systems, "
                    "resilient cloud microservices, and high-reliability data backends with proven performance gains."
                ),
                "target_role": target_role,
                "relevant_skills": extracted_skills[:8],
                "tailored_highlights": {
                    "default": [
                        "Architected scalable backend microservices reducing end-to-end processing latency by 35%.",
                        "Spearheaded database query optimization and indexing, cutting p99 query time from 420ms to 85ms.",
                        "Engineered fault-tolerant event processing pipelines handling peak production volume.",
                    ]
                },
                "change_summary": [
                    f"Synthesized targeted professional summary directly addressing the {target_role} role.",
                    f"Prioritized top relevant skills ({', '.join(extracted_skills[:3])}) matching mandatory requirements.",
                    "Structured experience highlights to emphasize quantifiable performance and system scalability achievements.",
                ],
                "unresolved_gaps": [],
            }
            return schema.model_validate(mock_tailoring)

        # Specialized handling for StructuredCoverLetterOutput
        if schema.__name__ == "StructuredCoverLetterOutput":
            target_role = "Software Engineer"
            m_role = re.search(r"TARGET ROLE:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_role:
                target_role = m_role.group(1).strip()

            target_company = "the company"
            m_comp = re.search(r"TARGET COMPANY:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_comp:
                target_company = m_comp.group(1).strip()

            recipient = "Hiring Team"
            m_rec = re.search(r"RECIPIENT:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_rec and m_rec.group(1).strip():
                recipient = m_rec.group(1).strip()

            salutation = f"Dear {recipient} at {target_company}," if recipient != target_company else f"Dear {recipient},"

            # Extract unresolved gaps from prompt if flagged
            unresolved = []
            m_gaps = re.search(r"UNRESOLVED GAPS:\s*([^\n]+)", prompt, re.IGNORECASE)
            if m_gaps and m_gaps.group(1).strip() and "none" not in m_gaps.group(1).lower():
                unresolved = [g.strip() for g in m_gaps.group(1).split(",") if g.strip()]

            mock_letter = {
                "salutation": salutation,
                "opening": (
                    f"I am writing to express my strong interest in the {target_role} role at {target_company}. "
                    "With a proven background in architecting high-reliability distributed systems, optimizing backend performance, "
                    f"and delivering scalable cloud architectures, I am excited about the opportunity to contribute to {target_company}'s mission."
                ),
                "body_paragraphs": [
                    (
                        "Throughout my engineering career, I have focused on solving complex distributed data challenges with measurable impact. "
                        "In my previous roles, I architected scalable cloud microservices that reduced end-to-end processing latency by 35% "
                        "while upholding 99.99% system availability under peak production workloads."
                    ),
                    (
                        "Additionally, I led targeted database and infrastructure optimizations, reducing p99 query latency from 420ms to 85ms. "
                        "My approach pairs rigorous system design with transparent evidence and collaborative cross-functional execution, "
                        f"ensuring technical solutions align directly with {target_company}'s operational goals."
                    ),
                ],
                "closing": (
                    f"I would welcome the opportunity to discuss how my technical experience and verified engineering accomplishments "
                    f"can add immediate value to the {target_role} team at {target_company}. Thank you for your time and consideration."
                ),
                "sign_off": "Sincerely,",
                "factual_claims": [
                    {
                        "claim_text": "Architected scalable cloud microservices reducing processing latency by 35% and maintaining 99.99% availability.",
                        "entity_type": "experience",
                        "verification_status": "verified",
                    },
                    {
                        "claim_text": "Optimized database queries, reducing p99 query latency from 420ms to 85ms.",
                        "entity_type": "experience",
                        "verification_status": "verified",
                    },
                ],
                "unresolved_gaps": unresolved,
                "change_summary": "Generated evidence-grounded cover letter strictly aligned with confirmed profile accomplishments and job requirements.",
            }
            return schema.model_validate(mock_letter)

        # Inspect schema fields to build compliant mock dictionary
        schema_fields = schema.model_fields if hasattr(schema, "model_fields") else {}
        mock_data: Dict[str, Any] = {}

        for field_name, field_info in schema_fields.items():
            field_type = field_info.annotation
            field_type_str = str(field_type).lower()

            if "str" in field_type_str:
                if "summary" in field_name:
                    mock_data[field_name] = (
                        "Senior engineering professional with deep expertise in scalable cloud architecture, "
                        "robust backend development, and high-reliability distributed systems."
                    )
                elif "role" in field_name or "title" in field_name:
                    mock_data[field_name] = "Lead Software Engineer"
                elif "reason" in field_name or "explanation" in field_name:
                    mock_data[field_name] = "Tailored to align directly with target job requirements while strictly preserving verified evidence."
                elif "bullet" in field_name or "highlight" in field_name:
                    mock_data[field_name] = "Delivered high-impact optimizations across core services with verifiable performance gains."
                elif "code" in field_name or "status" in field_name:
                    mock_data[field_name] = "supported"
                else:
                    mock_data[field_name] = f"Mock {field_name.replace('_', ' ').capitalize()}"
            elif "int" in field_type_str:
                mock_data[field_name] = 5
            elif "float" in field_type_str:
                if "score" in field_name or "percentage" in field_name or "coverage" in field_name:
                    mock_data[field_name] = 88.5
                else:
                    mock_data[field_name] = 1.0
            elif "bool" in field_type_str:
                mock_data[field_name] = True
            elif "list" in field_type_str:
                if "skill" in field_name:
                    mock_data[field_name] = ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"]
                elif "highlight" in field_name or "bullet" in field_name or "responsibilities" in field_name:
                    mock_data[field_name] = [
                        "Architected low-latency microservices with automated failover and telemetry.",
                        "Spearheaded database query optimization reducing p99 latency by 40%.",
                        "Collaborated with cross-functional teams to deliver customer-facing features on schedule.",
                    ]
                elif "recommendation" in field_name:
                    mock_data[field_name] = ["Consider adding a verifiable metric report for recent platform initiatives."]
                elif "gap" in field_name or "unmet" in field_name:
                    mock_data[field_name] = []
                elif "str" in field_type_str:
                    mock_data[field_name] = ["Relevant qualification 1", "Relevant qualification 2"]
                else:
                    mock_data[field_name] = []
            elif "dict" in field_type_str:
                mock_data[field_name] = {}
            else:
                mock_data[field_name] = None

        # Return validated Pydantic model
        return schema.model_validate(mock_data)

    async def compute_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """Compute deterministic mock embedding vectors (dimension 128) based on MD5 hashes."""
        embeddings: List[List[float]] = []
        dim = 128
        for text in texts:
            # Deterministic pseudo-embedding based on text hash
            h = hashlib.sha256(text.encode("utf-8")).digest()
            # Generate 128 normalized float values
            vec = [(float(b) / 255.0 * 2.0 - 1.0) for b in h[:32]]
            # Repeat to reach dim=128
            vec = (vec * 4)[:dim]
            # Normalize vector to unit length
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings
