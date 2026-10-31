"""Crew factory for assembling and configuring CrewAI multi-agent crews."""

from typing import Optional, List, Any
from crewai import Crew, Process

from aidy.agents.researcher import create_researcher_agent
from aidy.agents.fact_checker import create_fact_checker_agent
from aidy.agents.analyst import create_analyst_agent
from aidy.agents.writer import create_writer_agent
from aidy.crew.tasks import (
    create_research_task,
    create_fact_check_task,
    create_analysis_task,
    create_writing_task,
)


def build_research_crew(
    topic: str,
    subquestions: Optional[List[str]] = None,
    max_sources: int = 5,
    llm: Optional[Any] = None,
    research_tools: Optional[List[Any]] = None,
) -> Crew:
    """Instantiates specialized agents and sequentially connects tasks into a coordinated Crew."""
    researcher = create_researcher_agent(llm=llm, tools=research_tools)
    fact_checker = create_fact_checker_agent(llm=llm)
    analyst = create_analyst_agent(llm=llm)
    writer = create_writer_agent(llm=llm)

    task1 = create_research_task(researcher, topic, subquestions, max_sources)
    task2 = create_fact_check_task(fact_checker, task1)
    task3 = create_analysis_task(analyst, task1, task2)
    task4 = create_writing_task(writer, topic, task1, task2, task3)

    crew = Crew(
        agents=[researcher, fact_checker, analyst, writer],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True,
    )
    return crew
