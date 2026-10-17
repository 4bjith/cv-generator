"""Production-quality PDF export service for CV templates using ReportLab."""

import io
from typing import Any, Dict, List, Optional, Tuple
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas

from app.schemas.cv import CVContentSnapshot
from app.services.export.constants import (
    TEMPLATE_ACADEMIC_RESEARCH,
    TEMPLATE_ATS_MINIMAL,
    TEMPLATE_CLASSIC_EXECUTIVE,
    TEMPLATE_CONTEMPORARY_TWO_COLUMN,
    TEMPLATE_MODERN_PROFESSIONAL,
    TEMPLATE_TECHNICAL_DEVELOPER,
    FontConfig,
    PageSizeConfig,
    Palette,
    SpacingMetrics,
)
from app.services.export.helpers import (
    escape_xml,
    filter_visible_items,
    format_date_range,
    format_date_str,
    get_candidate_headline,
    get_candidate_location_str,
    get_candidate_name,
    get_font,
    get_page_size,
    get_palette,
    get_resolved_section_order,
    get_spacing,
    is_section_visible,
    normalize_template,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for adding clean page numbers to multi-page CVs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if num_pages > 1:
                self.saveState()
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#64748b"))
                page_str = f"Page {self._pageNumber} of {num_pages}"
                self.drawRightString(self._pagesize[0] - 36, 18, page_str)
                self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


class PDFStyles:
    """Encapsulates paragraph and flowable styles based on palette, font, and spacing."""

    def __init__(
        self,
        palette: Palette,
        font: FontConfig,
        spacing: SpacingMetrics,
        template_id: str,
    ) -> None:
        self.palette = palette
        self.font = font
        self.spacing = spacing
        self.template_id = template_id

        # Candidate Name / Main Title
        is_centered = template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH)
        self.name_style = ParagraphStyle(
            "CVName",
            fontName=font.rl_bold,
            fontSize=spacing.heading1_size,
            leading=spacing.heading1_size * 1.15,
            textColor=palette.primary_rl,
            alignment=1 if is_centered else 0,
            spaceAfter=3,
        )

        # Professional Headline / Title
        headline_color = (
            palette.text_rl if template_id == TEMPLATE_ATS_MINIMAL
            else palette.accent_rl
        )
        headline_font = (
            font.rl_italic if template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH)
            else font.rl_bold
        )
        self.headline_style = ParagraphStyle(
            "CVHeadline",
            fontName=headline_font,
            fontSize=spacing.body_font_size + 1.5,
            leading=(spacing.body_font_size + 1.5) * 1.25,
            textColor=headline_color,
            alignment=1 if is_centered else 0,
            spaceAfter=4,
        )

        # Contact Details
        self.contact_style = ParagraphStyle(
            "CVContact",
            fontName=font.rl_regular,
            fontSize=spacing.body_font_size - 0.8,
            leading=(spacing.body_font_size - 0.8) * 1.3,
            textColor=palette.muted_rl,
            alignment=1 if is_centered else 0,
            spaceAfter=4,
        )

        # Section Heading
        section_heading_color = (
            colors.HexColor("#000000") if template_id == TEMPLATE_ATS_MINIMAL
            else palette.primary_rl
        )
        self.section_heading_style = ParagraphStyle(
            "CVSectionHeading",
            fontName=font.rl_bold,
            fontSize=spacing.heading2_size,
            leading=spacing.heading2_size * 1.2,
            textColor=section_heading_color,
            spaceBefore=spacing.section_gap,
            spaceAfter=2,
            keepWithNext=True,
        )

        # Item Primary Title (Role / Degree / Project Name)
        self.item_title_style = ParagraphStyle(
            "CVItemTitle",
            fontName=font.rl_bold,
            fontSize=spacing.heading3_size,
            leading=spacing.heading3_size * 1.25,
            textColor=palette.primary_rl,
        )

        # Item Subtitle (Company / Institution / Venue)
        sub_font = (
            font.rl_italic if template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH)
            else font.rl_regular
        )
        self.item_subtitle_style = ParagraphStyle(
            "CVItemSubtitle",
            fontName=sub_font,
            fontSize=spacing.body_font_size,
            leading=spacing.body_font_size * 1.25,
            textColor=palette.text_rl,
        )

        # Item Meta / Date
        self.item_date_style = ParagraphStyle(
            "CVItemDate",
            fontName=font.rl_regular,
            fontSize=spacing.body_font_size - 0.8,
            leading=(spacing.body_font_size - 0.8) * 1.2,
            textColor=palette.muted_rl,
            alignment=2,  # Right-aligned
        )

        # Body Text
        self.body_style = ParagraphStyle(
            "CVBody",
            fontName=font.rl_regular,
            fontSize=spacing.body_font_size,
            leading=spacing.body_leading,
            textColor=palette.text_rl,
            spaceAfter=spacing.item_gap,
        )

        # Bullet List Items
        self.bullet_style = ParagraphStyle(
            "CVBullet",
            fontName=font.rl_regular,
            fontSize=spacing.body_font_size - 0.2,
            leading=spacing.body_leading - 0.5,
            textColor=palette.text_rl,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=2,
        )

        # Tech Stack & Badges
        self.tag_style = ParagraphStyle(
            "CVTag",
            fontName=font.rl_bold if template_id == TEMPLATE_TECHNICAL_DEVELOPER else font.rl_regular,
            fontSize=spacing.body_font_size - 1.0,
            leading=(spacing.body_font_size - 1.0) * 1.2,
            textColor=palette.accent_rl,
            spaceAfter=2,
        )

        # Sidebar Heading (Two-Column)
        self.sidebar_heading_style = ParagraphStyle(
            "CVSidebarHeading",
            fontName=font.rl_bold,
            fontSize=spacing.heading3_size + 0.5,
            leading=(spacing.heading3_size + 0.5) * 1.2,
            textColor=palette.primary_rl,
            spaceBefore=spacing.section_gap - 2,
            spaceAfter=2,
            keepWithNext=True,
        )


def _build_contact_line(snapshot: CVContentSnapshot, template_id: str, styles: PDFStyles) -> List[Paragraph]:
    """Build formatted contact details line(s)."""
    basics = snapshot.basics
    if not basics:
        return []

    items = []
    if basics.email:
        items.append(f'<a href="mailto:{escape_xml(basics.email)}">{escape_xml(basics.email)}</a>')
    if basics.phone:
        items.append(escape_xml(basics.phone))
    
    loc = get_candidate_location_str(snapshot)
    if loc:
        items.append(escape_xml(loc))
    
    if basics.url:
        clean_url = basics.url.replace("https://", "").replace("http://", "").rstrip("/")
        items.append(f'<a href="{escape_xml(basics.url)}">{escape_xml(clean_url)}</a>')
    
    for prof in basics.profiles:
        if prof.url:
            label = prof.network or prof.username or "Profile"
            items.append(f'<a href="{escape_xml(prof.url)}">{escape_xml(label)}</a>')

    if not items:
        return []

    separator = "  |  " if template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ATS_MINIMAL) else "  •  "
    line_html = separator.join(items)
    return [Paragraph(line_html, styles.contact_style)]


def _build_section_header(title: str, styles: PDFStyles, template_id: str, printable_width: float) -> List[Any]:
    """Build section title with appropriate divider rule styling."""
    flowables: List[Any] = [Paragraph(escape_xml(title.upper()), styles.section_heading_style)]

    if template_id == TEMPLATE_ATS_MINIMAL:
        flowables.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#000000"),
                spaceBefore=1,
                spaceAfter=styles.spacing.item_gap,
            )
        )
    elif template_id == TEMPLATE_CLASSIC_EXECUTIVE:
        flowables.append(
            HRFlowable(
                width="100%",
                thickness=0.75,
                color=styles.palette.border_rl,
                spaceBefore=1,
                spaceAfter=styles.spacing.item_gap,
            )
        )
    elif template_id == TEMPLATE_ACADEMIC_RESEARCH:
        flowables.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=styles.palette.primary_rl,
                spaceBefore=1,
                spaceAfter=styles.spacing.item_gap,
            )
        )
    else:
        # Modern professional & technical developer
        flowables.append(
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=styles.palette.accent_rl,
                spaceBefore=1,
                spaceAfter=styles.spacing.item_gap,
            )
        )

    return flowables


def _build_work_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate work experience flowables."""
    work_items = filter_visible_items(snapshot.work, item_visibility)
    if not work_items:
        return []

    story: List[Any] = []
    left_w = printable_width * 0.65
    right_w = printable_width * 0.35

    for idx, item in enumerate(work_items):
        item_story: List[Any] = []
        position = escape_xml(item.position or "Position")
        company = escape_xml(item.name or item.company or "")
        title_text = f"<b>{position}</b>"
        if company:
            title_text += f" - {company}"

        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        is_curr = bool(getattr(item, "is_current", False) or getattr(item, "isCurrent", False))
        date_str = format_date_range(start_d, end_d, is_curr)
        loc_str = escape_xml(item.location or "")
        meta_parts = [p for p in [date_str, loc_str] if p]
        meta_text = " | ".join(meta_parts)

        # Header 2-column table
        table_data = [
            [
                Paragraph(title_text, styles.item_title_style),
                Paragraph(meta_text, styles.item_date_style),
            ]
        ]
        t = Table(table_data, colWidths=[left_w, right_w])
        t.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ])
        )
        item_story.append(t)

        # Summary
        if item.summary:
            item_story.append(Paragraph(escape_xml(item.summary), styles.body_style))

        # Highlights / bullet points
        bullets = item.highlights or item.responsibilities or []
        for bullet in bullets:
            if bullet and bullet.strip():
                item_story.append(
                    Paragraph(f"&bull;&nbsp; {escape_xml(bullet.strip())}", styles.bullet_style)
                )

        # Technologies
        techs = item.technologies or []
        if techs:
            tech_str = f"<b>Tech Stack:</b> {escape_xml(', '.join(techs))}"
            item_story.append(Paragraph(tech_str, styles.tag_style))

        item_story.append(Spacer(1, styles.spacing.item_gap))
        story.append(KeepTogether(item_story))

    return story


def _build_skills_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate skills flowables."""
    skills = filter_visible_items(snapshot.skills, item_visibility)
    if not skills:
        return []

    story: List[Any] = []
    # Check if skills have keywords or categories
    has_categories = any(s.keywords or s.category for s in skills)

    if has_categories:
        for skill in skills:
            category_name = escape_xml(skill.name or skill.category or "Skills")
            keywords = skill.keywords or []
            if keywords:
                kw_str = ", ".join(keywords)
            else:
                kw_str = skill.level or ""
            line = f"<b>{category_name}:</b> {escape_xml(kw_str)}" if kw_str else f"<b>{category_name}</b>"
            story.append(Paragraph(line, styles.body_style))
    else:
        # Group skills into a clean multi-item inline list
        skill_names = [escape_xml(s.name) for s in skills if s.name]
        if skill_names:
            line = "  •  ".join(skill_names)
            story.append(Paragraph(line, styles.body_style))

    story.append(Spacer(1, styles.spacing.item_gap))
    return story


def _build_projects_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate projects flowables."""
    projects = filter_visible_items(snapshot.projects, item_visibility)
    if not projects:
        return []

    story: List[Any] = []
    left_w = printable_width * 0.7
    right_w = printable_width * 0.3

    for item in projects:
        item_story: List[Any] = []
        name = escape_xml(item.name or "Project")
        if item.url:
            name_text = f'<b><a href="{escape_xml(item.url)}">{name}</a></b>'
        else:
            name_text = f"<b>{name}</b>"

        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        date_str = format_date_range(start_d, end_d)
        table_data = [
            [
                Paragraph(name_text, styles.item_title_style),
                Paragraph(date_str, styles.item_date_style),
            ]
        ]
        t = Table(table_data, colWidths=[left_w, right_w])
        t.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ])
        )
        item_story.append(t)

        if item.description:
            item_story.append(Paragraph(escape_xml(item.description), styles.body_style))

        for bullet in (item.highlights or []):
            if bullet and bullet.strip():
                item_story.append(
                    Paragraph(f"&bull;&nbsp; {escape_xml(bullet.strip())}", styles.bullet_style)
                )

        techs = item.keywords or item.technologies or []
        if techs:
            tech_str = f"<b>Technologies:</b> {escape_xml(', '.join(techs))}"
            item_story.append(Paragraph(tech_str, styles.tag_style))

        item_story.append(Spacer(1, styles.spacing.item_gap))
        story.append(KeepTogether(item_story))

    return story


def _build_education_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate education flowables."""
    education = filter_visible_items(snapshot.education, item_visibility)
    if not education:
        return []

    story: List[Any] = []
    left_w = printable_width * 0.7
    right_w = printable_width * 0.3

    for item in education:
        item_story: List[Any] = []
        deg = getattr(item, "degree", None) or getattr(item, "studyType", None) or ""
        area = getattr(item, "area", None) or getattr(item, "field_of_study", None) or ""
        inst = getattr(item, "institution", "") or ""

        degree_text = escape_xml(deg)
        area_text = escape_xml(area)
        inst_text = escape_xml(inst)

        if degree_text and area_text:
            deg_area = f"{degree_text} in {area_text}"
        else:
            deg_area = degree_text or area_text or "Degree"

        title_text = f"<b>{deg_area}</b>"
        if inst_text:
            title_text += f" - {inst_text}"

        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        date_str = format_date_range(start_d, end_d)
        table_data = [
            [
                Paragraph(title_text, styles.item_title_style),
                Paragraph(date_str, styles.item_date_style),
            ]
        ]
        t = Table(table_data, colWidths=[left_w, right_w])
        t.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ])
        )
        item_story.append(t)

        score_val = getattr(item, "score", None) or getattr(item, "grade", None)
        if score_val:
            gpa_text = f"GPA / Score: {escape_xml(score_val)}"
            item_story.append(Paragraph(gpa_text, styles.body_style))

        bullets = getattr(item, "courses", None) or getattr(item, "achievements", None) or getattr(item, "highlights", None) or []
        for bullet in bullets:
            if bullet and bullet.strip():
                item_story.append(
                    Paragraph(f"&bull;&nbsp; {escape_xml(bullet.strip())}", styles.bullet_style)
                )

        item_story.append(Spacer(1, styles.spacing.item_gap))
        story.append(KeepTogether(item_story))

    return story


def _build_certificates_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate certificates flowables."""
    certs = filter_visible_items(snapshot.certificates, item_visibility)
    if not certs:
        return []

    story: List[Any] = []
    left_w = printable_width * 0.75
    right_w = printable_width * 0.25

    for item in certs:
        name = escape_xml(item.name or "Certificate")
        issuer = escape_xml(item.issuer or "")
        line = f"<b>{name}</b>"
        if issuer:
            line += f" - {issuer}"
        date_str = format_date_str(item.date)

        table_data = [
            [
                Paragraph(line, styles.item_title_style),
                Paragraph(date_str, styles.item_date_style),
            ]
        ]
        t = Table(table_data, colWidths=[left_w, right_w])
        t.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ])
        )
        story.append(t)

    story.append(Spacer(1, styles.spacing.item_gap))
    return story


def _build_awards_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    printable_width: float,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate awards flowables."""
    awards = filter_visible_items(snapshot.awards, item_visibility)
    if not awards:
        return []

    story: List[Any] = []
    left_w = printable_width * 0.75
    right_w = printable_width * 0.25

    for item in awards:
        title = escape_xml(item.title or "Award")
        awarder = escape_xml(item.awarder or "")
        line = f"<b>{title}</b>"
        if awarder:
            line += f" - {awarder}"
        date_str = format_date_str(item.date)

        table_data = [
            [
                Paragraph(line, styles.item_title_style),
                Paragraph(date_str, styles.item_date_style),
            ]
        ]
        t = Table(table_data, colWidths=[left_w, right_w])
        t.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ])
        )
        story.append(t)
        if item.summary:
            story.append(Paragraph(escape_xml(item.summary), styles.body_style))

    story.append(Spacer(1, styles.spacing.item_gap))
    return story


def _build_languages_section(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    item_visibility: Optional[Dict[str, bool]],
) -> List[Any]:
    """Generate languages flowables."""
    langs = filter_visible_items(snapshot.languages, item_visibility)
    if not langs:
        return []

    lang_strs = []
    for item in langs:
        l_name = escape_xml(item.language or "")
        fluency = escape_xml(item.fluency or "")
        if l_name and fluency:
            lang_strs.append(f"<b>{l_name}</b> ({fluency})")
        elif l_name:
            lang_strs.append(f"<b>{l_name}</b>")

    if not lang_strs:
        return []

    line = "  •  ".join(lang_strs)
    return [Paragraph(line, styles.body_style), Spacer(1, styles.spacing.item_gap)]


def generate_cv_pdf(
    snapshot: CVContentSnapshot,
    overrides: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Generate production-ready, searchable vector PDF from CV content snapshot.
    
    Supports:
    - All 6 templates (modern-professional, classic-executive, ats-minimal,
      technical-developer, contemporary-two-column, academic-research)
    - Page sizes: A4 and US Letter
    - Spacing densities: compact, normal, relaxed
    - Color palettes: slate, blue, emerald, burgundy, amber, monochrome
    - Typography: sans, serif, mono
    - Section and item visibility rules and custom section ordering
    """
    presentation = snapshot.presentation
    p_data = presentation.model_dump(mode="python") if presentation else {}
    if overrides:
        p_data.update(overrides)

    template_id = normalize_template(p_data.get("template"))
    palette = get_palette(p_data.get("color_scheme"))
    page_size_cfg = get_page_size(p_data.get("page_size"))
    spacing = get_spacing(p_data.get("spacing"))
    font = get_font(p_data.get("typography"))

    section_visibility = p_data.get("section_visibility") or {}
    item_visibility = p_data.get("item_visibility") or {}
    section_order = get_resolved_section_order(p_data.get("section_order"))

    # For academic-research template, default education-first if order is standard
    if template_id == TEMPLATE_ACADEMIC_RESEARCH and "education" in section_order:
        sec_order = list(section_order)
        sec_order.remove("education")
        sec_order.insert(1, "education")
        section_order = sec_order

    styles = PDFStyles(palette, font, spacing, template_id)
    page_w, page_h = page_size_cfg.pagesize_rl
    margin = spacing.margin_pt
    printable_w = page_w - (2 * margin)

    buf = io.BytesIO()

    # --------------------------------------------------------------------------
    # CONTEMPORARY TWO-COLUMN TEMPLATE BUILDER
    # --------------------------------------------------------------------------
    if template_id == TEMPLATE_CONTEMPORARY_TWO_COLUMN:
        return _build_contemporary_two_column_pdf(
            snapshot=snapshot,
            styles=styles,
            page_w=page_w,
            page_h=page_h,
            margin=margin,
            printable_w=printable_w,
            section_visibility=section_visibility,
            item_visibility=item_visibility,
            section_order=section_order,
        )

    # --------------------------------------------------------------------------
    # SINGLE-COLUMN TEMPLATES BUILDER (Modern, Classic, ATS, Technical, Academic)
    # --------------------------------------------------------------------------
    doc = SimpleDocTemplate(
        buf,
        pagesize=page_size_cfg.pagesize_rl,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    story: List[Any] = []

    # 1. Candidate Header
    candidate_name = get_candidate_name(snapshot)
    headline = get_candidate_headline(snapshot)
    story.append(Paragraph(escape_xml(candidate_name), styles.name_style))
    if headline:
        story.append(Paragraph(escape_xml(headline), styles.headline_style))

    contact_flowables = _build_contact_line(snapshot, template_id, styles)
    for cf in contact_flowables:
        story.append(cf)

    # Header Divider Rule
    if template_id == TEMPLATE_CLASSIC_EXECUTIVE:
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=palette.border_rl,
                spaceBefore=6,
                spaceAfter=spacing.section_gap,
            )
        )
    elif template_id == TEMPLATE_ATS_MINIMAL:
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.HexColor("#000000"),
                spaceBefore=4,
                spaceAfter=spacing.section_gap - 2,
            )
        )
    elif template_id == TEMPLATE_ACADEMIC_RESEARCH:
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=palette.primary_rl,
                spaceBefore=6,
                spaceAfter=spacing.section_gap,
            )
        )
    else:
        # Modern & Technical: accent bar
        story.append(
            HRFlowable(
                width="100%",
                thickness=2.0,
                color=palette.accent_rl,
                spaceBefore=6,
                spaceAfter=spacing.section_gap,
            )
        )

    # 2. Ordered Sections
    basics = snapshot.basics
    has_summary = bool(basics and (basics.summary or basics.base_summary))

    for sec_key in section_order:
        if sec_key == "basics":
            if is_section_visible("basics", section_visibility, has_summary):
                summary_text = (basics.summary or basics.base_summary or "").strip()
                title = "Research Profile" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Professional Summary"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.append(Paragraph(escape_xml(summary_text), styles.body_style))

        elif sec_key == "work":
            if is_section_visible("work", section_visibility, len(snapshot.work) > 0):
                title = "Research & Academic Experience" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Professional Experience"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_work_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "skills":
            if is_section_visible("skills", section_visibility, len(snapshot.skills) > 0):
                title = "Technical Skills & Competencies" if template_id == TEMPLATE_TECHNICAL_DEVELOPER else "Core Competencies & Skills"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_skills_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "projects":
            if is_section_visible("projects", section_visibility, len(snapshot.projects) > 0):
                title = "Publications & Selected Projects" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Key Projects & Initiatives"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_projects_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "education":
            if is_section_visible("education", section_visibility, len(snapshot.education) > 0):
                title = "Education & Academic Credentials" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Education"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_education_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "certificates":
            if is_section_visible("certificates", section_visibility, len(snapshot.certificates) > 0):
                title = "Certifications & Professional Credentials"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_certificates_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "awards":
            if is_section_visible("awards", section_visibility, len(snapshot.awards) > 0):
                title = "Honors, Grants & Fellowships" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Honors & Achievements"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_awards_section(snapshot, styles, printable_w, item_visibility))

        elif sec_key == "languages":
            if is_section_visible("languages", section_visibility, len(snapshot.languages) > 0):
                title = "Languages"
                story.extend(_build_section_header(title, styles, template_id, printable_w))
                story.extend(_build_languages_section(snapshot, styles, item_visibility))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()


def _build_contemporary_two_column_pdf(
    snapshot: CVContentSnapshot,
    styles: PDFStyles,
    page_w: float,
    page_h: float,
    margin: float,
    printable_w: float,
    section_visibility: Dict[str, bool],
    item_visibility: Dict[str, bool],
    section_order: List[str],
) -> bytes:
    """Build contemporary two-column PDF using multi-frame BaseDocTemplate."""
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=(page_w, page_h))

    header_h = 65.0
    gap = 16.0
    sidebar_w = printable_w * 0.33
    main_w = printable_w - sidebar_w - gap
    body_h = page_h - (2 * margin) - header_h - 10.0

    # Page 1 frames: header across full width, sidebar on left, main on right
    f_header = Frame(
        margin,
        page_h - margin - header_h,
        printable_w,
        header_h,
        id="f_header",
        topPadding=0,
        bottomPadding=0,
        leftPadding=0,
        rightPadding=0,
    )
    f_sidebar = Frame(
        margin,
        margin,
        sidebar_w,
        body_h,
        id="f_sidebar",
        topPadding=0,
        bottomPadding=0,
        leftPadding=0,
        rightPadding=6,
    )
    f_main = Frame(
        margin + sidebar_w + gap,
        margin,
        main_w,
        body_h,
        id="f_main",
        topPadding=0,
        bottomPadding=0,
        leftPadding=6,
        rightPadding=0,
    )

    # Later pages frame: full printable area for remaining content flow
    f_later = Frame(
        margin,
        margin,
        printable_w,
        page_h - (2 * margin),
        id="f_later",
        topPadding=0,
        bottomPadding=0,
        leftPadding=0,
        rightPadding=0,
    )

    t_first = PageTemplate(id="FirstPage", frames=[f_header, f_sidebar, f_main])
    t_later = PageTemplate(id="LaterPages", frames=[f_later])
    doc.addPageTemplates([t_first, t_later])

    story: List[Any] = []

    # 1. Header Frame
    candidate_name = get_candidate_name(snapshot)
    headline = get_candidate_headline(snapshot)
    story.append(Paragraph(escape_xml(candidate_name), styles.name_style))
    if headline:
        story.append(Paragraph(escape_xml(headline), styles.headline_style))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=styles.palette.accent_rl,
            spaceBefore=3,
            spaceAfter=0,
        )
    )
    story.append(FrameBreak())

    # 2. Sidebar Frame: Contact, Skills, Education, Certifications, Languages
    basics = snapshot.basics
    story.append(Paragraph("<b>CONTACT</b>", styles.sidebar_heading_style))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.0,
            color=styles.palette.border_rl,
            spaceBefore=1,
            spaceAfter=4,
        )
    )
    contact_parts = []
    if basics:
        if basics.email:
            contact_parts.append(f'✉ {escape_xml(basics.email)}')
        if basics.phone:
            contact_parts.append(f'☎ {escape_xml(basics.phone)}')
        loc = get_candidate_location_str(snapshot)
        if loc:
            contact_parts.append(f'⚲ {escape_xml(loc)}')
        if basics.url:
            clean_url = basics.url.replace("https://", "").replace("http://", "").rstrip("/")
            contact_parts.append(f'🔗 {escape_xml(clean_url)}')
        for prof in basics.profiles:
            if prof.url:
                contact_parts.append(f'• {escape_xml(prof.network or prof.username or "Link")}')

    for cp in contact_parts:
        story.append(Paragraph(cp, styles.contact_style))
    story.append(Spacer(1, styles.spacing.item_gap))

    # Sidebar Skills
    if is_section_visible("skills", section_visibility, len(snapshot.skills) > 0):
        story.append(Paragraph("<b>SKILLS</b>", styles.sidebar_heading_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=styles.palette.border_rl,
                spaceBefore=1,
                spaceAfter=4,
            )
        )
        story.extend(_build_skills_section(snapshot, styles, sidebar_w, item_visibility))

    # Sidebar Education
    if is_section_visible("education", section_visibility, len(snapshot.education) > 0):
        story.append(Paragraph("<b>EDUCATION</b>", styles.sidebar_heading_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=styles.palette.border_rl,
                spaceBefore=1,
                spaceAfter=4,
            )
        )
        story.extend(_build_education_section(snapshot, styles, sidebar_w, item_visibility))

    # Sidebar Certifications
    if is_section_visible("certificates", section_visibility, len(snapshot.certificates) > 0):
        story.append(Paragraph("<b>CERTIFICATIONS</b>", styles.sidebar_heading_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=styles.palette.border_rl,
                spaceBefore=1,
                spaceAfter=4,
            )
        )
        story.extend(_build_certificates_section(snapshot, styles, sidebar_w, item_visibility))

    # Sidebar Languages
    if is_section_visible("languages", section_visibility, len(snapshot.languages) > 0):
        story.append(Paragraph("<b>LANGUAGES</b>", styles.sidebar_heading_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.0,
                color=styles.palette.border_rl,
                spaceBefore=1,
                spaceAfter=4,
            )
        )
        story.extend(_build_languages_section(snapshot, styles, item_visibility))

    # Transition to main frame and set LaterPages template for overflow
    story.append(NextPageTemplate("LaterPages"))
    story.append(FrameBreak())

    # 3. Main Frame: Summary, Work Experience, Projects, Awards
    has_summary = bool(basics and (basics.summary or basics.base_summary))
    if is_section_visible("basics", section_visibility, has_summary):
        summary_text = (basics.summary or basics.base_summary or "").strip()
        story.extend(_build_section_header("Profile Summary", styles, TEMPLATE_CONTEMPORARY_TWO_COLUMN, main_w))
        story.append(Paragraph(escape_xml(summary_text), styles.body_style))

    if is_section_visible("work", section_visibility, len(snapshot.work) > 0):
        story.extend(_build_section_header("Experience", styles, TEMPLATE_CONTEMPORARY_TWO_COLUMN, main_w))
        story.extend(_build_work_section(snapshot, styles, main_w, item_visibility))

    if is_section_visible("projects", section_visibility, len(snapshot.projects) > 0):
        story.extend(_build_section_header("Key Projects", styles, TEMPLATE_CONTEMPORARY_TWO_COLUMN, main_w))
        story.extend(_build_projects_section(snapshot, styles, main_w, item_visibility))

    if is_section_visible("awards", section_visibility, len(snapshot.awards) > 0):
        story.extend(_build_section_header("Achievements", styles, TEMPLATE_CONTEMPORARY_TWO_COLUMN, main_w))
        story.extend(_build_awards_section(snapshot, styles, main_w, item_visibility))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
