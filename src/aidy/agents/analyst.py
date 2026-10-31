"""Analyst Agent definition for cross-source synthesis and pattern recognition."""

from typing import List, Optional, Any
from crewai import Agent


def create_analyst_agent(llm: Optional[Any] = None, tools: Optional[List[Any]] = None) -> Agent:
    """Builds the Analyst Agent tasked with synthesizing verified claims into strategic insights."""
    return Agent(
        role="Principal Intelligence Analyst",
        goal="Synthesize verified findings across sources, identify patterns, contradictions, and critical research gaps.",
        backstory=(
            "You are a strategic research analyst with deep competence in comparative literature analysis. "
            "You synthesize disparate pieces of evidence, delineate emerging consensus from disputed claims, "
            "and clearly articulate what is known, what is uncertain, and what remains unstudied."
        ),
        tools=tools or [],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
