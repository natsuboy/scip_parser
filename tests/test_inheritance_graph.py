"""
Tests for InheritanceGraphBuilder.
"""

import pytest

from scip_parser.core.types import (
    Document,
    Index,
    Metadata,
    Relationship,
    SymbolInformation,
    SymbolKind,
    ToolInfo,
)
from scip_parser.graph.inheritance_graph import InheritanceGraphBuilder


@pytest.fixture
def mock_index():
    # Base class
    base_sym = SymbolInformation(
        symbol="Base", kind=SymbolKind.Class, display_name="Base", relationships=[]
    )

    # Interface
    interface_sym = SymbolInformation(symbol="I", kind=SymbolKind.Interface, display_name="I")

    # Base implements I
    base_sym.relationships.append(Relationship(symbol="I", is_implementation=True))

    # Child class inherits from Base
    child_sym = SymbolInformation(
        symbol="Child",
        kind=SymbolKind.Class,
        display_name="Child",
        relationships=[Relationship(symbol="Base", is_implementation=True)],  # Inheritance
    )

    # GrandChild inherits from Child
    grandchild_sym = SymbolInformation(
        symbol="GrandChild",
        kind=SymbolKind.Class,
        display_name="GrandChild",
        relationships=[Relationship(symbol="Child", is_implementation=True)],
    )

    doc = Document(
        relative_path="classes.py",
        language="python",
        occurrences=[],
        symbols={
            "Base": base_sym,
            "Child": child_sym,
            "GrandChild": grandchild_sym,
            "I": interface_sym,
        },
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_build_inheritance_graph(mock_index):
    builder = InheritanceGraphBuilder(mock_index)
    graph = builder.build()

    assert "Base" in graph.nodes
    assert "Child" in graph.nodes

    # Base -> Child (Parent -> Child edge for LCA)
    assert graph.has_edge("Base", "Child")
    assert graph.has_edge("Child", "GrandChild")
    assert graph.has_edge("I", "Base")


def test_get_parents_children(mock_index):
    builder = InheritanceGraphBuilder(mock_index)
    builder.build()

    parents = builder.get_parents("Child")
    assert parents == ["Base"]

    children = builder.get_children("Base")
    assert "Child" in children
    assert len(children) == 1

    assert builder.get_parents("Base") == ["I"]


def test_find_common_ancestor(mock_index):
    builder = InheritanceGraphBuilder(mock_index)
    builder.build()

    ancestor = builder.find_common_ancestor("Child", "GrandChild")
    assert ancestor == "Child"

    ancestor = builder.find_common_ancestor("Base", "GrandChild")
    assert ancestor == "Base"
