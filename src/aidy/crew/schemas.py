"""Structured Pydantic models for agent outputs, claim verification, and research reports."""

from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ResearchQuery(BaseModel):
    """Input parameters for initiating a research workflow."""

    topic: str = Field(..., min_length=3, description="Core research topic or question")
    subquestions: Optional[List[str]] = Field(default_factory=list, description="Specific sub-questions to investigate")
    depth: Literal["standard", "comprehensive", "deep_dive"] = Field("comprehensive", description="Investigation depth")
    max_sources: int = Field(5, ge=2, le=15, description="Maximum number of primary sources to retrieve")
    constraints: Optional[str] = Field(None, description="Scope boundaries, excluded domains, or specific guidelines")


class EvidenceSnippet(BaseModel):
    """Extracted factual snippet linked to a specific registered source."""

    source_citation_id: int = Field(..., description="1-indexed reference matching [citation_id]")
    source_url: str = Field(..., description="Canonical URL of the source")
    source_title: str = Field(..., description="Title of the source")
    extracted_text: str = Field(..., description="Direct factual quote or paraphrased evidence")
    relevance_score: float = Field(default=0.85, ge=0.0, le=1.0)


class VerifiedClaim(BaseModel):
    """Factual claim evaluated against retrieved evidence with exact citation grounding."""

    claim_id: str = Field(..., description="Identifier e.g. C01, C02")
    statement: str = Field(..., description="Core factual statement evaluated")
    verification_status: Literal["Verified", "Contradicted", "Unverified", "CLAIM SUPPORTED"] = Field(
        ..., description="Verification verdict strictly supported by evidence"
    )
    support_type: Literal["EXACT_QUOTATION", "SUPPORTED_PARAPHRASE", "UNSUPPORTED"] = Field(
        "SUPPORTED_PARAPHRASE", description="Granular proof type: verbatim quote or semantic paraphrase"
    )
    supporting_citation_ids: List[int] = Field(default_factory=list, description="Citation IDs providing proof")
    exact_text_spans: List[str] = Field(default_factory=list, description="Verified substrings from source text")
    supporting_evidence_quote: Optional[str] = Field(None, description="Verbatim text quote from cited source")
    rationale: str = Field(..., description="Detailed verification rationale explaining evidence support or gaps")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class AnalyticalSynthesis(BaseModel):
    """Deep structural synthesis of verified evidence produced by Analyst Agent."""

    key_patterns: List[str] = Field(..., description="Identified patterns and convergences across sources")
    disagreements_and_tensions: List[str] = Field(..., description="Contradictions or debates in literature")
    critical_uncertainties: List[str] = Field(..., description="Unproven assertions or ambiguous outcomes")
    research_gaps: List[str] = Field(..., description="Unaddressed research areas or missing data")


class ResearchReport(BaseModel):
    """Final industry-grade research report with full citation traceability."""

    report_id: str = Field(..., description="Unique report identifier e.g. REP-2026-001")
    topic: str = Field(..., description="Title of the research report")
    normalized_topic: Optional[str] = Field(None, description="Normalized canonical subject title")
    rejected_questions_warnings: List[str] = Field(default_factory=list, description="Warnings for rejected off-topic questions")
    research_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    executive_summary: str = Field(..., description="Concise executive synthesis of findings and implications")
    research_objectives: List[str] = Field(..., description="Specific research aims addressed")
    methodology: str = Field(..., description="Methodology, source collection, and fact-checking protocols applied")
    key_findings: List[str] = Field(..., description="Core empirical findings supported by citations")
    evidence_based_analysis: str = Field(..., description="In-depth analytical exploration of evidence")
    conflicting_evidence_and_uncertainty: str = Field(..., description="Analysis of contradictions and limits")
    research_gaps_and_limitations: List[str] = Field(..., description="Documented study boundaries and open questions")
    conclusion: str = Field(..., description="Concluding synthesis and forward-looking perspective")
    references: List[Dict[str, Any]] = Field(..., description="Traceable bibliography with URLs and citation tags")
    review_status: Literal["draft", "reviewed", "final"] = Field("draft", description="Human editorial approval status")

    # Audit & Execution telemetry
    is_offline_demo: bool = Field(False, description="Flag indicating if generated with offline benchmark data")
    execution_mode: str = Field("OFFLINE DEMO (VERIFIED BENCHMARK)", description="LIVE RESEARCH or OFFLINE DEMO")
    token_accounting_mode: Literal["exact_provider_usage", "estimated_heuristic", "unavailable"] = Field(
        "estimated_heuristic", description="Method used to calculate token expenditure"
    )
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_duration_s: float = Field(0.0, description="End-to-end execution runtime in seconds")
    tokens_consumed: int = Field(0, description="Total tokens used or estimated")
    quality_score: float = Field(0.85, description="Automated quality score based on citation fidelity")
    unsupported_claims: List[VerifiedClaim] = Field(default_factory=list, description="Claims excluded due to lack of proof")
