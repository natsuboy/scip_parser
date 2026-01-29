"""
Tests for DependencyGraphBuilder.
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
from scip_parser.graph.dependency_graph import DependencyGraphBuilder


@pytest.fixture
def mock_index():
    # File A imports File B
    # A has symbol "A" (Def)
    # A has reference to "B" (Import role)
    # B has symbol "B" (Def)

    doc_A = Document(
        relative_path="a.py",
        language="python",
        occurrences=[
            Occurrence(range=[0, 0, 0, 0], symbol="A", symbol_roles=SymbolRole.Definition),
            Occurrence(range=[1, 0, 1, 0], symbol="B", symbol_roles=SymbolRole.Import),  # Import B
        ],
        symbols={"A": SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A")},
    )

    doc_B = Document(
        relative_path="b.py",
        language="python",
        occurrences=[
            Occurrence(range=[0, 0, 0, 0], symbol="B", symbol_roles=SymbolRole.Definition)
        ],
        symbols={"B": SymbolInformation(symbol="B", kind=SymbolKind.Function, display_name="B")},
    )

    doc_C = Document(relative_path="c.py", language="python", occurrences=[], symbols={})

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc_A, doc_B, doc_C])
    index.build_indexes()
    return index


def test_build_dependency_graph(mock_index):
    builder = DependencyGraphBuilder(mock_index)
    graph = builder.build()

    # Nodes are documents (paths)
    assert "a.py" in graph.nodes
    assert "b.py" in graph.nodes
    assert "c.py" in graph.nodes

    # A imports B -> A depends on B. Edge A -> B.
    assert graph.has_edge("a.py", "b.py")


def test_get_dependencies(mock_index):
    builder = DependencyGraphBuilder(mock_index)
    builder.build()

    deps = builder.get_dependencies("a.py")
    assert deps == ["b.py"]

    rev_deps = builder.get_dependencies("b.py", reverse=True)  # dependants
    assert rev_deps == ["a.py"]


def test_find_cycles(mock_index):
    builder = DependencyGraphBuilder(mock_index)
    builder.build()

    # No cycles yet
    cycles = builder.find_cycles()
    assert len(cycles) == 0

    # Add cycle: B imports A
    # We can modify graph directly for test or update fixture.
    builder.graph.add_edge("b.py", "a.py")

    cycles = builder.find_cycles()
    assert len(cycles) > 0
    # Cycles can be returned in any rotation
    cycle_set = set(cycles[0])
    assert "a.py" in cycle_set
    assert "b.py" in cycle_set


def test_compute_stability_metrics(mock_index):
    builder = DependencyGraphBuilder(mock_index)
    builder.build()

    metrics = builder.compute_stability_metrics()
    # Instability I = Ce / (Ca + Ce)
    # Ca: Afferent (incoming) - who depends on me
    # Ce: Efferent (outgoing) - who I depend on

    # a.py: Depends on b.py (Ce=1). Incoming=0 (Ca=0).
    # I = 1 / (0 + 1) = 1.0 (Unstable)

    # b.py: Depends on 0 (Ce=0). Incoming=1 (Ca=1).
    # I = 0 / (1 + 0) = 0.0 (Stable)

    assert metrics["a.py"]["instability"] == 1.0
    assert metrics["b.py"]["instability"] == 0.0
