"""Production-quality editable DOCX export service for CV templates using python-docx."""

import io
from typing import Any, Dict, List, Optional
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor

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


def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert hex string (e.g. '#2563eb') to python-docx RGBColor."""
    clean = hex_str.lstrip("#")
    if len(clean) != 6:
        return RGBColor(15, 23, 42)
    return RGBColor(*(int(clean[i : i + 2], 16) for i in (0, 2, 4)))


def add_hyperlink(
    paragraph: Any,
    url: str,
    text: str,
    color_hex: str = "2563EB",
    underline: bool = True,
    font_name: Optional[str] = None,
    font_size_pt: Optional[float] = None,
) -> None:
    """Add a true OpenXML hyperlink run to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    ns = nsdecls("w", "r")
    clean_color = color_hex.lstrip("#")

    u_tag = "<w:u w:val='single'/>" if underline else ""
    r_fonts_tag = f"<w:rFonts w:ascii='{font_name}' w:hAnsi='{font_name}'/>" if font_name else ""
    sz_tag = f"<w:sz w:val='{int(font_size_pt * 2)}'/>" if font_size_pt else ""

    hyperlink = parse_xml(
        f"<w:hyperlink {ns} r:id='{r_id}'>"
        f"<w:r><w:rPr><w:color w:val='{clean_color}'/>{u_tag}{r_fonts_tag}{sz_tag}</w:rPr>"
        f"<w:t>{text}</w:t></w:r>"
        f"</w:hyperlink>"
    )
    paragraph._p.append(hyperlink)


def add_paragraph_bottom_border(
    paragraph: Any,
    color_hex: str = "2563EB",
    size_eighth_pts: str = "12",
) -> None:
    """Add a styled bottom border line under a heading paragraph."""
    clean_color = color_hex.lstrip("#")
    pPr = paragraph._p.get_or_add_pPr()
    ns = nsdecls("w")
    border = parse_xml(
        f"<w:pBdr {ns}><w:bottom w:val='single' w:sz='{size_eighth_pts}' w:space='4' w:color='{clean_color}'/></w:pBdr>"
    )
    pPr.append(border)


def set_cell_background(cell: Any, fill_hex: str) -> None:
    """Set background color shading for a table cell."""
    clean_fill = fill_hex.lstrip("#")
    tcPr = cell._tc.get_or_add_tcPr()
    ns = nsdecls("w")
    shd = parse_xml(f"<w:shd {ns} w:fill='{clean_fill}'/>")
    tcPr.append(shd)


def make_borderless_table(table: Any) -> None:
    """Ensure table has zero borders across all cells."""
    table.style = "Normal Table"
    tblPr = table._tbl.tblPr
    ns = nsdecls("w")
    borders = parse_xml(
        f"<w:tblBorders {ns}>"
        "<w:top w:val='none'/>"
        "<w:left w:val='none'/>"
        "<w:bottom w:val='none'/>"
        "<w:right w:val='none'/>"
        "<w:insideH w:val='none'/>"
        "<w:insideV w:val='none'/>"
        "</w:tblBorders>"
    )
    tblPr.append(borders)


class DOCXFormatter:
    """Encapsulates styling operations for Word document generation."""

    def __init__(
        self,
        doc: Any,
        palette: Palette,
        font: FontConfig,
        spacing: SpacingMetrics,
        template_id: str,
    ) -> None:
        self.doc = doc
        self.palette = palette
        self.font = font
        self.spacing = spacing
        self.template_id = template_id

        self.primary_rgb = hex_to_rgb(palette.primary_hex)
        self.text_rgb = hex_to_rgb(palette.text_hex)
        self.accent_rgb = hex_to_rgb(palette.accent_hex)
        self.muted_rgb = hex_to_rgb(palette.muted_hex)

    def add_title(self, text: str) -> Any:
        p = self.doc.add_paragraph()
        if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.bold = True
        run.font.name = self.font.docx_family
        run.font.size = Pt(self.spacing.heading1_size)
        run.font.color.rgb = self.primary_rgb
        return p

    def add_headline(self, text: str) -> Any:
        p = self.doc.add_paragraph()
        if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = self.font.docx_family
        run.font.size = Pt(self.spacing.body_font_size + 1.5)
        if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH):
            run.italic = True
            run.font.color.rgb = self.text_rgb
        elif self.template_id == TEMPLATE_ATS_MINIMAL:
            run.font.color.rgb = self.text_rgb
        else:
            run.bold = True
            run.font.color.rgb = self.accent_rgb
        return p

    def add_contact_paragraph(self, snapshot: CVContentSnapshot) -> Any:
        basics = snapshot.basics
        if not basics:
            return None

        p = self.doc.add_paragraph()
        if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(self.spacing.section_gap / 2)

        sep = "  |  " if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ATS_MINIMAL) else "  •  "
        first = True

        def _add_sep():
            nonlocal first
            if not first:
                r_sep = p.add_run(sep)
                r_sep.font.name = self.font.docx_family
                r_sep.font.size = Pt(self.spacing.body_font_size - 1.0)
                r_sep.font.color.rgb = self.muted_rgb
            first = False

        if basics.email:
            _add_sep()
            add_hyperlink(
                p,
                f"mailto:{basics.email}",
                basics.email,
                self.palette.accent_hex,
                underline=False,
                font_name=self.font.docx_family,
                font_size_pt=self.spacing.body_font_size - 1.0,
            )

        if basics.phone:
            _add_sep()
            r = p.add_run(basics.phone)
            r.font.name = self.font.docx_family
            r.font.size = Pt(self.spacing.body_font_size - 1.0)
            r.font.color.rgb = self.muted_rgb

        loc = get_candidate_location_str(snapshot)
        if loc:
            _add_sep()
            r = p.add_run(loc)
            r.font.name = self.font.docx_family
            r.font.size = Pt(self.spacing.body_font_size - 1.0)
            r.font.color.rgb = self.muted_rgb

        if basics.url:
            _add_sep()
            clean_url = basics.url.replace("https://", "").replace("http://", "").rstrip("/")
            add_hyperlink(
                p,
                basics.url,
                clean_url,
                self.palette.accent_hex,
                underline=False,
                font_name=self.font.docx_family,
                font_size_pt=self.spacing.body_font_size - 1.0,
            )

        for prof in basics.profiles:
            if prof.url:
                _add_sep()
                label = prof.network or prof.username or "Profile"
                add_hyperlink(
                    p,
                    prof.url,
                    label,
                    self.palette.accent_hex,
                    underline=False,
                    font_name=self.font.docx_family,
                    font_size_pt=self.spacing.body_font_size - 1.0,
                )

        return p

    def add_section_heading(self, title: str, parent: Optional[Any] = None) -> Any:
        container = parent if parent is not None else self.doc
        p = container.add_paragraph()
        p.paragraph_format.space_before = Pt(self.spacing.section_gap)
        p.paragraph_format.space_after = Pt(self.spacing.item_gap)
        p.paragraph_format.keep_with_next = True

        run = p.add_run(title.upper())
        run.bold = True
        run.font.name = self.font.docx_family
        run.font.size = Pt(self.spacing.heading2_size)

        if self.template_id == TEMPLATE_ATS_MINIMAL:
            run.font.color.rgb = RGBColor(0, 0, 0)
            add_paragraph_bottom_border(p, "000000", size_eighth_pts="4")
        elif self.template_id == TEMPLATE_CLASSIC_EXECUTIVE:
            run.font.color.rgb = self.primary_rgb
            add_paragraph_bottom_border(p, self.palette.border_hex, size_eighth_pts="6")
        elif self.template_id == TEMPLATE_ACADEMIC_RESEARCH:
            run.font.color.rgb = self.primary_rgb
            add_paragraph_bottom_border(p, self.palette.primary_hex, size_eighth_pts="8")
        else:
            run.font.color.rgb = self.primary_rgb
            add_paragraph_bottom_border(p, self.palette.accent_hex, size_eighth_pts="12")

        return p

    def add_entry_header(
        self,
        left_bold_title: str,
        left_subtitle: Optional[str],
        right_meta: str,
        container: Optional[Any] = None,
        col_widths: Optional[tuple] = None,
    ) -> Any:
        parent = container if container is not None else self.doc
        table = parent.add_table(rows=1, cols=2)
        make_borderless_table(table)

        if col_widths:
            table.columns[0].width = col_widths[0]
            table.columns[1].width = col_widths[1]

        c0 = table.cell(0, 0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(self.spacing.item_gap / 2)
        p0.paragraph_format.space_after = Pt(1)

        r_bold = p0.add_run(left_bold_title)
        r_bold.bold = True
        r_bold.font.name = self.font.docx_family
        r_bold.font.size = Pt(self.spacing.heading3_size)
        r_bold.font.color.rgb = self.primary_rgb

        if left_subtitle:
            r_sub = p0.add_run(f" — {left_subtitle}")
            if self.template_id in (TEMPLATE_CLASSIC_EXECUTIVE, TEMPLATE_ACADEMIC_RESEARCH):
                r_sub.italic = True
            r_sub.font.name = self.font.docx_family
            r_sub.font.size = Pt(self.spacing.body_font_size)
            r_sub.font.color.rgb = self.text_rgb

        c1 = table.cell(0, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(self.spacing.item_gap / 2)
        p1.paragraph_format.space_after = Pt(1)

        if right_meta:
            r_meta = p1.add_run(right_meta)
            r_meta.font.name = self.font.docx_family
            r_meta.font.size = Pt(self.spacing.body_font_size - 0.8)
            r_meta.font.color.rgb = self.muted_rgb

        return table

    def add_body_paragraph(self, text: str, container: Optional[Any] = None) -> Any:
        parent = container if container is not None else self.doc
        p = parent.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(self.spacing.item_gap / 2)
        run = p.add_run(text)
        run.font.name = self.font.docx_family
        run.font.size = Pt(self.spacing.body_font_size)
        run.font.color.rgb = self.text_rgb
        return p

    def add_bullet_item(self, text: str, container: Optional[Any] = None) -> Any:
        parent = container if container is not None else self.doc
        p = parent.add_paragraph(style="List Bullet")
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.font.name = self.font.docx_family
        run.font.size = Pt(self.spacing.body_font_size - 0.2)
        run.font.color.rgb = self.text_rgb
        return p

    def add_tech_stack(self, label: str, items_str: str, container: Optional[Any] = None) -> Any:
        parent = container if container is not None else self.doc
        p = parent.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(self.spacing.item_gap / 2)

        r_lbl = p.add_run(f"{label}: ")
        r_lbl.bold = True
        r_lbl.font.name = self.font.docx_family
        r_lbl.font.size = Pt(self.spacing.body_font_size - 0.8)
        r_lbl.font.color.rgb = self.accent_rgb

        r_val = p.add_run(items_str)
        r_val.font.name = self.font.docx_family
        r_val.font.size = Pt(self.spacing.body_font_size - 0.8)
        r_val.font.color.rgb = self.text_rgb
        return p


def _build_work_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
    col_widths: Optional[tuple] = None,
) -> None:
    work_items = filter_visible_items(snapshot.work, item_visibility)
    for item in work_items:
        pos = getattr(item, "position", None) or "Position"
        comp = getattr(item, "name", None) or getattr(item, "company", None) or ""
        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        is_curr = bool(getattr(item, "is_current", False) or getattr(item, "isCurrent", False))
        date_str = format_date_range(start_d, end_d, is_curr)
        loc = getattr(item, "location", "") or ""
        meta_str = " | ".join(p for p in [date_str, loc] if p)

        fmt.add_entry_header(pos, comp, meta_str, container=container, col_widths=col_widths)

        if item.summary:
            fmt.add_body_paragraph(item.summary, container=container)

        bullets = item.highlights or item.responsibilities or []
        for bullet in bullets:
            if bullet and bullet.strip():
                fmt.add_bullet_item(bullet.strip(), container=container)

        techs = item.technologies or []
        if techs:
            fmt.add_tech_stack("Tech Stack", ", ".join(techs), container=container)


def _build_skills_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
) -> None:
    skills = filter_visible_items(snapshot.skills, item_visibility)
    if not skills:
        return

    has_categories = any(s.keywords or s.category for s in skills)
    if has_categories:
        for skill in skills:
            cat = skill.name or skill.category or "Skills"
            kws = skill.keywords or []
            kw_str = ", ".join(kws) if kws else (skill.level or "")
            fmt.add_tech_stack(cat, kw_str, container=container)
    else:
        names = [s.name for s in skills if s.name]
        if names:
            fmt.add_body_paragraph("  •  ".join(names), container=container)


def _build_projects_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
    col_widths: Optional[tuple] = None,
) -> None:
    projects = filter_visible_items(snapshot.projects, item_visibility)
    for item in projects:
        name = item.name or "Project"
        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        date_str = format_date_range(start_d, end_d)
        fmt.add_entry_header(name, None, date_str, container=container, col_widths=col_widths)

        if item.description:
            fmt.add_body_paragraph(item.description, container=container)

        for bullet in (item.highlights or []):
            if bullet and bullet.strip():
                fmt.add_bullet_item(bullet.strip(), container=container)

        techs = item.keywords or item.technologies or []
        if techs:
            fmt.add_tech_stack("Technologies", ", ".join(techs), container=container)


def _build_education_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
    col_widths: Optional[tuple] = None,
) -> None:
    education = filter_visible_items(snapshot.education, item_visibility)
    for item in education:
        deg = getattr(item, "degree", None) or getattr(item, "studyType", None) or ""
        area = getattr(item, "area", None) or getattr(item, "field_of_study", None) or ""
        inst = getattr(item, "institution", "") or ""
        deg_area = f"{deg} in {area}" if (deg and area) else (deg or area or "Degree")
        start_d = getattr(item, "start_date", None) or getattr(item, "startDate", None)
        end_d = getattr(item, "end_date", None) or getattr(item, "endDate", None)
        date_str = format_date_range(start_d, end_d)

        fmt.add_entry_header(deg_area, inst, date_str, container=container, col_widths=col_widths)

        score_val = getattr(item, "score", None) or getattr(item, "grade", None)
        if score_val:
            fmt.add_body_paragraph(f"GPA / Score: {score_val}", container=container)

        bullets = getattr(item, "courses", None) or getattr(item, "achievements", None) or getattr(item, "highlights", None) or []
        for bullet in bullets:
            if bullet and bullet.strip():
                fmt.add_bullet_item(bullet.strip(), container=container)


def _build_certificates_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
    col_widths: Optional[tuple] = None,
) -> None:
    certs = filter_visible_items(snapshot.certificates, item_visibility)
    for item in certs:
        name = item.name or "Certificate"
        issuer = item.issuer or ""
        date_val = getattr(item, "date", None) or getattr(item, "issue_date", None)
        date_str = format_date_str(date_val)
        fmt.add_entry_header(name, issuer, date_str, container=container, col_widths=col_widths)


def _build_awards_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
    col_widths: Optional[tuple] = None,
) -> None:
    awards = filter_visible_items(snapshot.awards, item_visibility)
    for item in awards:
        title = item.title or "Award"
        awarder = item.awarder or ""
        date_str = format_date_str(item.date)
        fmt.add_entry_header(title, awarder, date_str, container=container, col_widths=col_widths)
        if item.summary:
            fmt.add_body_paragraph(item.summary, container=container)


def _build_languages_docx(
    snapshot: CVContentSnapshot,
    fmt: DOCXFormatter,
    item_visibility: Optional[Dict[str, bool]],
    container: Optional[Any] = None,
) -> None:
    langs = filter_visible_items(snapshot.languages, item_visibility)
    if not langs:
        return
    strs = []
    for item in langs:
        l_name = item.language or ""
        fluency = item.fluency or ""
        if l_name and fluency:
            strs.append(f"{l_name} ({fluency})")
        elif l_name:
            strs.append(l_name)
    if strs:
        fmt.add_body_paragraph("  •  ".join(strs), container=container)


def generate_cv_docx(
    snapshot: CVContentSnapshot,
    overrides: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Generate production-ready, editable Microsoft Word (.docx) document from CV content snapshot.
    
    Supports:
    - All 6 templates (modern-professional, classic-executive, ats-minimal,
      technical-developer, contemporary-two-column, academic-research)
    - Page sizes: A4 and US Letter
    - Spacing densities: compact, normal, relaxed
    - Native Word headings, paragraphs, bullet lists, borderless alignment tables
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

    doc = docx.Document()

    # Configure Section Page Size and Margins
    section = doc.sections[0]
    section.page_width = Inches(page_size_cfg.width_in)
    section.page_height = Inches(page_size_cfg.height_in)
    section.top_margin = Inches(spacing.margin_in)
    section.bottom_margin = Inches(spacing.margin_in)
    section.left_margin = Inches(spacing.margin_in)
    section.right_margin = Inches(spacing.margin_in)

    fmt = DOCXFormatter(doc, palette, font, spacing, template_id)
    printable_w_in = page_size_cfg.width_in - (2 * spacing.margin_in)

    # 1. Candidate Header
    candidate_name = get_candidate_name(snapshot)
    headline = get_candidate_headline(snapshot)
    fmt.add_title(candidate_name)
    if headline:
        fmt.add_headline(headline)

    fmt.add_contact_paragraph(snapshot)

    basics = snapshot.basics
    has_summary = bool(basics and (basics.summary or basics.base_summary))

    # --------------------------------------------------------------------------
    # CONTEMPORARY TWO-COLUMN TEMPLATE BUILDER (Using 2-Column Borderless Table)
    # --------------------------------------------------------------------------
    if template_id == TEMPLATE_CONTEMPORARY_TWO_COLUMN:
        col_table = doc.add_table(rows=1, cols=2)
        make_borderless_table(col_table)

        col0_w = Inches(printable_w_in * 0.33)
        col1_w = Inches(printable_w_in * 0.67)
        col_table.columns[0].width = col0_w
        col_table.columns[1].width = col1_w

        cell_sidebar = col_table.cell(0, 0)
        cell_main = col_table.cell(0, 1)

        # Apply subtle shading to sidebar cell
        set_cell_background(cell_sidebar, palette.accent_muted_hex)

        # SIDEBAR COLUMN: Skills, Education, Certifications, Languages
        if is_section_visible("skills", section_visibility, len(snapshot.skills) > 0):
            fmt.add_section_heading("Skills", parent=cell_sidebar)
            _build_skills_docx(snapshot, fmt, item_visibility, container=cell_sidebar)

        if is_section_visible("education", section_visibility, len(snapshot.education) > 0):
            fmt.add_section_heading("Education", parent=cell_sidebar)
            _build_education_docx(
                snapshot, fmt, item_visibility, container=cell_sidebar,
                col_widths=(Inches(col0_w.inches * 0.65), Inches(col0_w.inches * 0.35))
            )

        if is_section_visible("certificates", section_visibility, len(snapshot.certificates) > 0):
            fmt.add_section_heading("Certifications", parent=cell_sidebar)
            _build_certificates_docx(
                snapshot, fmt, item_visibility, container=cell_sidebar,
                col_widths=(Inches(col0_w.inches * 0.65), Inches(col0_w.inches * 0.35))
            )

        if is_section_visible("languages", section_visibility, len(snapshot.languages) > 0):
            fmt.add_section_heading("Languages", parent=cell_sidebar)
            _build_languages_docx(snapshot, fmt, item_visibility, container=cell_sidebar)

        # MAIN COLUMN: Summary, Work, Projects, Awards
        if is_section_visible("basics", section_visibility, has_summary):
            summary_text = (basics.summary or basics.base_summary or "").strip()
            fmt.add_section_heading("Profile Summary", parent=cell_main)
            fmt.add_body_paragraph(summary_text, container=cell_main)

        main_col_widths = (Inches(col1_w.inches * 0.68), Inches(col1_w.inches * 0.32))

        if is_section_visible("work", section_visibility, len(snapshot.work) > 0):
            fmt.add_section_heading("Experience", parent=cell_main)
            _build_work_docx(snapshot, fmt, item_visibility, container=cell_main, col_widths=main_col_widths)

        if is_section_visible("projects", section_visibility, len(snapshot.projects) > 0):
            fmt.add_section_heading("Key Projects", parent=cell_main)
            _build_projects_docx(snapshot, fmt, item_visibility, container=cell_main, col_widths=main_col_widths)

        if is_section_visible("awards", section_visibility, len(snapshot.awards) > 0):
            fmt.add_section_heading("Achievements", parent=cell_main)
            _build_awards_docx(snapshot, fmt, item_visibility, container=cell_main, col_widths=main_col_widths)

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    # --------------------------------------------------------------------------
    # SINGLE-COLUMN TEMPLATES BUILDER (Modern, Classic, ATS, Technical, Academic)
    # --------------------------------------------------------------------------
    entry_col_widths = (Inches(printable_w_in * 0.68), Inches(printable_w_in * 0.32))

    for sec_key in section_order:
        if sec_key == "basics":
            if is_section_visible("basics", section_visibility, has_summary):
                summary_text = (basics.summary or basics.base_summary or "").strip()
                title = "Research Profile" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Professional Summary"
                fmt.add_section_heading(title)
                fmt.add_body_paragraph(summary_text)

        elif sec_key == "work":
            if is_section_visible("work", section_visibility, len(snapshot.work) > 0):
                title = "Research & Academic Experience" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Professional Experience"
                fmt.add_section_heading(title)
                _build_work_docx(snapshot, fmt, item_visibility, col_widths=entry_col_widths)

        elif sec_key == "skills":
            if is_section_visible("skills", section_visibility, len(snapshot.skills) > 0):
                title = "Technical Skills & Competencies" if template_id == TEMPLATE_TECHNICAL_DEVELOPER else "Core Competencies & Skills"
                fmt.add_section_heading(title)
                _build_skills_docx(snapshot, fmt, item_visibility)

        elif sec_key == "projects":
            if is_section_visible("projects", section_visibility, len(snapshot.projects) > 0):
                title = "Publications & Selected Projects" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Key Projects & Initiatives"
                fmt.add_section_heading(title)
                _build_projects_docx(snapshot, fmt, item_visibility, col_widths=entry_col_widths)

        elif sec_key == "education":
            if is_section_visible("education", section_visibility, len(snapshot.education) > 0):
                title = "Education & Academic Credentials" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Education"
                fmt.add_section_heading(title)
                _build_education_docx(snapshot, fmt, item_visibility, col_widths=entry_col_widths)

        elif sec_key == "certificates":
            if is_section_visible("certificates", section_visibility, len(snapshot.certificates) > 0):
                title = "Certifications & Professional Credentials"
                fmt.add_section_heading(title)
                _build_certificates_docx(snapshot, fmt, item_visibility, col_widths=entry_col_widths)

        elif sec_key == "awards":
            if is_section_visible("awards", section_visibility, len(snapshot.awards) > 0):
                title = "Honors, Grants & Fellowships" if template_id == TEMPLATE_ACADEMIC_RESEARCH else "Honors & Achievements"
                fmt.add_section_heading(title)
                _build_awards_docx(snapshot, fmt, item_visibility, col_widths=entry_col_widths)

        elif sec_key == "languages":
            if is_section_visible("languages", section_visibility, len(snapshot.languages) > 0):
                title = "Languages"
                fmt.add_section_heading(title)
                _build_languages_docx(snapshot, fmt, item_visibility)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
