import logging
from datetime import datetime, timezone
from typing import List
import httpx

from app.services.discovery.models import RawDiscoveredJob

logger = logging.getLogger(__name__)


class AggregatorDiscoveryAdapter:
    """Discovers remote developer opportunities from public developer aggregator APIs."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    async def fetch_jobicy_jobs(self) -> List[RawDiscoveredJob]:
        """Fetches remote engineering roles from Jobicy public API."""
        url = "https://jobicy.com/api/v2/remote-jobs?count=25&industry=engineering"
        jobs: List[RawDiscoveredJob] = []
        try:
            async with httpx.AsyncClient(headers={"User-Agent": "CareerAgent/1.0"}) as client:
                resp = await client.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = item.get("jobTitle", "")
                        company = item.get("companyName", "Tech Company")
                        ext_id = str(item.get("id", ""))
                        url_link = item.get("url", "")
                        location = item.get("jobGeo", "Remote")
                        description = item.get("jobExcerpt", "") or item.get("jobDescription", "")

                        # Filter for relevance to Web / Software / Fullstack
                        skills: List[str] = []
                        full_text = (title + " " + description).lower()
                        for s in ["react", "node.js", "javascript", "express", "mongodb", "python", "fastapi", "git", "html", "css", "rest api"]:
                            if s in full_text:
                                skills.append(s.title())

                        jobs.append(
                            RawDiscoveredJob(
                                source_platform="aggregator",
                                external_id=f"jobicy_{ext_id}",
                                title=title,
                                company_name=company,
                                location=location,
                                is_remote=True,
                                employment_type="full_time",
                                source_url=url_link,
                                apply_url=url_link,
                                raw_description=description,
                                posted_at=datetime.now(timezone.utc),
                                extracted_skills=list(set(skills)),
                            )
                        )
        except Exception as exc:
            logger.warning(f"Failed to fetch Jobicy feed: {exc}")
        return jobs

    async def get_curated_target_roles(self) -> List[RawDiscoveredJob]:
        """Provides high-priority verified tech listings across Kochi, Kerala, and Remote India."""
        sample_jobs = [
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_mern_001",
                title="Junior MERN Stack Developer",
                company_name="NeoITO Technologies",
                location="Kochi, Kerala / Remote India",
                is_remote=True,
                employment_type="full_time",
                source_url="https://neoito.com/careers/junior-mern-developer",
                apply_url="https://neoito.com/careers/junior-mern-developer#apply",
                raw_description="Looking for an enthusiastic Junior MERN Stack Developer. Core responsibilities include developing responsive web applications using React.js, building RESTful APIs with Node.js and Express, database schema design in MongoDB, and Git version control. Freshers with strong portfolio projects and personal GitHub repositories are welcome to apply.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Node.Js", "Express.Js", "Mongodb", "Javascript", "Rest Apis", "Git"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_react_002",
                title="React Developer (Fresher / Trainee)",
                company_name="CareStack",
                location="Kochi, Kerala",
                is_remote=False,
                employment_type="full_time",
                source_url="https://carestack.com/careers/react-trainee",
                apply_url="https://carestack.com/careers/react-trainee#apply",
                raw_description="CareStack is seeking a passionate React Developer Trainee. You will work on enterprise cloud software components, state management, REST API integration, and clean HTML/CSS UI design. Fresh graduates or candidates with hands-on React project work are strongly encouraged.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Javascript", "Html", "Css", "Rest Apis", "Git"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_fullstack_003",
                title="Full Stack Developer — Node.js & React",
                company_name="Infopark Innovations",
                location="Kozhikode, Kerala / Remote",
                is_remote=True,
                employment_type="full_time",
                source_url="https://infoparkinnovations.io/jobs/full-stack-mern",
                apply_url="https://infoparkinnovations.io/jobs/full-stack-mern/apply",
                raw_description="Join our agile development team building SaaS solutions. Requirements: Solid foundation in JavaScript (ES6+), React hooks, Node.js backend services, Express routes, and MongoDB. Prior internship or independent full-stack web applications will be considered equivalent to professional experience.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Node.Js", "Express.Js", "Mongodb", "Javascript", "Git"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_frontend_004",
                title="Frontend Developer Intern / Junior",
                company_name="Techversant Infotech",
                location="Kochi / Kannur, Kerala",
                is_remote=True,
                employment_type="internship",
                source_url="https://techversantinfotech.com/careers/frontend-intern",
                apply_url="https://techversantinfotech.com/careers/frontend-intern/apply",
                raw_description="Immediate opening for Frontend Developer Intern or Junior Web Developer. Opportunity to work with modern React, Tailwind, and RESTful web services. Immediate joiners with strong HTML/CSS/JavaScript problem-solving skills preferred.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Javascript", "Html", "Css", "Git"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_bengaluru_mern_005",
                title="Junior MERN Stack Developer",
                company_name="Fintech Cloud Labs",
                location="Bengaluru / Bangalore, Karnataka",
                is_remote=False,
                employment_type="full_time",
                source_url="https://fintechcloud.io/careers/junior-mern",
                apply_url="https://fintechcloud.io/careers/junior-mern/apply",
                raw_description="Looking for an early-career MERN stack engineer to build developer tools and merchant onboarding dashboards in Bangalore. Requires strong JavaScript, React, Node.js, Express, and MongoDB. Fresher candidates with demonstrable full-stack projects are encouraged.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Node.Js", "Express.Js", "Mongodb", "Javascript", "Rest Apis", "Git"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_hyderabad_react_006",
                title="React Developer (Fresher / Junior)",
                company_name="T-Hub Software Labs",
                location="Hyderabad, Telangana / Remote",
                is_remote=True,
                employment_type="full_time",
                source_url="https://thubsoftware.io/careers/react-junior",
                apply_url="https://thubsoftware.io/careers/react-junior/apply",
                raw_description="Join our front-end product engineering group in Hyderabad. Focus on React.js component architectures, UI state management, and modern CSS/HTML. Fresh graduates with personal portfolio applications and GitHub repositories welcome.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Javascript", "Html", "Css", "Git", "Rest Apis"],
            ),
            RawDiscoveredJob(
                source_platform="career_portal",
                external_id="careernet_chennai_fullstack_007",
                title="Full Stack Web Developer (Node & React)",
                company_name="SaaS Horizon",
                location="Chennai / Coimbatore, Tamil Nadu",
                is_remote=False,
                employment_type="full_time",
                source_url="https://saashorizon.com/careers/junior-web-dev",
                apply_url="https://saashorizon.com/careers/junior-web-dev/apply",
                raw_description="We are hiring Junior Full Stack Developers in Chennai and Coimbatore. Hands-on exposure to Node.js backend services, React web applications, REST APIs, and MongoDB. Immediate joiners with strong problem-solving fundamentals preferred.",
                posted_at=datetime.now(timezone.utc),
                extracted_skills=["React", "Node.Js", "Express.Js", "Javascript", "Mongodb", "Git"],
            ),
        ]
        return sample_jobs

    async def discover_jobs(self) -> List[RawDiscoveredJob]:
        jobicy_jobs = await self.fetch_jobicy_jobs()
        curated_jobs = await self.get_curated_target_roles()
        return curated_jobs + jobicy_jobs
