"""Unit tests for SourceRegistry deduplication, citation indexing, and verification."""

import pytest
from aidy.tools.source_registry import SourceRegistry


def test_source_registry_deduplication():
    reg = SourceRegistry()
    s1 = reg.add_source(
        title="Agentic AI in Healthcare",
        url="https://nature.com/articles/agentic-health/",
        snippet="Empirical trial results.",
    )
    s2 = reg.add_source(
        title="Duplicate Entry",
        url="https://nature.com/articles/agentic-health",  # trailing slash removed during normalization
        snippet="Duplicate snippet.",
    )

    assert s1.citation_id == 1
    assert s2.citation_id == 1  # Deduplicated
    assert len(reg.get_all()) == 1


def test_source_registry_sequential_ids():
    reg = SourceRegistry()
    s1 = reg.add_source("Paper 1", "https://arxiv.org/abs/2401.0001", "Snippet 1")
    s2 = reg.add_source("Paper 2", "https://arxiv.org/abs/2401.0002", "Snippet 2")

    assert s1.citation_id == 1
    assert s2.citation_id == 2
    assert reg.get_by_citation_id(2).title == "Paper 2"

    reg.mark_verified(2)
    assert reg.get_by_citation_id(2).is_verified is True
