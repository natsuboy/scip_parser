"""
Tests for advanced inheritance scenarios in InheritanceGraphBuilder.
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
def complex_index():
    """
    Creates a complex inheritance structure:
    
    1. Deep Hierarchy: Root -> A -> B -> C
    2. Multiple Inheritance (Diamond): 
       Base
       /   \
      Left Right
       \\   /
       Bottom
    """
    symbols = {}

    # Deep Hierarchy
    symbols["Root"] = SymbolInformation(
        symbol="Root", kind=SymbolKind.Class, display_name="Root", relationships=[]
    )
    symbols["A"] = SymbolInformation(
        symbol="A",
        kind=SymbolKind.Class,
        display_name="A",
        relationships=[Relationship(symbol="Root", is_implementation=True)],
    )
    symbols["B"] = SymbolInformation(
        symbol="B",
        kind=SymbolKind.Class,
        display_name="B",
        relationships=[Relationship(symbol="A", is_implementation=True)],
    )
    symbols["C"] = SymbolInformation(
        symbol="C",
        kind=SymbolKind.Class,
        display_name="C",
        relationships=[Relationship(symbol="B", is_implementation=True)],
    )

    # Diamond Inheritance
    symbols["Base"] = SymbolInformation(
        symbol="Base", kind=SymbolKind.Class, display_name="Base", relationships=[]
    )
    symbols["Left"] = SymbolInformation(
        symbol="Left",
        kind=SymbolKind.Class,
        display_name="Left",
        relationships=[Relationship(symbol="Base", is_implementation=True)],
    )
    symbols["Right"] = SymbolInformation(
        symbol="Right",
        kind=SymbolKind.Class,
        display_name="Right",
        relationships=[Relationship(symbol="Base", is_implementation=True)],
    )
    symbols["Bottom"] = SymbolInformation(
        symbol="Bottom",
        kind=SymbolKind.Class,
        display_name="Bottom",
        relationships=[
            Relationship(symbol="Left", is_implementation=True),
            Relationship(symbol="Right", is_implementation=True),
        ],
    )

    doc = Document(
        relative_path="complex.py",
        language="python",
        occurrences=[],
        symbols=symbols,
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_get_ancestors_descendants(complex_index):
    builder = InheritanceGraphBuilder(complex_index)
    builder.build()

    # Test ancestors
    ancestors_c = builder.get_ancestors("C")
    assert set(ancestors_c) == {"B", "A", "Root"}

    ancestors_bottom = builder.get_ancestors("Bottom")
    assert set(ancestors_bottom) == {"Left", "Right", "Base"}

    # Test descendants
    descendants_root = builder.get_descendants("Root")
    assert set(descendants_root) == {"A", "B", "C"}

    descendants_base = builder.get_descendants("Base")
    assert set(descendants_base) == {"Left", "Right", "Bottom"}


def test_get_method_resolution_order(complex_index):
    builder = InheritanceGraphBuilder(complex_index)
    builder.build()

    # Linear MRO
    mro_c = builder.get_method_resolution_order("C")
    # Note: NetworkX BFS/DFS might affect order, but parent-child relationship is fixed
    # Standard MRO: C, B, A, Root
    assert mro_c[0] == "C"
    assert "B" in mro_c
    assert "A" in mro_c
    assert "Root" in mro_c
    # Ensure order logic (child before parent)
    assert mro_c.index("C") < mro_c.index("B")
    assert mro_c.index("B") < mro_c.index("A")
    assert mro_c.index("A") < mro_c.index("Root")

    # Diamond MRO
    mro_bottom = builder.get_method_resolution_order("Bottom")
    assert mro_bottom[0] == "Bottom"
    assert "Left" in mro_bottom
    assert "Right" in mro_bottom
    assert "Base" in mro_bottom
    # Base should be last (or after Left/Right)
    assert mro_bottom.index("Bottom") < mro_bottom.index("Base")


def test_find_diamond_inheritance(complex_index):
    builder = InheritanceGraphBuilder(complex_index)
    builder.build()

    diamonds = builder.find_diamond_inheritance()
    assert len(diamonds) > 0

    found = False
    for diamond in diamonds:
        if diamond["descendant"] == "Bottom" and diamond["base"] == "Base":
            found = True
            assert len(diamond["paths"]) >= 2

    assert found, "Diamond inheritance for Bottom->Base not found"


def test_analyze_depth(complex_index):
    builder = InheritanceGraphBuilder(complex_index)
    builder.build()

    # Test Linear Depth
    depth_c = builder.analyze_depth("C")
    assert depth_c["direct_depth"] == 1  # Only B
    assert depth_c["total_depth"] == 3  # Root -> A -> B -> C (depth 3)
    assert depth_c["class_count"] == 3  # B, A, Root

    depth_root = builder.analyze_depth("Root")
    assert depth_root["total_depth"] == 0

    # Test Diamond Depth
    depth_bottom = builder.analyze_depth("Bottom")
    assert depth_bottom["direct_depth"] == 2  # Left, Right
    # Path: Base -> Left -> Bottom (depth 2)
    assert depth_bottom["total_depth"] == 2
    assert depth_bottom["class_count"] == 3  # Left, Right, Base


def test_edge_cases():
    """Test empty index and missing symbols"""
    empty_index = Index(
        metadata=Metadata(version=1, tool_info=ToolInfo(name="t", version="1"), project_root="/"),
        documents=[],
    )
    builder = InheritanceGraphBuilder(empty_index)
    builder.build()

    assert builder.get_parents("Missing") == []
    assert builder.get_children("Missing") == []
    assert builder.get_ancestors("Missing") == []
    assert builder.analyze_depth("Missing")["total_depth"] == 0
