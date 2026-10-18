"""Production-ready PDF and DOCX export services for Cover Letters."""

import datetime
import html
import io
import re
from typing import Any, List, Optional

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.models.cover_letter import CoverLetter


def get_sanitized_cover_letter_filename(name: str, ext: str) -> str:
    """Create a safe, clean file attachment name e.g. 'Jane_Doe_Cover_Letter.pdf'."""
    clean_name = re.sub(r"[^\w\s-]", "", name).strip()
    clean_name = re.sub(r"[\s_-]+", "_", clean_name)
    if not clean_name:
        clean_name = "Cover_Letter"
    clean_ext = ext.lstrip(".").lower()
    return f"{clean_name}.{clean_ext}"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for adding clean page numbers to multi-page cover letters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[dict] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if num_pages > 1:
                self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, page_text)
        self.restoreState()


def escape_xml(text: Optional[str]) -> str:
    """Escape text safely for ReportLab flowable XML parsing."""
    if not text:
        return ""
    return html.escape(str(text), quote=False)


def generate_cover_letter_pdf(cover_letter: CoverLetter) -> io.BytesIO:
    """
    Generate an elegant, professional PDF for a cover letter using ReportLab.
    Supports clean letterhead, recipient block, salutation, body paragraphs, and sign-off.
    """
    buffer = io.BytesIO()

    # 0.75-inch margins (54pt)
    margin = 54
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_name_style = ParagraphStyle(
        "CLHeaderName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
    )

    header_contact_style = ParagraphStyle(
        "CLHeaderContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
    )

    date_style = ParagraphStyle(
        "CLDate",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    recipient_style = ParagraphStyle(
        "CLRecipient",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )

    recipient_bold_style = ParagraphStyle(
        "CLRecipientBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
    )

    salutation_style = ParagraphStyle(
        "CLSalutation",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
    )

    body_style = ParagraphStyle(
        "CLBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15.5,
        textColor=colors.HexColor("#1e293b"),
    )

    signoff_style = ParagraphStyle(
        "CLSignOff",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
    )

    signoff_name_style = ParagraphStyle(
        "CLSignOffName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # 1. Sender Header / Letterhead
    story.append(Paragraph(escape_xml(cover_letter.sender_name), header_name_style))
    if cover_letter.sender_contact:
        story.append(Spacer(1, 3))
        story.append(Paragraph(escape_xml(cover_letter.sender_contact), header_contact_style))

    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#cbd5e1"),
            spaceBefore=2,
            spaceAfter=12,
        )
    )

    # 2. Date
    created_date = cover_letter.created_at or datetime.datetime.now()
    date_str = created_date.strftime("%B %d, %Y")
    story.append(Paragraph(escape_xml(date_str), date_style))
    story.append(Spacer(1, 12))

    # 3. Recipient Information Block
    has_recipient_info = False
    if cover_letter.recipient_name:
        story.append(Paragraph(escape_xml(cover_letter.recipient_name), recipient_bold_style))
        has_recipient_info = True
    if cover_letter.recipient_title:
        story.append(Paragraph(escape_xml(cover_letter.recipient_title), recipient_style))
        has_recipient_info = True
    if cover_letter.recipient_company:
        story.append(Paragraph(escape_xml(cover_letter.recipient_company), recipient_style))
        has_recipient_info = True
    if cover_letter.recipient_address:
        story.append(Paragraph(escape_xml(cover_letter.recipient_address), recipient_style))
        has_recipient_info = True

    if has_recipient_info:
        story.append(Spacer(1, 14))

    # 4. Salutation
    salutation_text = cover_letter.salutation or "Dear Hiring Manager,"
    story.append(Paragraph(escape_xml(salutation_text), salutation_style))
    story.append(Spacer(1, 10))

    # 5. Opening Paragraph
    if cover_letter.opening:
        story.append(Paragraph(escape_xml(cover_letter.opening), body_style))
        story.append(Spacer(1, 10))

    # 6. Body Paragraphs
    for paragraph in (cover_letter.body_paragraphs or []):
        if paragraph and paragraph.strip():
            story.append(Paragraph(escape_xml(paragraph.strip()), body_style))
            story.append(Spacer(1, 10))

    # 7. Closing Paragraph
    if cover_letter.closing:
        story.append(Paragraph(escape_xml(cover_letter.closing), body_style))
        story.append(Spacer(1, 14))

    # 8. Sign-off and Signature
    sign_off_text = cover_letter.sign_off or "Sincerely,"
    story.append(Paragraph(escape_xml(sign_off_text), signoff_style))
    story.append(Spacer(1, 24))  # Space for signature
    story.append(Paragraph(escape_xml(cover_letter.sender_name), signoff_name_style))

    # Build PDF with page number canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


def generate_cover_letter_docx(cover_letter: CoverLetter) -> io.BytesIO:
    """
    Generate a clean, professional DOCX document for a cover letter using python-docx.
    Configured with standard 1-inch margins, modern typography, and structured paragraphs.
    """
    doc = docx.Document()

    # 1. Page Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # 2. Base Style Customization
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)  # Slate dark

    # 3. Sender Header
    p_sender = doc.add_paragraph()
    p_sender.paragraph_format.space_after = Pt(2)
    run_name = p_sender.add_run(cover_letter.sender_name)
    run_name.bold = True
    run_name.font.size = Pt(16)
    run_name.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    if cover_letter.sender_contact:
        p_contact = doc.add_paragraph()
        p_contact.paragraph_format.space_after = Pt(14)
        run_contact = p_contact.add_run(cover_letter.sender_contact)
        run_contact.font.size = Pt(9.5)
        run_contact.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # 4. Date
    created_date = cover_letter.created_at or datetime.datetime.now()
    date_str = created_date.strftime("%B %d, %Y")
    p_date = doc.add_paragraph()
    p_date.paragraph_format.space_after = Pt(14)
    run_date = p_date.add_run(date_str)
    run_date.font.size = Pt(10.5)

    # 5. Recipient Block
    if cover_letter.recipient_name or cover_letter.recipient_company:
        p_rec = doc.add_paragraph()
        p_rec.paragraph_format.space_after = Pt(14)
        p_rec.paragraph_format.line_spacing = 1.15

        if cover_letter.recipient_name:
            r1 = p_rec.add_run(cover_letter.recipient_name + "\n")
            r1.bold = True
        if cover_letter.recipient_title:
            p_rec.add_run(cover_letter.recipient_title + "\n")
        if cover_letter.recipient_company:
            p_rec.add_run(cover_letter.recipient_company + "\n")
        if cover_letter.recipient_address:
            p_rec.add_run(cover_letter.recipient_address)

    # 6. Salutation
    p_salut = doc.add_paragraph()
    p_salut.paragraph_format.space_after = Pt(10)
    run_salut = p_salut.add_run(cover_letter.salutation or "Dear Hiring Manager,")
    run_salut.bold = True

    # 7. Opening
    if cover_letter.opening:
        p_open = doc.add_paragraph()
        p_open.paragraph_format.space_after = Pt(10)
        p_open.paragraph_format.line_spacing = 1.15
        p_open.add_run(cover_letter.opening)

    # 8. Body Paragraphs
    for para in (cover_letter.body_paragraphs or []):
        if para and para.strip():
            p_body = doc.add_paragraph()
            p_body.paragraph_format.space_after = Pt(10)
            p_body.paragraph_format.line_spacing = 1.15
            p_body.add_run(para.strip())

    # 9. Closing
    if cover_letter.closing:
        p_close = doc.add_paragraph()
        p_close.paragraph_format.space_after = Pt(14)
        p_close.paragraph_format.line_spacing = 1.15
        p_close.add_run(cover_letter.closing)

    # 10. Sign-off and Signature
    p_signoff = doc.add_paragraph()
    p_signoff.paragraph_format.space_after = Pt(28)  # Signature gap
    p_signoff.add_run(cover_letter.sign_off or "Sincerely,")

    p_signature = doc.add_paragraph()
    p_signature.paragraph_format.space_after = Pt(0)
    run_sig = p_signature.add_run(cover_letter.sender_name)
    run_sig.bold = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
