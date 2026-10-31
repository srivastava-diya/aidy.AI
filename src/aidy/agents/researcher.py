"""Researcher Agent definition for source collection and evidence extraction."""

import os
from typing import List, Optional, Any
from crewai import Agent


def load_prompt(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_researcher_agent(llm: Optional[Any] = None, tools: Optional[List[Any]] = None) -> Agent:
    """Builds the Researcher Agent equipped with search and webpage reading tools."""
    prompt = load_prompt("researcher_prompt.txt")
    return Agent(
        role="Senior Research Specialist",
        goal="Break down research queries, discover authoritative sources, and extract factual evidence excerpts.",
        backstory=(
            "You are a meticulous investigative researcher with expertise in literature review, "
            "source validation, and information extraction. You never assume or extrapolate; "
            "you gather verified factual records and attribute every fact to its canonical source."
        ),
        tools=tools or [],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
