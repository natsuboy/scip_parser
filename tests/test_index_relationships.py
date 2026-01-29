"""
Tests for Index relationship query methods.
"""

import pytest

from scip_parser.core.types import (
    Document,
    Index,
    Metadata,
    Occurrence,
    Relationship,
    SymbolInformation,
    SymbolKind,
    SymbolRole,
    ToolInfo,
)


@pytest.fixture
def mock_index():
    # Helper interface
    interface_sym = SymbolInformation(
        symbol="interface#", kind=SymbolKind.Interface, display_name="Interface"
    )

    # Implementation class
    impl_sym = SymbolInformation(
        symbol="impl#",
        kind=SymbolKind.Class,
        display_name="Impl",
        relationships=[Relationship(symbol="interface#", is_implementation=True)],
    )

    # Occurrences
    def_occ = Occurrence(
        range=[0, 0, 0, 0], symbol="interface#", symbol_roles=SymbolRole.Definition
    )

    ref_occ = Occurrence(
        range=[1, 0, 1, 0],
        symbol="interface#",
        symbol_roles=SymbolRole.ReadAccess,  # Reference
    )

    doc = Document(
        relative_path="test.py",
        language="python",
        occurrences=[def_occ, ref_occ],
        symbols={"interface#": interface_sym, "impl#": impl_sym},
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")
    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_find_references(mock_index):
    refs = mock_index.find_references("interface#")
    assert len(refs) == 1
    assert refs[0].is_reference
    assert not refs[0].is_definition


def test_find_definition(mock_index):
    defi = mock_index.find_definition("interface#")
    assert defi is not None
    assert defi.is_definition

    assert mock_index.find_definition("nonexistent") is None


def test_find_implementations(mock_index):
    impls = mock_index.find_implementations("interface#")
    assert len(impls) == 1
    assert impls[0] == "impl#"

    assert len(mock_index.find_implementations("impl#")) == 0
