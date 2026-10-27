import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.services.discovery.models import RawDiscoveredJob

logger = logging.getLogger(__name__)

# Sample verified companies with public ATS boards actively hiring software talent
DEFAULT_GREENHOUSE_BOARDS = [
    "canonical",
    "gitlab",
    "automattic",
    "docker",
    "elastic",
    "postman",
    "razorpay",
    "browserstack",
]

DEFAULT_LEVER_BOARDS = [
    "affirm",
    "palantir",
    "fullstory",
    "atlassian",
]


class DirectATSDiscoveryAdapter:
    """Discovers fresh job postings directly from public corporate ATS feeds (Greenhouse, Lever)."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def fetch_greenhouse_board(self, client: httpx.AsyncClient, company: str) -> List[RawDiscoveredJob]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
        jobs: List[RawDiscoveredJob] = []
        try:
            resp = await client.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.debug(f"Greenhouse board for {company} returned status {resp.status_code}")
                return jobs
            data = resp.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                external_id = str(item.get("id", ""))
                location_name = item.get("location", {}).get("name", "Remote") or "Remote"
                content = item.get("content", "")
                apply_url = item.get("absolute_url", "")
                
                # Check for remote indicator
                is_remote = "remote" in location_name.lower() or "remote" in title.lower() or "anywhere" in location_name.lower()

                # Basic skill keyword extraction
                skills: List[str] = []
                content_lower = (content + " " + title).lower()
                for tech in ["react", "node.js", "nodejs", "javascript", "typescript", "express", "mongodb", "python", "fastapi", "git", "html", "css", "rest api"]:
                    if tech in content_lower:
                        skills.append(tech.title())

                jobs.append(
                    RawDiscoveredJob(
                        source_platform="greenhouse",
                        external_id=f"gh_{company}_{external_id}",
                        title=title,
                        company_name=company.capitalize(),
                        location=location_name,
                        is_remote=is_remote,
                        employment_type="full_time",
                        source_url=apply_url,
                        apply_url=apply_url,
                        raw_description=content or f"{title} position at {company.capitalize()}",
                        posted_at=datetime.now(timezone.utc),
                        extracted_skills=list(set(skills)),
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to fetch Greenhouse board for {company}: {exc}")
        return jobs

    async def fetch_lever_board(self, client: httpx.AsyncClient, company: str) -> List[RawDiscoveredJob]:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        jobs: List[RawDiscoveredJob] = []
        try:
            resp = await client.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.debug(f"Lever board for {company} returned status {resp.status_code}")
                return jobs
            data = resp.json()
            for item in data:
                title = item.get("text", "")
                external_id = str(item.get("id", ""))
                categories = item.get("categories", {})
                location_name = categories.get("location", "Remote") or "Remote"
                commitment = categories.get("commitment", "Full-time") or "full_time"
                description = item.get("descriptionPlain", "") or item.get("description", "")
                apply_url = item.get("applyUrl", "") or item.get("hostedUrl", "")

                is_remote = "remote" in location_name.lower() or "remote" in title.lower()

                skills: List[str] = []
                content_lower = (description + " " + title).lower()
                for tech in ["react", "node.js", "nodejs", "javascript", "typescript", "express", "mongodb", "python", "fastapi", "git", "html", "css", "rest api"]:
                    if tech in content_lower:
                        skills.append(tech.title())

                jobs.append(
                    RawDiscoveredJob(
                        source_platform="lever",
                        external_id=f"lever_{company}_{external_id}",
                        title=title,
                        company_name=company.capitalize(),
                        location=location_name,
                        is_remote=is_remote,
                        employment_type="internship" if "intern" in commitment.lower() else "full_time",
                        source_url=apply_url,
                        apply_url=apply_url,
                        raw_description=description or f"{title} at {company.capitalize()}",
                        posted_at=datetime.now(timezone.utc),
                        extracted_skills=list(set(skills)),
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to fetch Lever board for {company}: {exc}")
        return jobs

    async def discover_jobs(self, custom_companies: Optional[List[str]] = None) -> List[RawDiscoveredJob]:
        """Discovers open opportunities across curated corporate ATS public boards."""
        companies_gh = custom_companies or DEFAULT_GREENHOUSE_BOARDS
        companies_lever = custom_companies or DEFAULT_LEVER_BOARDS
        results: List[RawDiscoveredJob] = []

        async with httpx.AsyncClient(headers={"User-Agent": "CareerAgent/1.0 (Candidate Discovery)"}) as client:
            for co in companies_gh:
                jobs = await self.fetch_greenhouse_board(client, co)
                results.extend(jobs)
            for co in companies_lever:
                jobs = await self.fetch_lever_board(client, co)
                results.extend(jobs)

        return results
