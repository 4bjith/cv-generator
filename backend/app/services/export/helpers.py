"""Helper functions for CV export pipelines."""

import re
import html
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.schemas.cv import CVContentSnapshot
from app.services.export.constants import (
    COLOR_PALETTES,
    FONTS,
    PAGE_SIZES,
    SPACING_CONFIGS,
    TEMPLATE_ALIASES,
    TEMPLATE_MODERN_PROFESSIONAL,
    FontConfig,
    PageSizeConfig,
    Palette,
    SpacingMetrics,
)


def normalize_template(template: Optional[str]) -> str:
    """Normalize template ID using alias mapping, defaulting to modern-professional."""
    if not template:
        return TEMPLATE_MODERN_PROFESSIONAL
    key = template.strip().lower()
    return TEMPLATE_ALIASES.get(key, TEMPLATE_MODERN_PROFESSIONAL)


def get_palette(color_scheme: Optional[str]) -> Palette:
    """Get color palette config by name, defaulting to slate."""
    if not color_scheme:
        return COLOR_PALETTES["slate"]
    key = color_scheme.strip().lower()
    return COLOR_PALETTES.get(key, COLOR_PALETTES["slate"])


def get_page_size(page_size: Optional[str]) -> PageSizeConfig:
    """Get page size config by name, defaulting to A4."""
    if not page_size:
        return PAGE_SIZES["a4"]
    key = page_size.strip().lower()
    return PAGE_SIZES.get(key, PAGE_SIZES["a4"])


def get_spacing(spacing: Optional[str]) -> SpacingMetrics:
    """Get spacing metrics by name, defaulting to normal."""
    if not spacing:
        return SPACING_CONFIGS["normal"]
    key = spacing.strip().lower()
    return SPACING_CONFIGS.get(key, SPACING_CONFIGS["normal"])


def get_font(typography: Optional[str]) -> FontConfig:
    """Get font family config by typography name, defaulting to sans."""
    if not typography:
        return FONTS["sans"]
    key = typography.strip().lower()
    return FONTS.get(key, FONTS["sans"])


def get_candidate_name(snapshot: CVContentSnapshot) -> str:
    """Extract candidate full name from basics snapshot."""
    basics = snapshot.basics
    if not basics:
        return "Candidate"
    
    if basics.name and basics.name.strip():
        return basics.name.strip()
    
    parts = []
    if basics.first_name and basics.first_name.strip():
        parts.append(basics.first_name.strip())
    if basics.last_name and basics.last_name.strip():
        parts.append(basics.last_name.strip())
    
    if parts:
        return " ".join(parts)
    
    if basics.preferred_name and basics.preferred_name.strip():
        return basics.preferred_name.strip()
    
    return "Candidate"


def get_candidate_headline(snapshot: CVContentSnapshot) -> str:
    """Extract candidate headline / professional title."""
    basics = snapshot.basics
    if not basics:
        return ""
    return (
        basics.label
        or basics.professional_headline
        or basics.primary_title
        or ""
    ).strip()


def get_candidate_location_str(snapshot: CVContentSnapshot) -> str:
    """Format location string from basics snapshot."""
    basics = snapshot.basics
    if not basics:
        return ""
    
    parts = []
    if basics.city:
        parts.append(basics.city.strip())
    if basics.state:
        parts.append(basics.state.strip())
    elif basics.location and basics.location.region:
        parts.append(basics.location.region.strip())
    if basics.country:
        parts.append(basics.country.strip())
    elif basics.country_code:
        parts.append(basics.country_code.strip())
    
    return ", ".join(parts)


def get_sanitized_export_filename(name: str, ext: str) -> str:
    """Create a safe, clean file attachment name e.g. 'Jane_Doe_CV.pdf'."""
    clean_name = re.sub(r"[^\w\s-]", "", name).strip()
    clean_name = re.sub(r"[\s_-]+", "_", clean_name)
    if not clean_name:
        clean_name = "CV_Document"
    clean_ext = ext.lstrip(".").lower()
    return f"{clean_name}_CV.{clean_ext}"


def format_date_str(date_str: Optional[str]) -> str:
    """Format an ISO date string into readable month/year (e.g. 'Jan 2022' or '2022')."""
    if not date_str:
        return ""
    date_str = date_str.strip()
    if len(date_str) == 4 and date_str.isdigit():
        return date_str
    
    try:
        # Try full YYYY-MM-DD
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%b %Y")
    except ValueError:
        pass
    
    try:
        # Try YYYY-MM
        dt = datetime.strptime(date_str[:7], "%Y-%m")
        return dt.strftime("%b %Y")
    except ValueError:
        pass
    
    return date_str


def format_date_range(start_date: Optional[str], end_date: Optional[str], is_current: bool = False) -> str:
    """Format a start and end date range into a concise human string."""
    start = format_date_str(start_date)
    if is_current:
        end = "Present"
    elif end_date:
        end = format_date_str(end_date)
    else:
        end = ""
    
    if start and end:
        return f"{start} - {end}"
    elif start:
        return start
    elif end:
        return end
    return ""


def escape_xml(text: Optional[str]) -> str:
    """Escape XML special characters for ReportLab Paragraph markup."""
    if text is None:
        return ""
    return html.escape(str(text), quote=False)


def filter_visible_items(items: List[Any], item_visibility: Optional[Dict[str, bool]]) -> List[Any]:
    """Filter out items where item_visibility[item_id] == False."""
    if not items:
        return []
    if not item_visibility:
        return items
    
    filtered = []
    for item in items:
        item_id = str(getattr(item, "id", "") or "")
        if item_id and item_visibility.get(item_id) is False:
            continue
        filtered.append(item)
    return filtered


def is_section_visible(section_key: str, section_visibility: Optional[Dict[str, bool]], has_content: bool) -> bool:
    """Check if a section should be rendered based on visibility settings and content presence."""
    if not has_content:
        return False
    if not section_visibility:
        return True
    return section_visibility.get(section_key, True)


DEFAULT_SECTION_ORDER = [
    "basics",
    "work",
    "skills",
    "projects",
    "education",
    "certificates",
    "awards",
    "languages",
]


def get_resolved_section_order(custom_order: Optional[List[str]]) -> List[str]:
    """Return ordered section keys ensuring all defaults are present."""
    if not custom_order:
        return list(DEFAULT_SECTION_ORDER)
    
    order = []
    seen = set()
    for key in custom_order:
        if key in DEFAULT_SECTION_ORDER and key not in seen:
            order.append(key)
            seen.add(key)
    
    for key in DEFAULT_SECTION_ORDER:
        if key not in seen:
            order.append(key)
            seen.add(key)
    
    return order
