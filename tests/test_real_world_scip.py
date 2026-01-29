from __future__ import annotations

from scip_parser.core.types import Descriptor, Index, SymbolKind, SymbolRole
from scip_parser.query.api import QueryAPI
from scip_parser.query.filters import (
    DocumentationFilter,
    DocumentFilter,
    KindFilter,
    LanguageFilter,
    NameFilter,
    PatternFilter,
    RoleFilter,
)
from scip_parser.query.search import SymbolSearcher


class TestGoodsManagerSCIP:
    def test_index_basic_stats(self, real_index: Index):
        stats = real_index.get_statistics()
        assert stats["total_documents"] == 1496
        assert stats["total_symbols"] > 50000
        assert stats["language_distribution"]["go"] == 1496
        assert "kind_distribution" in stats

    def test_query_api_all_methods(self, real_index: Index):
        api = QueryAPI(real_index)

        api.by_language("go")
        api.by_kind(SymbolKind.Unspecified)
        api.by_name("main", exact=False)
        api.by_pattern("main*")
        api.by_document("cmd/api/main.go")
        api.has_documentation()
        api.is_exported()
        api.with_role(SymbolRole.Definition)

        results = api.execute()
        assert isinstance(results, list)

        assert api.count() == len(results)
        assert api.first() == (results[0] if results else None)

        api.find_references("some-sym")
        api.find_implementations("some-sym")
        api.find_hierarchy("some-sym")

        api.group_by_kind()
        api.group_by_document()
        api.aggregate_stats()

    def test_find_definition_and_references(self, real_index: Index):
        symbol = "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/internal/app/domain/entity/distribution`/Distributor#Id."

        defn = real_index.find_definition(symbol)
        assert defn is not None
        assert defn.is_definition

        refs = real_index.find_references(symbol)
        assert isinstance(refs, list)

    def test_implementations_and_hierarchy(self, real_index: Index):
        target = "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/internal/app/api/open/stock`/goodsSalesStatsController#"
        impls = real_index.find_implementations(target)
        assert isinstance(impls, list)

        supertypes = real_index.find_supertypes(target)
        assert isinstance(supertypes, list)

        subtypes = real_index.find_subtypes(target)
        assert isinstance(subtypes, list)

    def test_call_graph_features(self, real_index: Index):
        symbol = "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/cmd/api`/main()."
        callees = real_index.find_callees(symbol)
        assert isinstance(callees, list)

        callers = real_index.find_callers(symbol)
        assert isinstance(callers, list)

        if callees:
            path = real_index.get_call_path(symbol, callees[0])
            if path:
                assert path[0] == symbol

    def test_filters_direct(self, real_index: Index):
        doc = real_index.documents[0]
        sym = doc.symbols[list(doc.symbols.keys())[0]]

        assert LanguageFilter("go").match(sym, doc, real_index)
        assert KindFilter(sym.kind).match(sym, doc, real_index)
        assert NameFilter(sym.display_name).match(sym, doc, real_index)
        assert PatternFilter("*").match(sym, doc, real_index)
        assert DocumentFilter(doc.relative_path).match(sym, doc, real_index)
        assert RoleFilter(SymbolRole.Definition).match(sym, doc, real_index)
        assert DocumentationFilter(has_doc=False).match(
            sym, doc, real_index
        ) or DocumentationFilter(has_doc=True).match(sym, doc, real_index)

    def test_symbol_searcher(self, real_index: Index):
        searcher = SymbolSearcher(real_index)
        fuzzy_results = searcher.fuzzy_search("Distributor", limit=5)
        assert len(fuzzy_results) > 0
        ac_results = searcher.autocomplete("get", limit=10)
        assert len(ac_results) <= 10

    def test_complexity_and_hotspots(self, real_index: Index):
        complexity = real_index.analyze_complexity()
        assert complexity["function_count"] >= 0
        hotspots = real_index.find_hotspots(n=5)
        assert len(hotspots) == 5

    def test_dead_code_and_exported_symbols(self, real_index: Index):
        exported = real_index.get_exported_symbols()
        assert len(exported) > 0

    def test_query_api_stats_and_existence(self, real_index: Index):
        api = QueryAPI(real_index).by_document("cmd/api/main.go")
        assert api.exists() is True
        assert api.count() > 0

    def test_get_symbols_at_line(self, real_index: Index):
        symbols = real_index.get_symbols_at_line("cmd/api/main.go", 0)
        assert isinstance(symbols, list)

        doc = real_index.get_document("cmd/api/main.go")
        if doc and doc.occurrences:
            occ = doc.occurrences[0]
            found = doc.get_symbol_at(occ.range[0], occ.range[1])
            assert found is not None

    def test_descriptor_suffixes(self):
        d1 = Descriptor("name", suffix=Descriptor.NAMESPACE)
        assert d1.get_suffix_char() == "/"

        d2 = Descriptor("name", suffix=Descriptor.TYPE)
        assert d2.get_suffix_char() == "#"

        d3 = Descriptor("name", suffix=Descriptor.TERM)
        assert d3.get_suffix_char() == "."

        d4 = Descriptor("name", suffix=Descriptor.METHOD)
        assert d4.get_suffix_char() == "()."

        d_param = Descriptor("name", suffix=Descriptor.PARAMETER)
        assert d_param.get_suffix_char() == "()"

        d_tparam = Descriptor("name", suffix=Descriptor.TYPE_PARAMETER)
        assert d_tparam.get_suffix_char() == "[]"

        d_meta = Descriptor("name", suffix=Descriptor.META)
        assert d_meta.get_suffix_char() == ":"

        d_macro = Descriptor("name", suffix=Descriptor.MACRO)
        assert d_macro.get_suffix_char() == "!"

        d_local = Descriptor("name", suffix=Descriptor.LOCAL)
        assert d_local.get_suffix_char() == ""

    def test_symbol_information_relationships(self, real_index: Index):
        from scip_parser.core.types import Relationship, SymbolInformation

        info = SymbolInformation(
            "test",
            SymbolKind.Function,
            "test",
            relationships=[
                Relationship("ref", is_reference=True),
                Relationship("impl", is_implementation=True),
                Relationship("type", is_type_definition=True),
                Relationship("defn", is_definition=True),
            ],
        )
        assert "ref" in info.get_relationships("reference")
        assert "impl" in info.get_relationships("implementation")
        assert "type" in info.get_relationships("type_definition")
        assert "defn" in info.get_relationships("definition")

    def test_occurrence_properties(self):
        from scip_parser.core.types import Occurrence, SymbolRole

        occ = Occurrence(
            [1, 1, 1, 5], "sym", symbol_roles=SymbolRole.Definition | SymbolRole.WriteAccess
        )
        assert occ.is_definition is True
        assert occ.is_reference is False
        assert occ.is_write_access is True
        assert occ.is_read_access is False

        occ2 = Occurrence(
            [1, 1, 1, 5],
            "sym",
            symbol_roles=SymbolRole.Import | SymbolRole.Test | SymbolRole.Generated,
        )
        assert occ2.is_import is True
        assert occ2.is_test is True
        assert occ2.is_generated is True

        assert occ.get_start_line() == 1

    def test_index_more_methods(self, real_index: Index):
        symbols = real_index.list_symbols()
        assert len(symbols) > 0

        intfaces = real_index.get_definitions_by_kinds([SymbolKind.Interface])
        assert isinstance(intfaces, list)
        assert len(intfaces) > 0

        real_index.get_functions()
        real_index.get_methods()
        real_index.get_classes()
        real_index.get_interfaces()
        real_index.get_definitions_by_language("go")

        real_index.find_symbols_by_name("main")
        real_index.find_symbols_by_pattern("*main*")
