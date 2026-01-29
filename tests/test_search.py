"""
Tests for SymbolSearcher.
"""

import pytest

from scip_parser.core.types import (
    Document,
    Index,
    Metadata,
    SymbolInformation,
    SymbolKind,
    ToolInfo,
)
from scip_parser.query.search import SymbolSearcher


@pytest.fixture
def mock_index():
    symbols = {
        "A": SymbolInformation(
            symbol="A", kind=SymbolKind.Function, display_name="calculate_total"
        ),
        "B": SymbolInformation(symbol="B", kind=SymbolKind.Class, display_name="Calculator"),
        "C": SymbolInformation(
            symbol="C", kind=SymbolKind.Function, display_name="calculate_average"
        ),
    }
    doc = Document(relative_path="test.py", language="python", occurrences=[], symbols=symbols)
    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_search_basic(mock_index):
    searcher = SymbolSearcher(mock_index)
    results = searcher.search("calculate")
    assert len(results) == 2
    names = sorted(r.display_name for r in results)
    assert names == ["calculate_average", "calculate_total"]


def test_fuzzy_search(mock_index):
    searcher = SymbolSearcher(mock_index)

    # Typo "Calclator" -> "Calculator"
    results = searcher.fuzzy_search("Calclator")
    assert len(results) > 0
    assert results[0].display_name == "Calculator"


def test_autocomplete(mock_index):
    searcher = SymbolSearcher(mock_index)
    # Prefix match
    results = searcher.autocomplete("calc")
    assert len(results) == 3
    names = sorted(r.display_name for r in results)
    assert names == ["Calculator", "calculate_average", "calculate_total"]

    results = searcher.autocomplete("Calculator")
    assert len(results) == 1
    assert results[0].display_name == "Calculator"
