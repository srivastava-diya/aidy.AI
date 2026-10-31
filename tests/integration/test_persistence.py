"""Integration tests for database persistence and report status updates."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aidy.persistence.database import Base
from aidy.persistence.repositories import RunRepository, ReportRepository
from aidy.crew.workflow import ResearchWorkflowRunner
from aidy.crew.schemas import ResearchQuery
from aidy.export.markdown_export import format_report_as_markdown


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session
    session.close()


def test_save_and_retrieve_run(test_db):
    run_repo = RunRepository(test_db)
    rep_repo = ReportRepository(test_db)

    runner = ResearchWorkflowRunner()
    res = runner.run(ResearchQuery(topic="Clinical Decision AI", max_sources=2))

    md_content = format_report_as_markdown(res["report"])
    saved_run = run_repo.save_run(
        run_id=res["run_id"],
        topic="Clinical Decision AI",
        duration_s=res["duration_s"],
        tokens_used=res["tokens_used"],
        quality_score=res["quality_score"],
        errors=res["errors"],
        sources=res["sources"],
        claims=res["verified_claims"],
        report=res["report"],
        markdown_content=md_content,
    )

    assert saved_run.run_id == res["run_id"]
    retrieved = run_repo.get_run(res["run_id"])
    assert retrieved is not None
    assert len(retrieved.sources) == len(res["sources"])
    assert len(retrieved.claims) == len(res["verified_claims"])

    # Test editorial update
    report_obj = rep_repo.get_report(res["report"].report_id)
    assert report_obj.review_status == "draft"
    rep_repo.update_status(res["report"].report_id, "final", "Reviewed by clinical lead.")
    updated_rep = rep_repo.get_report(res["report"].report_id)
    assert updated_rep.review_status == "final"
    assert updated_rep.reviewer_notes == "Reviewed by clinical lead."
