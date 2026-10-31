"""Fact-Checker Agent definition for claim verification and citation audit."""

from typing import List, Optional, Any
from crewai import Agent
from aidy.agents.researcher import load_prompt


def create_fact_checker_agent(llm: Optional[Any] = None, tools: Optional[List[Any]] = None) -> Agent:
    """Builds the Fact-Checker Agent responsible for auditing claims against primary source evidence."""
    return Agent(
        role="Lead Fact-Checker & Source Auditor",
        goal="Audit all factual assertions against retrieved evidence, classifying each as Verified, Contradicted, or Unverified.",
        backstory=(
            "You are an incorruptible fact-checker and scientific auditor. You refuse to accept claims "
            "without direct corroborating evidence in the cited text. If evidence is ambiguous, partial, "
            "or absent, you unequivocally mark the claim as unverified and expose the evidentiary gap."
        ),
        tools=tools or [],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
