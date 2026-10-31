"""Integration tests for multi-agent workflow orchestration and report generation."""

import pytest
from aidy.crew.workflow import ResearchWorkflowRunner
from aidy.crew.schemas import ResearchQuery
from aidy.tools.source_registry import SourceRegistry


def test_workflow_end_to_end_execution():
    runner = ResearchWorkflowRunner(registry=SourceRegistry())
    query = ResearchQuery(
        topic="Agentic AI in Healthcare",
        subquestions=["What are clinical accuracy rates?"],
        depth="standard",
        max_sources=3,
    )

    events = []
    def callback(stage, msg, details):
        events.append((stage, details.get("stage_idx")))

    result = runner.run(query, status_callback=callback)

    assert result["run_id"].startswith("RUN-")
    assert len(result["sources"]) > 0
    assert len(result["verified_claims"]) >= 2
    assert result["report"] is not None
    assert result["report"].review_status == "draft"  # Strict human review rule!
    assert result["quality_score"] > 0.6
    assert len(events) >= 6  # Verified all stages emitted
