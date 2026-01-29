"""
Tests for Index hierarchy query methods.
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
def mock_index():
    # func_a calls func_b

    # func_a definition at lines 0-5
    func_a_def = Occurrence(
        range=[0, 0, 5, 0], symbol="func_a().", symbol_roles=SymbolRole.Definition
    )

    # func_b definition at lines 10-15
    func_b_def = Occurrence(
        range=[10, 0, 15, 0], symbol="func_b().", symbol_roles=SymbolRole.Definition
    )

    # call to func_b inside func_a (at line 2)
    # enclosing_range covers func_a definition
    func_b_ref = Occurrence(
        range=[2, 4, 2, 10],
        symbol="func_b().",
        symbol_roles=SymbolRole.ReadAccess,
        enclosing_range=[0, 0, 5, 0],
    )

    doc = Document(
        relative_path="main.py",
        language="python",
        occurrences=[func_a_def, func_b_ref, func_b_def],
        symbols={
            "func_a().": SymbolInformation(
                symbol="func_a().", kind=SymbolKind.Function, display_name="func_a"
            ),
            "func_b().": SymbolInformation(
                symbol="func_b().", kind=SymbolKind.Function, display_name="func_b"
            ),
        },
    )

    metadata = Metadata(version=1, tool_info=ToolInfo(name="test", version="1"), project_root="/")

    index = Index(metadata=metadata, documents=[doc])
    index.build_indexes()
    return index


def test_get_symbols_in_range(mock_index):
    syms = mock_index.get_symbols_in_range("main.py", 0, 5)
    # Should include func_a definition and func_b reference
    assert len(syms) == 2
    symbols = {s.symbol for s in syms}
    assert "func_a()." in symbols
    assert "func_b()." in symbols


def test_find_callees(mock_index):
    callees = mock_index.find_callees("func_a().")
    assert len(callees) == 1
    assert callees[0] == "func_b()."


def test_find_callers(mock_index):
    callers = mock_index.find_callers("func_b().")
    assert len(callers) == 1
    # Caller is func_a because func_b_ref is enclosed in func_a definition range
    # BUT, to identify "func_a()." as the caller symbol, find_callers needs to
    # look up the symbol at the enclosing range.
    # The doc has func_a_def at [0,0,5,0].
    # enclosing_range is [0,0,5,0].
    # So it should match.
    assert callers[0] == "func_a()."


def test_get_call_path(mock_index):
    path = mock_index.get_call_path("func_a().", "func_b().")
    assert path == ["func_a().", "func_b()."]
