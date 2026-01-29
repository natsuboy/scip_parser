"""
Tests for Index symbol search methods.
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


@pytest.fixture
def mock_index():
    # Create some dummy symbols
    sym1 = SymbolInformation(
        symbol="scip-python npm scip-python 0.1.0 index.py/main().",
        kind=SymbolKind.Function,
        display_name="main",
    )
    sym2 = SymbolInformation(
        symbol="scip-python npm scip-python 0.1.0 utils.py/Helper#",
        kind=SymbolKind.Class,
        display_name="Helper",
    )
    sym3 = SymbolInformation(
        symbol="scip-python npm scip-python 0.1.0 utils.py/Helper#help().",
        kind=SymbolKind.Method,
        display_name="help",
    )

    doc1 = Document(
        relative_path="index.py",
        language="python",
        occurrences=(),
        symbols={"scip-python npm scip-python 0.1.0 index.py/main().": sym1},
    )

    doc2 = Document(
        relative_path="utils.py",
        language="python",
        occurrences=(),
        symbols={
            "scip-python npm scip-python 0.1.0 utils.py/Helper#": sym2,
            "scip-python npm scip-python 0.1.0 utils.py/Helper#help().": sym3,
        },
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1.0"), project_root="/")

    index = Index(metadata=metadata, documents=(doc1, doc2))
    index.build_indexes()  # Build internal index if needed
    return index


def test_find_symbols_by_name(mock_index):
    # Test exact match
    results = mock_index.find_symbols_by_name("main", exact_match=True)
    assert len(results) == 1
    assert results[0].display_name == "main"

    # Test exact match fail
    results = mock_index.find_symbols_by_name("mai", exact_match=True)
    assert len(results) == 0

    # Test substring match
    results = mock_index.find_symbols_by_name("el", exact_match=False)
    # Should match "Helper" and "help"
    assert len(results) == 2
    names = sorted([r.display_name for r in results])
    assert names == ["Helper", "help"]


def test_find_symbols_by_pattern(mock_index):
    # Test pattern matching
    results = mock_index.find_symbols_by_pattern("*He*")
    assert len(results) == 1
    assert results[0].display_name == "Helper"

    results = mock_index.find_symbols_by_pattern("h*")
    assert len(results) == 1
    assert results[0].display_name == "help"


def test_search_symbols(mock_index):
    # Test general search (case insensitive substring for now)
    results = mock_index.search_symbols("helper")
    assert len(results) >= 1
    assert any(r.display_name == "Helper" for r in results)
