from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RawDiscoveredJob:
    """Standardized job opportunity extracted by a source adapter."""

    source_platform: str  # greenhouse, lever, ashby, remoteok, aggregator
    external_id: str
    title: str
    company_name: str
    location: str
    is_remote: bool
    employment_type: str  # full_time, internship, contract, etc.
    source_url: str
    apply_url: str
    raw_description: str
    posted_at: Optional[datetime] = None
    extracted_skills: List[str] = field(default_factory=list)
