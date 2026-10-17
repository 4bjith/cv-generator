"""Constants and configuration for CV export pipelines (PDF and DOCX)."""

from typing import Dict, Any, Tuple
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter

# ==============================================================================
# Supported Templates & Aliases
# ==============================================================================

TEMPLATE_MODERN_PROFESSIONAL = "modern-professional"
TEMPLATE_CLASSIC_EXECUTIVE = "classic-executive"
TEMPLATE_ATS_MINIMAL = "ats-minimal"
TEMPLATE_TECHNICAL_DEVELOPER = "technical-developer"
TEMPLATE_CONTEMPORARY_TWO_COLUMN = "contemporary-two-column"
TEMPLATE_ACADEMIC_RESEARCH = "academic-research"

TEMPLATE_ALIASES: Dict[str, str] = {
    "modern": TEMPLATE_MODERN_PROFESSIONAL,
    "corporate": TEMPLATE_MODERN_PROFESSIONAL,
    "professional": TEMPLATE_MODERN_PROFESSIONAL,
    "modern-professional": TEMPLATE_MODERN_PROFESSIONAL,
    
    "classic": TEMPLATE_CLASSIC_EXECUTIVE,
    "executive": TEMPLATE_CLASSIC_EXECUTIVE,
    "leadership": TEMPLATE_CLASSIC_EXECUTIVE,
    "classic-executive": TEMPLATE_CLASSIC_EXECUTIVE,
    
    "minimal": TEMPLATE_ATS_MINIMAL,
    "ats": TEMPLATE_ATS_MINIMAL,
    "ats-simple": TEMPLATE_ATS_MINIMAL,
    "ats-minimal": TEMPLATE_ATS_MINIMAL,
    
    "technical": TEMPLATE_TECHNICAL_DEVELOPER,
    "developer": TEMPLATE_TECHNICAL_DEVELOPER,
    "software-engineer": TEMPLATE_TECHNICAL_DEVELOPER,
    "dev": TEMPLATE_TECHNICAL_DEVELOPER,
    "technical-developer": TEMPLATE_TECHNICAL_DEVELOPER,
    
    "two-column": TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    "contemporary": TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    "sidebar": TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    "contemporary-two-column": TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    
    "academic": TEMPLATE_ACADEMIC_RESEARCH,
    "research": TEMPLATE_ACADEMIC_RESEARCH,
    "scholar": TEMPLATE_ACADEMIC_RESEARCH,
    "cv": TEMPLATE_ACADEMIC_RESEARCH,
    "academic-research": TEMPLATE_ACADEMIC_RESEARCH,
}

ALL_SUPPORTED_TEMPLATES = [
    TEMPLATE_MODERN_PROFESSIONAL,
    TEMPLATE_CLASSIC_EXECUTIVE,
    TEMPLATE_ATS_MINIMAL,
    TEMPLATE_TECHNICAL_DEVELOPER,
    TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    TEMPLATE_ACADEMIC_RESEARCH,
]

# ==============================================================================
# Color Palettes
# ==============================================================================

class Palette:
    def __init__(
        self,
        primary_hex: str,
        text_hex: str,
        accent_hex: str,
        accent_muted_hex: str,
        muted_hex: str,
        border_hex: str,
    ):
        self.primary_hex = primary_hex
        self.text_hex = text_hex
        self.accent_hex = accent_hex
        self.accent_muted_hex = accent_muted_hex
        self.muted_hex = muted_hex
        self.border_hex = border_hex
        
        # ReportLab colors
        self.primary_rl = colors.HexColor(primary_hex)
        self.text_rl = colors.HexColor(text_hex)
        self.accent_rl = colors.HexColor(accent_hex)
        self.accent_muted_rl = colors.HexColor(accent_muted_hex)
        self.muted_rl = colors.HexColor(muted_hex)
        self.border_rl = colors.HexColor(border_hex)

COLOR_PALETTES: Dict[str, Palette] = {
    "slate": Palette(
        primary_hex="#0f172a",
        text_hex="#334155",
        accent_hex="#2563eb",
        accent_muted_hex="#dbeafe",
        muted_hex="#64748b",
        border_hex="#e2e8f0",
    ),
    "blue": Palette(
        primary_hex="#0c4a6e",
        text_hex="#334155",
        accent_hex="#0284c7",
        accent_muted_hex="#e0f2fe",
        muted_hex="#64748b",
        border_hex="#bae6fd",
    ),
    "navy": Palette(
        primary_hex="#0f172a",
        text_hex="#334155",
        accent_hex="#1d4ed8",
        accent_muted_hex="#dbeafe",
        muted_hex="#64748b",
        border_hex="#cbd5e1",
    ),
    "emerald": Palette(
        primary_hex="#064e3b",
        text_hex="#334155",
        accent_hex="#059669",
        accent_muted_hex="#d1fae5",
        muted_hex="#64748b",
        border_hex="#a7f3d0",
    ),
    "burgundy": Palette(
        primary_hex="#4c0519",
        text_hex="#27272a",
        accent_hex="#9f1239",
        accent_muted_hex="#ffe4e6",
        muted_hex="#71717a",
        border_hex="#fecdd3",
    ),
    "ruby": Palette(
        primary_hex="#4c0519",
        text_hex="#27272a",
        accent_hex="#be123c",
        accent_muted_hex="#ffe4e6",
        muted_hex="#71717a",
        border_hex="#fecdd3",
    ),
    "amber": Palette(
        primary_hex="#451a03",
        text_hex="#292524",
        accent_hex="#b45309",
        accent_muted_hex="#fef3c7",
        muted_hex="#78716c",
        border_hex="#fde68a",
    ),
    "monochrome": Palette(
        primary_hex="#09090b",
        text_hex="#27272a",
        accent_hex="#18181b",
        accent_muted_hex="#f4f4f5",
        muted_hex="#52525b",
        border_hex="#d4d4d8",
    ),
    "charcoal": Palette(
        primary_hex="#18181b",
        text_hex="#27272a",
        accent_hex="#3f3f46",
        accent_muted_hex="#f4f4f5",
        muted_hex="#71717a",
        border_hex="#e4e4e7",
    ),
}

# ==============================================================================
# Page Sizes & Dimensions
# ==============================================================================

class PageSizeConfig:
    def __init__(self, key: str, width_pt: float, height_pt: float, width_in: float, height_in: float):
        self.key = key
        self.width_pt = width_pt
        self.height_pt = height_pt
        self.width_in = width_in
        self.height_in = height_in
        self.pagesize_rl = (width_pt, height_pt)

PAGE_SIZES: Dict[str, PageSizeConfig] = {
    "a4": PageSizeConfig("a4", 595.27, 841.89, 8.267, 11.692),
    "letter": PageSizeConfig("letter", 612.0, 792.0, 8.5, 11.0),
    "us-letter": PageSizeConfig("us-letter", 612.0, 792.0, 8.5, 11.0),
}

# ==============================================================================
# Spacing & Metrics
# ==============================================================================

class SpacingMetrics:
    def __init__(
        self,
        margin_pt: float,
        margin_in: float,
        body_font_size: float,
        body_leading: float,
        heading1_size: float,
        heading2_size: float,
        heading3_size: float,
        section_gap: float,
        item_gap: float,
    ):
        self.margin_pt = margin_pt
        self.margin_in = margin_in
        self.body_font_size = body_font_size
        self.body_leading = body_leading
        self.heading1_size = heading1_size
        self.heading2_size = heading2_size
        self.heading3_size = heading3_size
        self.section_gap = section_gap
        self.item_gap = item_gap

SPACING_CONFIGS: Dict[str, SpacingMetrics] = {
    "compact": SpacingMetrics(
        margin_pt=36.0,  # 0.5 in
        margin_in=0.5,
        body_font_size=9.0,
        body_leading=11.5,
        heading1_size=18.0,
        heading2_size=11.0,
        heading3_size=9.5,
        section_gap=8.0,
        item_gap=4.0,
    ),
    "normal": SpacingMetrics(
        margin_pt=48.0,  # ~0.67 in
        margin_in=0.67,
        body_font_size=9.5,
        body_leading=12.5,
        heading1_size=20.0,
        heading2_size=11.5,
        heading3_size=10.0,
        section_gap=11.0,
        item_gap=5.5,
    ),
    "relaxed": SpacingMetrics(
        margin_pt=60.0,  # ~0.83 in
        margin_in=0.83,
        body_font_size=10.0,
        body_leading=13.5,
        heading1_size=22.0,
        heading2_size=12.5,
        heading3_size=10.5,
        section_gap=14.0,
        item_gap=7.0,
    ),
}

# ==============================================================================
# Typography Families
# ==============================================================================

class FontConfig:
    def __init__(self, rl_regular: str, rl_bold: str, rl_italic: str, rl_bold_italic: str, docx_family: str):
        self.rl_regular = rl_regular
        self.rl_bold = rl_bold
        self.rl_italic = rl_italic
        self.rl_bold_italic = rl_bold_italic
        self.docx_family = docx_family

FONTS: Dict[str, FontConfig] = {
    "sans": FontConfig(
        rl_regular="Helvetica",
        rl_bold="Helvetica-Bold",
        rl_italic="Helvetica-Oblique",
        rl_bold_italic="Helvetica-BoldOblique",
        docx_family="Arial",
    ),
    "serif": FontConfig(
        rl_regular="Times-Roman",
        rl_bold="Times-Bold",
        rl_italic="Times-Italic",
        rl_bold_italic="Times-BoldItalic",
        docx_family="Times New Roman",
    ),
    "mono": FontConfig(
        rl_regular="Courier",
        rl_bold="Courier-Bold",
        rl_italic="Courier-Oblique",
        rl_bold_italic="Courier-BoldOblique",
        docx_family="Courier New",
    ),
}
