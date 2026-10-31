"""Data validation schemas and models for dataset processing in aidy.AI."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class AgentActivityRecord(BaseModel):
    """Schema for individual multi-agent activity run logs."""

    run_id: str = Field(..., description="Unique identifier for the research run (e.g. R111)")
    agent_role: Literal["Researcher", "Fact_Checker", "Analyst", "Writer", "Editor", "Publisher"] = Field(
        ..., description="Specialized role assumed by the agent"
    )
    task_type: str = Field(..., description="Domain topic or task category (e.g. HealthAI, FinTech)")
    tokens_used: int = Field(..., ge=0, le=100000, description="Total tokens consumed in the task")
    duration_s: float = Field(..., ge=0.0, le=3600.0, description="Execution duration in seconds")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Assessed output quality score [0.0 - 1.0]")
    errors: int = Field(0, ge=0, le=10, description="Number of execution errors or retries encountered")

    @field_validator("run_id")
    @classmethod
    def validate_run_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("run_id cannot be blank")
        return v


class DataCleaningReport(BaseModel):
    """Audit report generated during dataset cleaning and validation."""

    initial_row_count: int
    final_row_count: int
    missing_values_found: int
    duplicates_removed: int
    outliers_flagged: int
    corrections_applied: int
    schema_compliance_rate: float
    summary: str
