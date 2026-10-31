"""Coordinator and Crew Manager definition for workflow supervision and execution budgets."""

from typing import List, Optional, Any
from crewai import Agent


def create_coordinator_agent(llm: Optional[Any] = None, tools: Optional[List[Any]] = None) -> Agent:
    """Builds the Coordinator Agent responsible for overall workflow supervision."""
    return Agent(
        role="Research Crew Coordinator & Director",
        goal="Manage the sequence of research tasks, pass validated evidence, and enforce execution budgets.",
        backstory=(
            "You are an executive research manager. You ensure tasks transition cleanly between agents, "
            "verify that all outputs adhere to quality benchmarks, and ensure research operations complete "
            "within strict execution bounds."
        ),
        tools=tools or [],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )
