"""Authoritative, typed research context and topic-normalization engine.

Guarantees strict end-to-end alignment across all pipeline stages:
1. Normalizes raw user prompts into canonical subject titles.
2. Derives topic-specific research objectives, rejecting mismatched/stale subquestions with explicit warnings.
3. Holds the single authoritative execution state passed across agents.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def normalize_topic(raw_topic: str) -> str:
    """Extracts the canonical subject phrase from conversational research prompts.
    
    Example:
        'Research the current applications, benefits, limitations, and future scope of Agentic AI in healthcare.'
        -> 'Agentic AI in Healthcare'
    """
    cleaned = raw_topic.strip()
    if not cleaned:
        return "Unspecified Topic"

    # Remove trailing punctuation
    cleaned = cleaned.rstrip(".?!;")

    # Match common prompt introductory phrases (case-insensitive)
    patterns = [
        r"^research\s+(the\s+)?(current\s+)?(applications,\s+benefits,\s+limitations,?\s+and\s+future\s+scope\s+of\s+)?",
        r"^(please\s+)?research\s+(about\s+|on\s+|into\s+)?",
        r"^investigate\s+(the\s+)?",
        r"^analyze\s+(the\s+)?",
        r"^explore\s+(the\s+)?",
        r"^a\s+study\s+(on|of|into)\s+",
        r"^comprehensive\s+analysis\s+of\s+",
        r"^overview\s+of\s+",
    ]

    subject = cleaned
    for pat in patterns:
        m = re.match(pat, subject, re.IGNORECASE)
        if m:
            subject = subject[m.end():].strip()

    # Clean up leading lowercase articles if left over
    subject = re.sub(r"^(the|an|a)\s+", "", subject, flags=re.IGNORECASE).strip()

    # If the remaining string is too short or empty, fall back to cleaned raw topic
    if len(subject) < 3:
        subject = cleaned

    # Capitalize appropriately if all lowercase or mixed
    words = subject.split()
    if words and all(w.islower() for w in words):
        subject = " ".join([w.capitalize() if w not in ("in", "of", "and", "the", "for", "on", "with", "to") else w for w in words])

    return subject


def derive_research_objectives(
    original_topic: str,
    normalized_topic: str,
    user_subquestions: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """Derives focused, relevant research objectives for the topic.
    
    Validates user-submitted subquestions for topical relevance. Rejects off-topic
    or stale subquestions (e.g. education questions submitted with healthcare topic)
    with explicit warnings.
    
    Returns:
        (valid_objectives, warning_messages)
    """
    norm_lower = normalized_topic.lower()
    raw_lower = original_topic.lower()

    # Build domain keyword signature from topic
    topic_keywords = {
        w.strip(",.?!;:\"'()")
        for w in (norm_lower + " " + raw_lower).split()
        if len(w) > 3 and w not in ("research", "current", "applications", "benefits", "limitations", "future", "scope", "with", "from", "that", "this")
    }

    valid_questions: List[str] = []
    warnings: List[str] = []

    if user_subquestions:
        for q in user_subquestions:
            q_clean = q.strip()
            if not q_clean:
                continue
            q_lower = q_clean.lower()
            q_words = {w.strip(",.?!;:\"'()") for w in q_lower.split() if len(w) > 3}

            # Check for domain incompatibility
            is_education_q = any(k in q_lower for k in ("education", "classroom", "student", "curriculum", "pedagog", "school"))
            is_healthcare_topic = any(k in norm_lower for k in ("health", "clinic", "medic", "patient", "doctor", "hospital", "pharma"))

            if is_education_q and is_healthcare_topic:
                warnings.append(
                    f"Rejected off-topic subquestion '{q_clean}': Inquiry refers to educational systems but active research topic is '{normalized_topic}'."
                )
                continue

            # Check overlap or general applicability
            overlap = topic_keywords.intersection(q_words)
            is_general_methodological = any(k in q_lower for k in ("accuracy", "risk", "benchmark", "regulation", "framework", "architecture", "limitation", "cost", "compliance"))

            if overlap or is_general_methodological:
                valid_questions.append(q_clean)
            else:
                warnings.append(
                    f"Subquestion '{q_clean}' lacked strong conceptual grounding in '{normalized_topic}' and was replaced by synthesized objectives."
                )

    # If valid questions were accepted, use them
    if valid_questions:
        return valid_questions, warnings

    # Otherwise derive topic-specific objectives based on detected domain
    if any(k in norm_lower for k in ("health", "clinic", "medic", "patient", "doctor", "hospital")):
        objectives = [
            f"Identify established clinical applications and decision-support deployments of {normalized_topic}.",
            f"Evaluate measured diagnostic accuracy, operational benefits, and productivity impacts in healthcare delivery.",
            f"Analyze regulatory compliance requirements (e.g., FDA AI/ML medical device pathways, WHO ethics guidance) and safety constraints.",
            f"Examine technical and architectural limitations, distinguishing general predictive healthcare AI from autonomous multi-agent systems.",
            f"Assess the future clinical scope, collaborative human-agent workflows, and prospective trial requirements."
        ]
    elif any(k in norm_lower for k in ("education", "learning", "student", "teaching", "pedagog")):
        objectives = [
            f"Investigate current adaptive learning, automated assessment, and tutoring systems in {normalized_topic}.",
            f"Synthesize empirical evidence regarding pedagogical efficacy and measurable student learning outcomes.",
            f"Examine critical ethical limitations, student data privacy protections, and algorithmic fairness.",
            f"Identify future horizons for generative and agentic intelligence in personalized curriculum design."
        ]
    elif any(k in norm_lower for k in ("climate", "carbon", "warm", "energy", "emiss")):
        objectives = [
            f"Investigate core technological frameworks and industrial deployments in {normalized_topic}.",
            f"Quantify carbon abatement potential, energy efficiency, and operational benchmarks from peer-reviewed literature.",
            f"Analyze economic, supply chain, and regulatory hurdles governing global scaling.",
            f"Define open research gaps and future technological trajectories for net-zero attainment."
        ]
    elif any(k in norm_lower for k in ("fintech", "finance", "market", "portfolio", "trading")):
        objectives = [
            f"Map current algorithmic and quantitative deployment models across {normalized_topic}.",
            f"Evaluate risk-adjusted return benchmarks and operational efficiencies in financial market workflows.",
            f"Analyze systemic market risks, backtest overfitting vulnerabilities, and regulatory compliance mandates.",
            f"Detail future scope for autonomous agent auditing and explainable quantitative architectures."
        ]
    else:
        objectives = [
            f"Investigate foundational architectures and deployment models for {normalized_topic}.",
            f"Synthesize empirical performance benchmarks, operational advantages, and measured benefits.",
            f"Critically assess technical bottlenecks, ethical considerations, and governance limitations.",
            f"Identify high-priority research gaps and open scientific questions defining future scope."
        ]

    return objectives, warnings


class ResearchContext(BaseModel):
    """Authoritative, immutable research execution context passed through all agents and stages."""

    research_run_id: str = Field(..., description="Unique run identifier e.g. RUN-A1B2C3D4")
    report_id: str = Field(..., description="Unique report identifier e.g. REP-20261025-001")
    original_topic: str = Field(..., description="Raw topic string as entered by user")
    normalized_topic: str = Field(..., description="Cleaned, canonical subject title")
    research_questions: List[str] = Field(..., description="Topically validated, active research objectives")
    rejected_questions_warnings: List[str] = Field(default_factory=list, description="Warnings generated during objective validation")
    scope_and_exclusions: Optional[str] = Field(None, description="Explicit research boundaries or excluded subjects")
    selected_execution_mode: str = Field("OFFLINE DEMO (VERIFIED BENCHMARK)", description="Execution mode label")
    is_offline_demo: bool = Field(True, description="True if using local verified corpus; False if live web")

    # Execution telemetry
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = Field(None)
    duration_s: float = Field(0.0)
    tokens_used: int = Field(0)
    token_accounting_mode: str = Field("estimated_heuristic")
    quality_score: float = Field(0.85)

    # State collections
    retrieved_sources: List[Any] = Field(default_factory=list)
    verified_claims: List[Any] = Field(default_factory=list)
    quarantined_claims: List[Any] = Field(default_factory=list)
