"""
Tests for Index Analytics.
"""

import pytest

from scip_parser.core.types import (
    Document,
    Index,
    Metadata,
    Occurrence,
    SymbolInformation,
    SymbolKind,
    SymbolRole,
    ToolInfo,
)


@pytest.fixture
def index_with_stats():
    doc1 = Document(
        relative_path="a.py",
        language="python",
        occurrences=(
            Occurrence(range=(0, 0, 0), symbol="A"),
            Occurrence(range=(1, 0, 0), symbol="B"),
        ),
        symbols={
            "A": SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A"),
            "B": SymbolInformation(symbol="B", kind=SymbolKind.Class, display_name="B"),
        },
    )
    doc2 = Document(
        relative_path="b.ts",
        language="typescript",
        occurrences=(Occurrence(range=(0, 0, 0), symbol="C"),),
        symbols={
            "C": SymbolInformation(symbol="C", kind=SymbolKind.Function, display_name="C"),
        },
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/")
    return Index(metadata=metadata, documents=(doc1, doc2))


def test_get_statistics(index_with_stats):
    stats = index_with_stats.get_statistics()

    assert stats["total_documents"] == 2
    assert stats["total_symbols"] == 3
    assert stats["total_occurrences"] == 3

    assert stats["language_distribution"]["python"] == 1
    assert stats["language_distribution"]["typescript"] == 1

    assert stats["kind_distribution"]["Function"] == 2
    assert stats["kind_distribution"]["Class"] == 1


def test_analyze_complexity(index_with_stats):
    # Mock definition range for Function A: line 0 to 10 (11 lines)
    # Mock definition range for Class B: line 1 to 5 (5 lines)
    # Mock definition range for Function C: line 0 to 0 (1 line)

    # We need to inject ranges into occurrences in index_with_stats fixture
    # But fixture is already defined. Let's modify occurrences in place or create new test data.

    # Let's create new data for clarity
    doc1 = Document(
        relative_path="a.py",
        language="python",
        occurrences=(
            Occurrence(
                range=(0, 0, 10, 0), symbol="A", symbol_roles=SymbolRole.Definition
            ),  # 11 lines
            Occurrence(
                range=(20, 0, 25, 0), symbol="B", symbol_roles=SymbolRole.Definition
            ),  # 6 lines
        ),
        symbols={
            "A": SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A"),
            "B": SymbolInformation(symbol="B", kind=SymbolKind.Class, display_name="B"),
        },
    )
    doc2 = Document(
        relative_path="b.py",
        language="python",
        occurrences=(
            Occurrence(
                range=(0, 0, 0, 0), symbol="C", symbol_roles=SymbolRole.Definition
            ),  # 1 line
        ),
        symbols={
            "C": SymbolInformation(symbol="C", kind=SymbolKind.Function, display_name="C"),
        },
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=(doc1, doc2))
    index.build_indexes()

    complexity = index.analyze_complexity()

    assert complexity["function_count"] == 2  # A and C
    assert complexity["class_count"] == 1  # B

    # A length: 10 - 0 + 1 = 11
    # C length: 0 - 0 + 1 = 1
    # Avg: (11 + 1) / 2 = 6.0
    assert complexity["avg_function_length"] == 6.0
    assert complexity["max_function_length"] == 11

    # Test filter by document
    comp_doc1 = index.analyze_complexity("a.py")
    assert comp_doc1["function_count"] == 1
    assert comp_doc1["avg_function_length"] == 11.0

    comp_doc2 = index.analyze_complexity("b.py")
    assert comp_doc2["function_count"] == 1
    assert comp_doc2["avg_function_length"] == 1.0


def test_find_hotspots():
    doc1 = Document(
        relative_path="a.py",
        language="python",
        occurrences=(
            Occurrence(range=(0, 0, 0, 0), symbol="A", symbol_roles=SymbolRole.Definition),
            Occurrence(range=(1, 0, 1, 0), symbol="B", symbol_roles=SymbolRole.Definition),
        ),
        symbols={
            "A": SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A"),
            "B": SymbolInformation(symbol="B", kind=SymbolKind.Function, display_name="B"),
        },
    )
    doc2 = Document(
        relative_path="b.py",
        language="python",
        occurrences=(
            Occurrence(range=(0, 0, 0, 0), symbol="A"),
            Occurrence(range=(1, 0, 1, 0), symbol="A"),
            Occurrence(range=(2, 0, 2, 0), symbol="B"),
        ),
        symbols={},
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=(doc1, doc2))
    index.build_indexes()

    hotspots = index.find_hotspots(n=2)
    assert len(hotspots) == 2
    assert hotspots[0] == ("A", 2)
    assert hotspots[1] == ("B", 1)


def test_find_dead_code():
    doc1 = Document(
        relative_path="a.py",
        language="python",
        occurrences=(
            Occurrence(range=(0, 0, 0, 0), symbol="Used", symbol_roles=SymbolRole.Definition),
            Occurrence(range=(1, 0, 1, 0), symbol="Unused", symbol_roles=SymbolRole.Definition),
            Occurrence(
                range=(2, 0, 2, 0), symbol="Excluded_main", symbol_roles=SymbolRole.Definition
            ),
        ),
        symbols={
            "Used": SymbolInformation(symbol="Used", kind=SymbolKind.Function, display_name="Used"),
            "Unused": SymbolInformation(
                symbol="Unused", kind=SymbolKind.Function, display_name="Unused"
            ),
            "Excluded_main": SymbolInformation(
                symbol="Excluded_main", kind=SymbolKind.Function, display_name="Excluded_main"
            ),
        },
    )
    doc2 = Document(
        relative_path="b.py",
        language="python",
        occurrences=(Occurrence(range=(0, 0, 0, 0), symbol="Used"),),
        symbols={},
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=(doc1, doc2))
    index.build_indexes()

    dead_code = index.find_dead_code()
    assert "Unused" in dead_code
    assert "Used" not in dead_code
    assert "Excluded_main" not in dead_code


def test_get_exported_symbols():
    doc1 = Document(
        relative_path="a.py",
        language="python",
        occurrences=(),
        symbols={
            "Public": SymbolInformation(
                symbol="Public", kind=SymbolKind.Function, display_name="Public"
            ),
            "_Private": SymbolInformation(
                symbol="_Private", kind=SymbolKind.Function, display_name="_Private"
            ),
            "local 1": SymbolInformation(
                symbol="local 1", kind=SymbolKind.Variable, display_name="local_var"
            ),
        },
    )
    metadata = Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=(doc1,))
    index.build_indexes()

    exported = index.get_exported_symbols()
    names = [info.display_name for info in exported]
    assert "Public" in names
    assert "_Private" not in names
    assert "local_var" not in names
