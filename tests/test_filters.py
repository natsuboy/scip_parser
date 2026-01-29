"""
Tests for Filter System.
"""

import pytest

from scip_parser.core.types import SymbolInformation, SymbolKind
from scip_parser.query.filters import (
    AndFilter,
    KindFilter,
    NameFilter,
    NotFilter,
    OrFilter,
)


@pytest.fixture
def symbols():
    return [
        SymbolInformation(symbol="A", kind=SymbolKind.Function, display_name="A"),
        SymbolInformation(symbol="B", kind=SymbolKind.Class, display_name="B"),
        SymbolInformation(symbol="C", kind=SymbolKind.Function, display_name="C"),
    ]


def test_kind_filter(symbols):
    f = KindFilter(SymbolKind.Function)
    results = [s for s in symbols if f.match(s)]
    assert len(results) == 2
    assert results[0].display_name == "A"
    assert results[1].display_name == "C"


def test_name_filter(symbols):
    f = NameFilter("B")
    results = [s for s in symbols if f.match(s)]
    assert len(results) == 1
    assert results[0].display_name == "B"

    f2 = NameFilter("A", exact=False)
    # A matches. B no. C no.
    results = [s for s in symbols if f2.match(s)]
    assert len(results) == 1


def test_composite_filters(symbols):
    # (Kind=Function AND Name=A)
    f = AndFilter((KindFilter(SymbolKind.Function), NameFilter("A")))
    results = [s for s in symbols if f.match(s)]
    assert len(results) == 1
    assert results[0].display_name == "A"

    # (Kind=Class OR Name=C)
    f = OrFilter((KindFilter(SymbolKind.Class), NameFilter("C")))
    results = [s for s in symbols if f.match(s)]
    assert len(results) == 2  # B and C

    # NOT (Kind=Function)
    f = NotFilter(KindFilter(SymbolKind.Function))
    results = [s for s in symbols if f.match(s)]
    assert len(results) == 1  # B
