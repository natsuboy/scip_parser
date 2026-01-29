"""
Tests for CallGraphBuilder.
"""

import networkx as nx
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
from scip_parser.graph.call_graph import CallGraphBuilder


@pytest.fixture
def mock_index():
    # A calls B, B calls C.
    # A definition
    def_A = Occurrence(range=[0, 0, 5, 0], symbol="A", symbol_roles=SymbolRole.Definition)
    # Ref to B inside A
    ref_B = Occurrence(
        range=[1, 0, 1, 5],
        symbol="B",
        symbol_roles=SymbolRole.ReadAccess,
        enclosing_range=[0, 0, 5, 0],
    )

    # B definition
    def_B = Occurrence(range=[10, 0, 15, 0], symbol="B", symbol_roles=SymbolRole.Definition)
    # Ref to C inside B
    ref_C = Occurrence(
        range=[11, 0, 11, 5],
        symbol="C",
        symbol_roles=SymbolRole.ReadAccess,
        enclosing_range=[10, 0, 15, 0],
    )

    # C definition
    def_C = Occurrence(range=[20, 0, 25, 0], symbol="C", symbol_roles=SymbolRole.Definition)

    doc = Document(
        relative_path="main.py",
        language="python",
        occurrences=[def_A, ref_B, def_B, ref_C, def_C],
        symbols={
            "A": SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A"),
            "B": SymbolInformation(symbol="B", kind=SymbolKind.Function, display_name="B"),
            "C": SymbolInformation(symbol="C", kind=SymbolKind.Function, display_name="C"),
        },
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_build_call_graph(mock_index):
    builder = CallGraphBuilder(mock_index)
    graph = builder.build()

    assert isinstance(graph, nx.DiGraph)
    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert "C" in graph.nodes

    assert graph.has_edge("A", "B")
    assert graph.has_edge("B", "C")
    assert not graph.has_edge("A", "C")  # Direct edge


def test_get_callers_callees(mock_index):
    builder = CallGraphBuilder(mock_index)
    builder.build()

    callees_A = builder.get_callees("A")
    assert callees_A == ["B"]

    callers_C = builder.get_callers("C")
    assert callers_C == ["B"]


def test_get_call_path(mock_index):
    builder = CallGraphBuilder(mock_index)
    builder.build()

    path = builder.get_call_path("A", "C")
    assert path == ["A", "B", "C"]


def test_analyze_complexity(mock_index):
    builder = CallGraphBuilder(mock_index)
    builder.build()

    metrics = builder.analyze_complexity()
    # A has out-degree 1
    assert metrics["A"]["out_degree"] == 1
    # B has out-degree 1
    assert metrics["B"]["out_degree"] == 1
    # C has out-degree 0
    assert metrics["C"]["out_degree"] == 0
