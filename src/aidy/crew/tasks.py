"""Task definitions for the aidy.AI multi-agent pipeline."""

from typing import List, Optional
from crewai import Task, Agent


def create_research_task(
    agent: Agent,
    topic: str,
    subquestions: Optional[List[str]] = None,
    max_sources: int = 5,
) -> Task:
    subq_text = "\n".join([f"- {q}" for q in (subquestions or [])]) or "- Investigate core applications, benefits, risks, and empirical evidence."
    return Task(
        description=(
            f"Conduct rigorous primary research on: '{topic}'.\n"
            f"Focus on the following sub-inquiries:\n{subq_text}\n\n"
            f"Search for authoritative publications, retrieve full content snippets, and gather up to {max_sources} unique sources.\n"
            f"Output must list every discovered source with Title, Normalized URL, Publication Date, and verbatim Evidence Snippets indexed by [1], [2], etc."
        ),
        expected_output="Structured research findings containing numbered sources ([1], [2]...) and extracted factual excerpts.",
        agent=agent,
    )


def create_fact_check_task(
    agent: Agent,
    research_task: Task,
) -> Task:
    return Task(
        description=(
            "Audit all factual statements in the research findings against the provided source texts.\n"
            "For each key factual claim:\n"
            "1. Identify the claim statement.\n"
            "2. Cross-reference against the text of the cited source(s).\n"
            "3. Classify status strictly as 'Verified', 'Contradicted', or 'Unverified'.\n"
            "4. Provide the rationale and citation index numbers proving the assessment."
        ),
        expected_output="A structured claim verification table with claim ID, status, supporting citation numbers, and audit rationale.",
        agent=agent,
        context=[research_task],
    )


def create_analysis_task(
    agent: Agent,
    research_task: Task,
    fact_check_task: Task,
) -> Task:
    return Task(
        description=(
            "Synthesize the verified evidence and audited claims into an analytical framework.\n"
            "Identify:\n"
            "- Core recurring patterns and technological/scientific convergences.\n"
            "- Disagreements, institutional tensions, or contradictory findings.\n"
            "- Critical uncertainties and potential failure modes.\n"
            "- Key research gaps and unanswered scientific or policy questions.\n"
            "Keep interpretation rigorously grounded in the verified data."
        ),
        expected_output="Deep analytical synthesis detailing patterns, tensions, uncertainties, and research gaps.",
        agent=agent,
        context=[research_task, fact_check_task],
    )


def create_writing_task(
    agent: Agent,
    topic: str,
    research_task: Task,
    fact_check_task: Task,
    analysis_task: Task,
) -> Task:
    return Task(
        description=(
            f"Write the complete, publication-grade research report on '{topic}'.\n"
            "Structure the report strictly with the following 10 sections:\n"
            "1. Title and Research Date\n"
            "2. Executive Summary\n"
            "3. Research Objectives and Questions\n"
            "4. Methodology and Source-Selection Approach\n"
            "5. Key Findings (with inline citation tags like [1], [2])\n"
            "6. Evidence-Based Analysis\n"
            "7. Conflicting Evidence and Uncertainty\n"
            "8. Research Gaps and Limitations\n"
            "9. Conclusion\n"
            "10. References and Source Links\n\n"
            "Embed verified citation references throughout. Avoid speculation and promotional language."
        ),
        expected_output="Complete 10-section publication-ready Markdown research report with traceable citations.",
        agent=agent,
        context=[research_task, fact_check_task, analysis_task],
    )
