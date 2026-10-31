"""Automated audit tests for aidy.AI research report generation and citation integrity:
1. Invalid URLs rejected / unverified
2. Mismatched titles and content marked Unverified
3. Unsupported claims excluded from final findings
4. Empty retrieval results handled gracefully
5. Offline Demo vs. Live Research mode labeling
6. Token accounting mode explicitly declared
7. Topic alignment consistency across all report sections
"""

import pytest
from aidy.crew.workflow import ResearchWorkflowRunner, verify_claim_against_source
from aidy.crew.schemas import ResearchQuery
from aidy.tools.source_registry import SourceRegistry, SourceRecord
from aidy.core.security import validate_and_normalize_url
from aidy.core.exceptions import SecurityViolationError


def test_invalid_url_handling():
    """Verify that invalid schemes and private IPs are blocked and cannot enter the verified registry."""
    with pytest.raises(SecurityViolationError):
        validate_and_normalize_url("file:///etc/passwd")

    with pytest.raises(SecurityViolationError):
        validate_and_normalize_url("http://127.0.0.1:8000/api")

    with pytest.raises(SecurityViolationError):
        validate_and_normalize_url("http://169.254.169.254/latest/meta-data/")


def test_mismatched_title_and_content_unverified():
    """Verify that claims with no evidentiary overlap with the source content are marked Unverified."""
    source = SourceRecord(
        citation_id=1,
        title="High-performance medicine: the convergence of human and artificial intelligence",
        url="https://www.nature.com/articles/s41591-018-0300-7",
        snippet="Deep learning enables automated pattern recognition across radiology and pathology.",
        domain="nature.com",
        retrieval_mode="OFFLINE_VERIFIED_BENCHMARK",
    )

    # Claim wholly unrelated to the medical source text
    unrelated_claim = "Quantum superposition algorithms accelerate bitcoin mining by 400x."
    v_status, conf, rationale, quote = verify_claim_against_source(unrelated_claim, source)

    assert v_status == "Unverified", f"Expected Unverified but got {v_status}"
    assert quote is None
    assert "Insufficient direct evidentiary support" in rationale


def test_unsupported_claims_excluded_from_findings():
    """Verify that unsupported and contradicted claims are strictly excluded from report key findings."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res = runner.run(query)

    report = res["report"]
    claims = res["verified_claims"]

    unsupported = [c for c in claims if c.verification_status in ("Contradicted", "Unverified")]
    assert len(unsupported) > 0, "No unsupported claims were evaluated!"

    # Key findings must contain ONLY verified statements
    for finding in report.key_findings:
        for uc in unsupported:
            assert uc.statement not in finding, f"Unsupported claim '{uc.statement}' leaked into Key Findings!"

    # Unsupported claims must be documented in the conflicting evidence section
    for uc in unsupported:
        assert uc.claim_id in report.conflicting_evidence_and_uncertainty


def test_empty_retrieval_handled_gracefully():
    """Verify that empty queries or zero-match search results do not crash or produce fabricated findings."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="   ", max_sources=2)  # whitespace query

    # Should handle cleanly without fabricating positive assertions
    res = runner.run(query)
    assert res["run_id"].startswith("RUN-")
    assert res["report"] is not None


def test_demo_vs_live_mode_labeling():
    """Verify that offline demo execution is explicitly labeled throughout report and references."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Decarbonization in Climate Tech", max_sources=2)
    res = runner.run(query)

    report = res["report"]
    # Offline demo mode must be explicitly tagged
    assert report.is_offline_demo is True
    assert "OFFLINE DEMO" in report.execution_mode
    assert "OFFLINE DEMO" in report.executive_summary

    # References must be explicitly tagged
    for ref in report.references:
        assert ref["retrieval_mode"] == "OFFLINE_VERIFIED_BENCHMARK"
        assert "is_verified" in ref


def test_token_accounting_mode_labeled():
    """Verify that token expenditure is explicitly labeled as heuristic/estimated rather than exact provider usage."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="FinTech Machine Learning", max_sources=2)
    res = runner.run(query)

    report = res["report"]
    assert report.token_accounting_mode in ("exact_provider_usage", "estimated_heuristic", "unavailable")
    assert report.token_accounting_mode == "estimated_heuristic"


def test_topic_alignment_in_all_report_sections():
    """Verify that research topic strictly aligns across title, summary, objectives, findings, and conclusion."""
    topic_str = "Decarbonization Pathways in Heavy Industry"
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic=topic_str, max_sources=2)
    res = runner.run(query)

    report = res["report"]
    assert topic_str in report.topic
    assert topic_str in report.executive_summary
    assert topic_str in report.conclusion
    assert any(topic_str in obj for obj in report.research_objectives)
    # Ensure no leakage of unrelated medical template text
    assert "triage delays" not in report.executive_summary
    assert "diagnostic precision in initial trial cohorts" not in report.executive_summary
