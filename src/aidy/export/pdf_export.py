"""PDF report exporter using ReportLab styled with aidy.AI accents."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from aidy.crew.schemas import ResearchReport


def export_report_to_pdf(report: ResearchReport, output_path: str) -> str:
    """Generates an editorial PDF version of the research report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#17140F")
    ACCENT_PRIMARY = colors.HexColor("#17140F")
    ACCENT_SECONDARY = colors.HexColor("#2C6144")
    TEXT_DARK = colors.HexColor("#17140F")
    BG_CARD = colors.HexColor("#FBF9F4")
    BORDER = colors.HexColor("#D7D0C1")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "ReportMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#556358"),
        spaceAfter=10,
    )

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=ACCENT_SECONDARY,
        spaceBefore=10,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        leftIndent=15,
        spaceAfter=4,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(report.topic, title_style))
    story.append(Paragraph(
        f"<b>aidy.AI Research Intelligence Report</b> | Date: {report.research_date} | "
        f"Report ID: <code>{report.report_id}</code> | Status: <b>{report.review_status.upper()}</b><br/>"
        f"<b>Execution Mode:</b> {report.execution_mode} | "
        f"<b>Latency:</b> {report.execution_duration_s}s | "
        f"<b>Tokens:</b> {report.tokens_consumed:,} ({report.token_accounting_mode})",
        meta_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_PRIMARY, spaceAfter=10))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(report.executive_summary, body_style))

    if report.rejected_questions_warnings:
        warn_style = ParagraphStyle(
            "WarnStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#A84236"),
            spaceBefore=4,
            spaceAfter=6,
        )
        for w in report.rejected_questions_warnings:
            story.append(Paragraph(f"<b>Notice:</b> {w}", warn_style))

    # 2. Objectives
    story.append(Paragraph("2. Research Objectives and Inquiries", h2_style))
    for obj in report.research_objectives:
        story.append(Paragraph(f"• {obj}", bullet_style))

    # 3. Methodology
    story.append(Paragraph("3. Methodology and Source-Selection Approach", h2_style))
    story.append(Paragraph(report.methodology, body_style))

    # 4. Key Findings
    story.append(Paragraph("4. Key Findings (Substantiated by Verified Evidence)", h2_style))
    for kf in report.key_findings:
        story.append(Paragraph(f"• {kf}", bullet_style))

    # 5. Analysis
    story.append(Paragraph("5. Evidence-Based Analysis", h2_style))
    story.append(Paragraph(report.evidence_based_analysis, body_style))

    # 6. Conflicting Evidence
    story.append(Paragraph("6. Conflicting Evidence, Quarantined Claims & Uncertainty", h2_style))
    story.append(Paragraph(report.conflicting_evidence_and_uncertainty, body_style))

    # 7. Gaps & Limitations
    story.append(Paragraph("7. Research Gaps and Limitations", h2_style))
    for gap in report.research_gaps_and_limitations:
        story.append(Paragraph(f"• {gap}", bullet_style))

    # 8. Conclusion
    story.append(Paragraph("8. Conclusion", h2_style))
    story.append(Paragraph(report.conclusion, body_style))

    # 9. References
    story.append(Paragraph("9. References, Evidence Excerpts & Verification Audit", h2_style))
    ref_table_data = [["ID", "Title & Domain", "Status", "Retrieval Mode", "URL & Excerpt"]]
    for ref in report.references:
        v_status = "Verified" if ref.get("is_verified") else "Unverified"
        excerpt = ref.get("supporting_evidence_excerpt") or ""
        short_excerpt = f"<br/><font size=6.5 color='#556358'><i>\"{excerpt[:75]}...\"</i></font>" if excerpt else ""

        ref_table_data.append([
            f"[{ref['citation_id']}]",
            Paragraph(f"<b>{ref['title']}</b><br/><font size=7 color='#556358'>{ref['domain']}</font>", body_style),
            v_status,
            ref.get("retrieval_mode", "N/A")[:16],
            Paragraph(f"<font size=7 color='#2B5B84'>{ref['url'][:45]}...</font>{short_excerpt}", body_style),
        ])

    ref_table = Table(ref_table_data, colWidths=[0.45 * inch, 2.3 * inch, 0.75 * inch, 1.2 * inch, 2.3 * inch])
    ref_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_CARD),
        ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(ref_table)

    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER, spaceAfter=6))
    story.append(Paragraph(
        f"Generated by aidy.AI Multi-Agent Platform | Mode: {report.execution_mode} | "
        f"Latency: {report.execution_duration_s}s | Tokens: {report.tokens_consumed} ({report.token_accounting_mode})",
        meta_style,
    ))

    doc.build(story)
    return output_path
