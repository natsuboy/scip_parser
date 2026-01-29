"""
Tests for QueryAPI.
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
from scip_parser.query.api import QueryAPI


@pytest.fixture
def mock_index():
    doc = Document(
        relative_path="test.py",
        language="python",
        occurrences=(),
        symbols={
            "func": SymbolInformation(
                symbol="func", kind=SymbolKind.Function, display_name="my_function"
            ),
            "cls": SymbolInformation(symbol="cls", kind=SymbolKind.Class, display_name="MyClass"),
        },
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=(doc,))
    index.build_indexes()
    return index


def test_query_api_fluent(mock_index):
    results = QueryAPI(mock_index).by_kind(SymbolKind.Function).execute()
    assert len(results) == 1
    assert results[0].display_name == "my_function"

    results = QueryAPI(mock_index).by_language("python").execute()
    assert len(results) == 2

    results = QueryAPI(mock_index).by_name("MyClass").execute()
    assert len(results) == 1
    assert results[0].display_name == "MyClass"


def test_query_api_chaining(mock_index):
    # Chain filters
    api = QueryAPI(mock_index)
    results = api.by_language("python").by_kind(SymbolKind.Class).execute()
    assert len(results) == 1
    assert results[0].display_name == "MyClass"

    # New instance for no match
    results = QueryAPI(mock_index).by_language("java").execute()
    assert len(results) == 0


def test_query_api_first_count(mock_index):
    assert QueryAPI(mock_index).by_kind(SymbolKind.Function).count() == 1

    first = QueryAPI(mock_index).by_kind(SymbolKind.Class).first()
    assert first is not None
    assert first.display_name == "MyClass"
