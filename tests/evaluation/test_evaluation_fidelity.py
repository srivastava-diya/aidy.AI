"""Evaluation tests measuring factual grounding, citation integrity, and failure isolation."""

import pytest
from aidy.crew.workflow import ResearchWorkflowRunner
from aidy.crew.schemas import ResearchQuery
from aidy.tools.source_registry import SourceRegistry


def test_citation_integrity_and_referencing():
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res = runner.run(query)

    sources = res["sources"]
    valid_citation_ids = {s.citation_id for s in sources}

    # Verify every claim's citation ID corresponds to an actual registered source
    for claim in res["verified_claims"]:
        for cid in claim.supporting_citation_ids:
            assert cid in valid_citation_ids, f"Claim {claim.claim_id} cites non-existent citation ID {cid}"


def test_unsupported_claim_detection():
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(topic="Agentic AI in Healthcare", max_sources=3)
    res = runner.run(query)

    # Ensure at least one claim is audited as Contradicted/Unverified when unsupported
    claims = res["verified_claims"]
    contradicted_or_unverified = [c for c in claims if c.verification_status in ("Contradicted", "Unverified")]
    assert len(contradicted_or_unverified) >= 1, "Fact-Checker failed to flag unsupported or contradictory statements!"


def test_draft_status_enforcement():
    runner = ResearchWorkflowRunner()
    res = runner.run(ResearchQuery(topic="Ethics in AI", max_sources=2))
    assert res["report"].review_status == "draft", "Report was automatically published without human review!"
