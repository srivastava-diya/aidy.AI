"""Writer Agent definition for structured, citation-grounded research reporting."""

from typing import List, Optional, Any
from crewai import Agent


def create_writer_agent(llm: Optional[Any] = None, tools: Optional[List[Any]] = None) -> Agent:
    """Builds the Writer Agent responsible for compiling the 10-section publication-ready report."""
    return Agent(
        role="Senior Executive Report Author",
        goal="Author an objective, publication-grade research report with complete bracketed citation traceability.",
        backstory=(
            "You are an acclaimed academic and technical editor who crafts clear, precise, and editorial-grade "
            "intelligence reports. You weave verified claims into a cohesive narrative with inline citations ([1], [2]), "
            "strictly honoring evidence limits and avoiding empty superlatives."
        ),
        tools=tools or [],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
