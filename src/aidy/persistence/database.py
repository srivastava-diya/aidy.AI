"""Database engine and session management for local SQLite and future PostgreSQL support."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from aidy.core.config import settings

Base = declarative_base()

# Ensure database directory exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_file = db_url.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes all database tables idempotently and ensures schema migrations."""
    import aidy.persistence.models  # noqa: F401
    from sqlalchemy import inspect, text

    Base.metadata.create_all(bind=engine)

    try:
        with engine.begin() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()

            if "research_runs" in tables:
                run_cols = {col["name"] for col in inspector.get_columns("research_runs")}
                if "token_accounting_mode" not in run_cols:
                    conn.execute(text("ALTER TABLE research_runs ADD COLUMN token_accounting_mode VARCHAR(64) DEFAULT 'estimated_heuristic'"))
                if "execution_mode" not in run_cols:
                    conn.execute(text("ALTER TABLE research_runs ADD COLUMN execution_mode VARCHAR(64) DEFAULT 'OFFLINE DEMO (VERIFIED BENCHMARK)'"))

            if "sources" in tables:
                src_cols = {col["name"] for col in inspector.get_columns("sources")}
                if "retrieval_mode" not in src_cols:
                    conn.execute(text("ALTER TABLE sources ADD COLUMN retrieval_mode VARCHAR(64) DEFAULT 'OFFLINE_DEMO'"))
                if "supporting_evidence_excerpt" not in src_cols:
                    conn.execute(text("ALTER TABLE sources ADD COLUMN supporting_evidence_excerpt TEXT DEFAULT ''"))
    except Exception:
        pass


def get_db():
    """Provides a transactional database session scope."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
