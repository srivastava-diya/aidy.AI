"""Automated regression test suite verifying critical pipeline fixes:
1. Healthcare topic never receives education objectives.
2. Education topic receives relevant education objectives.
3. A second research run does not inherit the first run's topic or findings.
4. Findings do not contain awkward raw-topic sentence insertion.
5. A fabricated source excerpt cannot pass exact-quotation verification.
6. A valid URL alone cannot make an unsupported claim VERIFIED.
7. Unsupported claims are quarantined.
8. Citations resolve to the correct source records.
9. Reports Library loads the correct saved report by ID.
10. Editing a report does not overwrite its audit evidence.
11. Offline demo mode is clearly labelled and never falsely reported as live retrieval.
12. Missing source content produces an explicit unverified status.
"""

import os
import pytest
from aidy.crew.workflow import (
    ResearchWorkflowRunner,
    verify_claim_against_source,
    formulate_natural_claim_statement,
)
from aidy.crew.schemas import ResearchQuery
from aidy.crew.context import normalize_topic, derive_research_objectives
from aidy.tools.source_registry import SourceRegistry, SourceRecord
from aidy.persistence.database import SessionLocal, init_db
from aidy.persistence.repositories import RunRepository, ReportRepository
from aidy.export.markdown_export import format_report_as_markdown, save_markdown_report


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_01_healthcare_topic_never_receives_education_objectives():
    """1. Healthcare topic never receives education objectives even if user enters off-topic questions."""
    topic = "Research the current applications, benefits, limitations, and future scope of Agentic AI in healthcare."
    norm = normalize_topic(topic)
    assert norm == "Agentic AI in healthcare"

    # Even if off-topic education questions are provided, the system must reject them with a warning
    mismatched_subqs = ["How does adaptive grading improve classroom student retention?"]
    objs, warnings = derive_research_objectives(topic, norm, mismatched_subqs)

    assert len(warnings) > 0
    assert any("education" in w.lower() for w in warnings)
    for obj in objs:
        assert "education" not in obj.lower()
        assert "classroom" not in obj.lower()
        assert "student" not in obj.lower()
    assert any("health" in obj.lower() or "clinical" in obj.lower() for obj in objs)


def test_02_education_topic_receives_relevant_education_objectives():
    """2. Education topic receives relevant education objectives."""
    topic = "AI in education"
    norm = normalize_topic(topic)
    objs, warnings = derive_research_objectives(topic, norm, None)

    assert len(objs) >= 3
    assert any("education" in obj.lower() or "learning" in obj.lower() or "tutoring" in obj.lower() for obj in objs)
    for obj in objs:
        assert "clinic" not in obj.lower()
        assert "patient" not in obj.lower()


def test_03_second_research_run_does_not_inherit_first_run():
    """3. A second research run does not inherit the first run's topic, objectives, or findings."""
    runner1 = ResearchWorkflowRunner(registry=SourceRegistry())
    query1 = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res1 = runner1.run(query1)

    runner2 = ResearchWorkflowRunner(registry=SourceRegistry())
    query2 = ResearchQuery(topic="Decarbonization in Climate Tech", max_sources=2)
    res2 = runner2.run(query2)

    assert res1["run_id"] != res2["run_id"]
    assert res1["report"].report_id != res2["report"].report_id
    assert res1["report"].normalized_topic == "Agentic AI in Healthcare"
    assert res2["report"].normalized_topic == "Decarbonization in Climate Tech"

    # Verify no cross-contamination in findings or objectives
    for finding in res2["report"].key_findings:
        assert "health" not in finding.lower()
        assert "patient" not in finding.lower()

    for obj in res2["report"].research_objectives:
        assert "health" not in obj.lower()


def test_04_findings_do_not_contain_awkward_raw_topic_concatenation():
    """4. Findings do not contain awkward raw-topic sentence insertion."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(
        topic="Research the current applications, benefits, limitations, and future scope of Agentic AI in healthcare.",
        max_sources=4,
    )
    res = runner.run(query)
    report = res["report"]

    for finding in report.key_findings:
        assert "According to published research on Research the" not in finding
        assert "on Research the current applications" not in finding
        # Must be natural and end cleanly
        assert not finding.startswith("Research the current")


def test_05_fabricated_source_excerpt_cannot_pass_exact_quotation():
    """5. A fabricated source excerpt cannot pass exact-quotation verification."""
    source = SourceRecord(
        citation_id=1,
        title="High-performance medicine: the convergence of human and artificial intelligence",
        url="https://www.nature.com/articles/s41591-018-0300-7",
        snippet="Deep learning enables automated pattern recognition across medical imaging.",
        domain="nature.com",
    )

    fabricated_quote = "This system achieved a miraculous 99.99% diagnostic infallibility across all patient cohorts."
    claim = "Clinical algorithms achieve near-perfect diagnostic precision."

    v_res = verify_claim_against_source(claim, source, claimed_exact_quote=fabricated_quote)
    v_status, conf, rationale, quote = v_res

    assert v_status == "Unverified"
    assert quote is None
    assert "Quotation verification failed" in rationale


def test_06_valid_url_alone_cannot_verify_unsupported_claim():
    """6. A valid URL alone cannot make an unsupported claim VERIFIED."""
    source = SourceRecord(
        citation_id=1,
        title="Ethics and governance of artificial intelligence for health: WHO guidance",
        url="https://www.who.int/publications/i/item/9789240029200",
        snippet="WHO guidance emphasizes protecting human autonomy, promoting human safety, and ensuring explainability.",
        domain="who.int",
        url_verified=True,  # URL is valid and trusted
    )

    # Claim has zero evidence in snippet
    unsupported_claim = "Autonomous crypto mining algorithms reduce GPU energy consumption by 85%."
    v_res = verify_claim_against_source(unsupported_claim, source)
    v_status, conf, rationale, quote = v_res

    assert v_status == "Unverified"
    assert quote is None
    assert "Insufficient direct evidentiary support" in rationale


def test_07_unsupported_claims_are_quarantined():
    """7. Unsupported and contradicted claims are quarantined and excluded from Key Findings."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res = runner.run(query)

    report = res["report"]
    quarantined = res["report"].unsupported_claims

    assert len(quarantined) >= 1
    for qc in quarantined:
        assert qc.verification_status in ("Contradicted", "Unverified")
        # Ensure quarantined statement never leaks into key findings
        for finding in report.key_findings:
            assert qc.statement not in finding
        # Ensure quarantined statement is documented in conflicting evidence section
        assert qc.claim_id in report.conflicting_evidence_and_uncertainty


def test_08_citations_resolve_to_correct_source_records():
    """8. Citations resolve to the correct persisted source records."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res = runner.run(query)

    sources = {s.citation_id: s for s in res["sources"]}
    report = res["report"]

    for ref in report.references:
        cid = ref["citation_id"]
        assert cid in sources
        assert ref["title"] == sources[cid].title
        assert ref["url"] == sources[cid].url
        assert ref["domain"] == sources[cid].domain


def test_09_reports_library_loads_correct_saved_report_by_id():
    """9. Reports Library loads the correct saved report by ID."""
    db = SessionLocal()
    try:
        repo_run = RunRepository(db)
        repo_rep = ReportRepository(db)

        runner = ResearchWorkflowRunner(registry=SourceRegistry())
        query = ResearchQuery(topic="Climate Decarbonization Test", max_sources=2)
        res = runner.run(query)
        rep = res["report"]
        md = format_report_as_markdown(rep)

        repo_run.save_run(
            run_id=res["run_id"],
            topic=query.topic,
            duration_s=res["duration_s"],
            tokens_used=res["tokens_used"],
            quality_score=res["quality_score"],
            errors=res["errors"],
            sources=res["sources"],
            claims=res["verified_claims"],
            report=rep,
            markdown_content=md,
            is_offline_demo=rep.is_offline_demo,
        )

        loaded = repo_rep.get_report(rep.report_id)
        assert loaded is not None
        assert loaded.report_id == rep.report_id
        assert loaded.run_id == res["run_id"]
        assert loaded.topic == query.topic
        assert "Climate Decarbonization" in loaded.markdown_content
    finally:
        db.close()


def test_10_editing_report_does_not_overwrite_audit_evidence():
    """10. Editing a report does not overwrite its underlying source evidence or claim verification audit."""
    db = SessionLocal()
    try:
        repo_run = RunRepository(db)
        repo_rep = ReportRepository(db)

        runner = ResearchWorkflowRunner(registry=SourceRegistry())
        query = ResearchQuery(topic="Audit Evidence Preservation Test", max_sources=2)
        res = runner.run(query)
        rep = res["report"]
        md = format_report_as_markdown(rep)

        run_model = repo_run.save_run(
            run_id=res["run_id"],
            topic=query.topic,
            duration_s=res["duration_s"],
            tokens_used=res["tokens_used"],
            quality_score=res["quality_score"],
            errors=res["errors"],
            sources=res["sources"],
            claims=res["verified_claims"],
            report=rep,
            markdown_content=md,
            is_offline_demo=rep.is_offline_demo,
        )

        initial_sources_count = len(run_model.sources)
        initial_claims_count = len(run_model.claims)

        # Edit markdown content
        edited_md = md + "\n\n## 10. Editorial Addendum\nReviewed and annotated by human reviewer."
        success = repo_rep.update_markdown(rep.report_id, edited_md)
        assert success is True

        # Re-fetch run and verify sources and claims are completely untouched
        refetched_run = repo_run.get_run(res["run_id"])
        assert len(refetched_run.sources) == initial_sources_count
        assert len(refetched_run.claims) == initial_claims_count
        assert "Editorial Addendum" in refetched_run.report.markdown_content
    finally:
        db.close()


def test_11_offline_demo_mode_clearly_labelled():
    """11. Offline demo mode is clearly labelled and never falsely reported as live retrieval."""
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=2)
    res = runner.run(query)
    rep = res["report"]

    assert rep.is_offline_demo is True
    assert "OFFLINE DEMO" in rep.execution_mode
    assert "OFFLINE DEMO" in rep.executive_summary

    for ref in rep.references:
        assert ref["retrieval_mode"] in ("OFFLINE_VERIFIED_BENCHMARK", "OFFLINE_BENCHMARK_CORPUS")
        # Check transparent multi-tiered badges
        assert "BENCHMARK ABSTRACT RETRIEVED" in ref["verification_badges"] or "CONTENT RETRIEVED" in ref["verification_badges"]


def test_12_missing_source_content_produces_explicit_unverified_status():
    """12. Missing source content produces an explicit unverified status."""
    source_empty = SourceRecord(
        citation_id=99,
        title="Empty Source Test",
        url="https://example.com/empty",
        snippet="",
        full_content=None,
        domain="example.com",
    )

    claim = "Deep learning achieves 90% diagnostic accuracy."
    v_res = verify_claim_against_source(claim, source_empty)
    v_status, conf, rationale, quote = v_res

    assert v_status == "Unverified"
    assert quote is None
    assert "Missing source content" in rationale
