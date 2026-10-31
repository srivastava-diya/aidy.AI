"""Repository implementations for persisting runs, sources, and reports."""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from aidy.persistence.models import ResearchRunModel, SourceModel, ClaimModel, ReportModel
from aidy.crew.schemas import ResearchReport, VerifiedClaim
from aidy.tools.source_registry import SourceRecord


class RunRepository:
    """Manages CRUD operations and aggregate metrics for research runs."""

    def __init__(self, db: Session):
        self.db = db

    def save_run(
        self,
        run_id: str,
        topic: str,
        duration_s: float,
        tokens_used: int,
        quality_score: float,
        errors: int,
        sources: List[SourceRecord],
        claims: List[VerifiedClaim],
        report: ResearchReport,
        markdown_content: str,
        is_offline_demo: bool = False,
    ) -> ResearchRunModel:
        """Persists the full execution artifact graph in a single atomic transaction."""
        run_obj = ResearchRunModel(
            run_id=run_id,
            topic=topic,
            duration_s=duration_s,
            tokens_used=tokens_used,
            token_accounting_mode=getattr(report, "token_accounting_mode", "estimated_heuristic"),
            quality_score=quality_score,
            errors=errors,
            status="completed",
            is_offline_demo=is_offline_demo,
            execution_mode=getattr(report, "execution_mode", "OFFLINE DEMO (VERIFIED BENCHMARK)"),
        )
        self.db.add(run_obj)

        for s in sources:
            source_obj = SourceModel(
                run_id=run_id,
                citation_id=s.citation_id,
                title=s.title,
                url=s.url,
                snippet=s.snippet,
                domain=s.domain,
                published_date=s.published_date,
                is_verified=s.is_verified,
                retrieval_mode=getattr(s, "retrieval_mode", "OFFLINE_DEMO"),
                supporting_evidence_excerpt=getattr(s, "supporting_evidence_excerpt", s.snippet),
            )
            self.db.add(source_obj)

        for c in claims:
            claim_obj = ClaimModel(
                run_id=run_id,
                claim_id=c.claim_id,
                statement=c.statement,
                verification_status=c.verification_status,
                supporting_citations=json.dumps(c.supporting_citation_ids),
                rationale=c.rationale,
                confidence=c.confidence,
            )
            self.db.add(claim_obj)

        report_obj = ReportModel(
            report_id=report.report_id,
            run_id=run_id,
            topic=topic,
            executive_summary=report.executive_summary,
            markdown_content=markdown_content,
            review_status="draft",
        )
        self.db.add(report_obj)

        self.db.commit()
        self.db.refresh(run_obj)
        return run_obj

    def get_run(self, run_id: str) -> Optional[ResearchRunModel]:
        return self.db.query(ResearchRunModel).filter(ResearchRunModel.run_id == run_id).first()

    def list_recent_runs(self, limit: int = 20) -> List[ResearchRunModel]:
        return (
            self.db.query(ResearchRunModel)
            .order_by(desc(ResearchRunModel.created_at))
            .limit(limit)
            .all()
        )

    def get_live_metrics(self) -> Dict[str, Any]:
        """Calculates factual aggregate telemetry over actual stored research runs."""
        runs = self.db.query(ResearchRunModel).all()
        total_runs = len(runs)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "avg_duration_s": 0.0,
                "avg_tokens": 0,
                "avg_quality": 0.0,
            }

        successful = sum(1 for r in runs if r.status == "completed" and r.errors == 0)
        failed = sum(1 for r in runs if r.status == "failed" or r.errors > 0)
        avg_dur = sum(r.duration_s for r in runs) / total_runs
        avg_tok = sum(r.tokens_used for r in runs) / total_runs
        avg_qual = sum(r.quality_score for r in runs) / total_runs

        return {
            "total_runs": total_runs,
            "successful_runs": successful,
            "failed_runs": failed,
            "avg_duration_s": round(avg_dur, 2),
            "avg_tokens": int(avg_tok),
            "avg_quality": round(avg_qual, 3),
        }


class ReportRepository:
    """Manages queries, content updates, and editorial approval states for research reports."""

    def __init__(self, db: Session):
        self.db = db

    def get_report(self, report_id: str) -> Optional[ReportModel]:
        return self.db.query(ReportModel).filter(ReportModel.report_id == report_id).first()

    def list_reports(self, limit: int = 50) -> List[ReportModel]:
        return (
            self.db.query(ReportModel)
            .order_by(desc(ReportModel.created_at))
            .limit(limit)
            .all()
        )

    def update_status(self, report_id: str, new_status: str, notes: Optional[str] = None) -> bool:
        rep = self.get_report(report_id)
        if not rep:
            return False
        rep.review_status = new_status
        if notes:
            rep.reviewer_notes = notes
        self.db.commit()
        return True

    def update_markdown(self, report_id: str, new_content: str) -> bool:
        rep = self.get_report(report_id)
        if not rep:
            return False
        rep.markdown_content = new_content
        self.db.commit()
        return True
