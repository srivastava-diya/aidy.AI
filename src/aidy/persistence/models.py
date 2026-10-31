"""SQLAlchemy ORM models for research runs, sources, verified claims, and reports."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from aidy.persistence.database import Base


class ResearchRunModel(Base):
    """Execution telemetry record for an orchestrated research run."""

    __tablename__ = "research_runs"

    run_id = Column(String(32), primary_key=True, index=True)
    topic = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration_s = Column(Float, nullable=False, default=0.0)
    tokens_used = Column(Integer, nullable=False, default=0)
    token_accounting_mode = Column(String(64), nullable=False, default="estimated_heuristic")
    quality_score = Column(Float, nullable=False, default=0.85)
    errors = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="completed")  # completed, failed, cancelled
    is_offline_demo = Column(Boolean, default=False)
    execution_mode = Column(String(64), default="OFFLINE DEMO (VERIFIED BENCHMARK)")

    sources = relationship("SourceModel", back_populates="run", cascade="all, delete-orphan")
    claims = relationship("ClaimModel", back_populates="run", cascade="all, delete-orphan")
    report = relationship("ReportModel", back_populates="run", uselist=False, cascade="all, delete-orphan")


class SourceModel(Base):
    """Persistent external source record."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(32), ForeignKey("research_runs.run_id"), nullable=False, index=True)
    citation_id = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    url = Column(Text, nullable=False)
    snippet = Column(Text, nullable=False)
    domain = Column(String(128), nullable=False)
    published_date = Column(String(64), nullable=True)
    is_verified = Column(Boolean, default=False)
    retrieval_mode = Column(String(64), default="OFFLINE_DEMO")
    supporting_evidence_excerpt = Column(Text, nullable=True)

    run = relationship("ResearchRunModel", back_populates="sources")


class ClaimModel(Base):
    """Fact-checker verified statement record."""

    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(32), ForeignKey("research_runs.run_id"), nullable=False, index=True)
    claim_id = Column(String(32), nullable=False)
    statement = Column(Text, nullable=False)
    verification_status = Column(String(32), nullable=False)  # Verified, Contradicted, Unverified
    supporting_citations = Column(String(128), nullable=True)  # JSON or comma-separated citation IDs
    rationale = Column(Text, nullable=False)
    confidence = Column(Float, default=0.85)

    run = relationship("ResearchRunModel", back_populates="claims")


class ReportModel(Base):
    """Persistent final research report with human editorial approval tracking."""

    __tablename__ = "reports"

    report_id = Column(String(32), primary_key=True, index=True)
    run_id = Column(String(32), ForeignKey("research_runs.run_id"), nullable=False, unique=True)
    topic = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    executive_summary = Column(Text, nullable=False)
    markdown_content = Column(Text, nullable=False)
    review_status = Column(String(32), nullable=False, default="draft")  # draft, reviewed, final
    reviewer_notes = Column(Text, nullable=True)

    run = relationship("ResearchRunModel", back_populates="report")
