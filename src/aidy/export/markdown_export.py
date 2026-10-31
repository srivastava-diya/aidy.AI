"""Markdown export formatter for research reports."""

import os
from aidy.crew.schemas import ResearchReport


def format_report_as_markdown(report: ResearchReport) -> str:
    """Formats a ResearchReport instance into clean, standardized academic Markdown."""
    lines = []

    lines.append(f"# {report.topic}")
    lines.append(f"**Research Date:** {report.research_date}  ")
    lines.append(f"**Report ID:** `{report.report_id}` | **Editorial Status:** `{report.review_status.upper()}`  ")
    lines.append(f"**Execution Mode:** `{report.execution_mode}`  ")
    lines.append(f"**Telemetry:** Latency: {report.execution_duration_s}s | Tokens: {report.tokens_consumed:,} ({report.token_accounting_mode}) | Quality: {report.quality_score:.3f}  ")

    if report.is_offline_demo:
        lines.append(
            "\n> [!IMPORTANT]\n"
            "> **OFFLINE DEMO BENCHMARK MODE ACTIVE:**\n"
            "> This report was generated using verified peer-reviewed academic literature from the local benchmark corpus (arXiv, Nature, WHO, FDA, IPCC, IEA). "
            "> External API search keys were not detected. All citations refer to real publications with verifiable URLs, exact dates, and authentic abstracts.\n"
        )
    else:
        lines.append(
            "\n> [!NOTE]\n"
            "> **LIVE RESEARCH MODE ACTIVE:**\n"
            "> This report was generated via live open-web search and real-time webpage content retrieval.\n"
        )

    lines.append("---")
    lines.append("## 1. Executive Summary")
    lines.append(report.executive_summary)
    lines.append("")

    if report.rejected_questions_warnings:
        lines.append("> [!WARNING]")
        lines.append("> **Research Scope Alignment Notice:**")
        for w in report.rejected_questions_warnings:
            lines.append(f"> - {w}")
        lines.append("")

    lines.append("## 2. Research Objectives and Inquiries")
    for obj in report.research_objectives:
        lines.append(f"- {obj}")
    lines.append("")

    lines.append("## 3. Methodology and Source-Selection Approach")
    lines.append(report.methodology)
    lines.append("")

    lines.append("## 4. Key Findings (Substantiated by Verified Evidence)")
    for finding in report.key_findings:
        lines.append(f"- {finding}")
    lines.append("")

    lines.append("## 5. Evidence-Based Analysis")
    lines.append(report.evidence_based_analysis)
    lines.append("")

    lines.append("## 6. Conflicting Evidence, Quarantined Claims & Uncertainty")
    lines.append(report.conflicting_evidence_and_uncertainty)
    lines.append("")

    lines.append("## 7. Research Gaps and Limitations")
    for gap in report.research_gaps_and_limitations:
        lines.append(f"- {gap}")
    lines.append("")

    lines.append("## 8. Conclusion")
    lines.append(report.conclusion)
    lines.append("")

    lines.append("## 9. References, Evidence Excerpts & Verification Audit")
    for ref in report.references:
        badges = ref.get("verification_badges", [])
        badge_str = " ".join([f"[{b}]" for b in badges]) if badges else ("[CLAIM SUPPORTED]" if ref.get("is_verified") else "[UNVERIFIED]")
        lines.append(f"[{ref['citation_id']}] **{ref['title']}**  ")
        lines.append(f"    - *Verification Audit:* `{badge_str}`  ")
        lines.append(f"    - *Domain Authority:* `{ref['domain']}` | *Published Date:* {ref.get('published_date', 'N/A')}  ")
        lines.append(f"    - *Retrieval Provenance:* `{ref.get('retrieval_mode', 'N/A')}`  ")
        lines.append(f"    - *Canonical URL:* {ref['url']}  ")
        if ref.get("supporting_evidence_excerpt"):
            lines.append(f"    - *Supporting Evidence Excerpt:* \"{ref['supporting_evidence_excerpt']}\"  ")
        if ref.get("verification_rationale"):
            lines.append(f"    - *Audit Rationale:* {ref['verification_rationale']}  ")
        lines.append("")

    lines.append("---")
    lines.append(
        f"*aidy.AI Multi-Agent Research Platform | Workflow Started: {report.started_at} | "
        f"Completed: {report.completed_at} | Total Latency: {report.execution_duration_s}s*"
    )

    return "\n".join(lines)


def save_markdown_report(report: ResearchReport, output_dir: str = "data/reports") -> str:
    """Saves the markdown report to disk and returns absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{report.report_id}.md"
    target_path = os.path.join(output_dir, filename)
    content = format_report_as_markdown(report)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path
