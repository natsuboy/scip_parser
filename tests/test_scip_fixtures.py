"""
基于手工创建的 SCIP 文件的测试用例。

这些测试使用预先构造的测试数据，避免了用被测试的代码
获取"预期值"的循环验证问题。
"""

from __future__ import annotations

from scip_parser.core.types import (
    Index,
    SymbolKind,
    SymbolRole,
)
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


class TestSimpleSCIP:
    def test_index_basic_info(self, simple_test_index: Index):
        assert simple_test_index.metadata.tool_info.name == "scip-python"
        assert simple_test_index.metadata.project_root == "/test/project"
        assert len(simple_test_index.documents) == 4

    def test_find_definition(self, simple_test_index: Index):
        symbol = "python test-project main#main()."
        main_def = simple_test_index.find_definition(symbol)
        assert main_def is not None
        assert main_def.range == (0, 0, 10, 0)

    def test_find_references(self, simple_test_index: Index):
        logger_refs = simple_test_index.find_references("python test-project common#logger.")
        assert len(logger_refs) == 4
        assert all(occ.is_reference for occ in logger_refs)

        helper_refs = simple_test_index.find_references(
            "python test-project utils/helper#helper()."
        )
        assert len(helper_refs) == 1
        assert helper_refs[0] is not None
        assert "helper()" in helper_refs[0].symbol

    def test_symbol_info(self, simple_test_index: Index):
        main_info = simple_test_index.get_symbol_info("python test-project main#main().")
        assert main_info is not None
        assert main_info.display_name == "main"
        assert main_info.kind == SymbolKind.Function
        assert "Main function" in main_info.documentation

    def test_statistics(self, simple_test_index: Index):
        stats = simple_test_index.get_statistics()
        assert stats["total_documents"] == 4
        assert stats["total_symbols"] == 5
        assert stats["total_occurrences"] == 12

    def test_get_document(self, simple_test_index: Index):
        main_doc = simple_test_index.get_document("main.py")
        assert main_doc is not None
        assert main_doc.language == "python"

    def test_get_symbol_at(self, simple_test_index: Index):
        main_doc = simple_test_index.get_document("main.py")
        if main_doc:
            occ = main_doc.get_symbol_at(0, 2)
            if occ:
                assert "main" in occ.symbol

    def test_occurrence_roles(self, simple_test_index: Index):
        main_def = simple_test_index.find_definition("python test-project main#main().")
        assert main_def is not None
        assert main_def.is_definition is True

        logger_refs = simple_test_index.find_references("python test-project common#logger.")
        assert len(logger_refs) > 0
        assert logger_refs[0].is_reference is True


class TestHierarchySCIP:
    def test_find_implementations(self, hierarchy_test_index: Index):
        shape_impls = hierarchy_test_index.find_implementations("python test-project shapes/Shape#")
        assert len(shape_impls) == 2

    def test_find_subtypes(self, hierarchy_test_index: Index):
        shape_subtypes = hierarchy_test_index.find_subtypes("python test-project shapes/Shape#")
        assert len(shape_subtypes) == 2

    def test_find_supertypes(self, hierarchy_test_index: Index):
        circle_supertypes = hierarchy_test_index.find_supertypes(
            "python test-project shapes/Circle#"
        )
        assert len(circle_supertypes) == 1
        assert circle_supertypes[0] == "python test-project shapes/Shape#"

    def test_relationships(self, hierarchy_test_index: Index):
        circle_info = hierarchy_test_index.get_symbol_info("python test-project shapes/Circle#")
        assert circle_info is not None
        assert circle_info.relationships is not None
        assert len(circle_info.relationships) == 1
        rel = circle_info.relationships[0]
        assert rel.is_implementation is True


class TestQueryAPIWithFixtures:
    def test_by_language(self, simple_test_index: Index):
        python_results = QueryAPI(simple_test_index).by_language("python").execute()
        assert len(python_results) == 5
        go_results = QueryAPI(simple_test_index).by_language("go").execute()
        assert len(go_results) == 0

    def test_by_kind(self, simple_test_index: Index):
        func_results = QueryAPI(simple_test_index).by_kind(SymbolKind.Function).execute()
        assert len(func_results) == 2
        class_results = QueryAPI(simple_test_index).by_kind(SymbolKind.Class).execute()
        assert len(class_results) == 1

    def test_by_name_exact(self, simple_test_index: Index):
        main_results = QueryAPI(simple_test_index).by_name("main", exact=True).execute()
        assert len(main_results) == 1
        assert main_results[0].display_name == "main"

    def test_by_name_fuzzy(self, simple_test_index: Index):
        results = QueryAPI(simple_test_index).by_name("main", exact=False).execute()
        assert len(results) == 1

    def test_by_pattern(self, simple_test_index: Index):
        results = QueryAPI(simple_test_index).by_pattern("*main*").execute()
        assert len(results) == 1
        assert "main" in results[0].display_name.lower()

    def test_by_document(self, simple_test_index: Index):
        main_results = QueryAPI(simple_test_index).by_document("main.py").execute()
        assert len(main_results) == 1

    def test_by_document_list(self, simple_test_index: Index):
        results = QueryAPI(simple_test_index).by_document(["main.py", "utils.py"]).execute()
        assert len(results) == 2

    def test_has_documentation(self, simple_test_index: Index):
        with_doc = QueryAPI(simple_test_index).has_documentation().execute()
        assert len(with_doc) == 5

    def test_with_role(self, simple_test_index: Index):
        defs = QueryAPI(simple_test_index).with_role(SymbolRole.Definition).execute()
        assert len(defs) == 5

    def test_chaining(self, simple_test_index: Index):
        results = (
            QueryAPI(simple_test_index)
            .by_language("python")
            .by_document("main.py")
            .by_kind(SymbolKind.Function)
            .execute()
        )
        assert len(results) == 1
        assert results[0].display_name == "main"

    def test_count(self, simple_test_index: Index):
        api = QueryAPI(simple_test_index).by_document("main.py")
        assert api.count() == 1

    def test_first(self, simple_test_index: Index):
        api = QueryAPI(simple_test_index).by_language("python")
        res = api.first()
        assert res is not None
        assert res.display_name == "main"

    def test_exists(self, simple_test_index: Index):
        assert QueryAPI(simple_test_index).by_document("main.py").exists() is True
        assert QueryAPI(simple_test_index).by_document("nonexistent.py").exists() is False

    def test_group_by_kind(self, simple_test_index: Index):
        groups = QueryAPI(simple_test_index).group_by_kind()
        assert SymbolKind.Function in groups
        assert len(groups[SymbolKind.Function]) == 2
        assert SymbolKind.Class in groups
        assert len(groups[SymbolKind.Class]) == 1

    def test_group_by_document(self, simple_test_index: Index):
        groups = QueryAPI(simple_test_index).group_by_document()
        assert "main.py" in groups
        assert "utils.py" in groups
        assert len(groups["main.py"]) == 1

    def test_aggregate_stats(self, simple_test_index: Index):
        api = QueryAPI(simple_test_index).by_document("main.py")
        stats = api.aggregate_stats()
        assert stats["count"] == 1

    def test_find_hierarchy(self, hierarchy_test_index: Index):
        api = QueryAPI(hierarchy_test_index)
        hierarchy = api.find_hierarchy("python test-project shapes/Shape#", direction="both")
        assert len(hierarchy) == 2


class TestSymbolSearcherWithFixtures:
    def test_search(self, simple_test_index: Index):
        searcher = SymbolSearcher(simple_test_index)
        results = searcher.search("main")
        assert len(results) == 1
        assert results[0].display_name == "main"

    def test_fuzzy_search(self, simple_test_index: Index):
        searcher = SymbolSearcher(simple_test_index)
        results = searcher.fuzzy_search("helper", limit=5)
        assert len(results) >= 1

    def test_autocomplete(self, simple_test_index: Index):
        searcher = SymbolSearcher(simple_test_index)
        results = searcher.autocomplete("pro", limit=5)
        assert len(results) <= 5


class TestFiltersWithFixtures:
    def test_language_filter(self, simple_test_index: Index):
        f = LanguageFilter("python")
        doc = simple_test_index.documents[0]
        sym = list(doc.symbols.values())[0]
        assert f.match(sym, doc, simple_test_index)

    def test_kind_filter(self, simple_test_index: Index):
        f = KindFilter(SymbolKind.Function)
        doc = simple_test_index.documents[0]
        sym = list(doc.symbols.values())[0]
        if sym.kind == SymbolKind.Function:
            assert f.match(sym, doc, simple_test_index)

    def test_name_filter_exact(self, simple_test_index: Index):
        f = NameFilter("main", exact=True)
        doc = simple_test_index.documents[0]
        main_sym = [s for s in doc.symbols.values() if s.display_name == "main"][0]
        assert f.match(main_sym, doc, simple_test_index)

    def test_name_filter_fuzzy(self, simple_test_index: Index):
        f = NameFilter("in", exact=False)
        doc = simple_test_index.documents[0]
        main_sym = [s for s in doc.symbols.values() if s.display_name == "main"][0]
        assert f.match(main_sym, doc, simple_test_index)

    def test_pattern_filter(self, simple_test_index: Index):
        f = PatternFilter("*ain*")
        doc = simple_test_index.documents[0]
        main_sym = [s for s in doc.symbols.values() if s.display_name == "main"][0]
        assert f.match(main_sym, doc, simple_test_index)

    def test_document_filter(self, simple_test_index: Index):
        f = DocumentFilter("main.py")
        doc = simple_test_index.documents[0]
        sym = list(doc.symbols.values())[0]
        assert f.match(sym, doc, simple_test_index)

    def test_role_filter(self, simple_test_index: Index):
        f = RoleFilter(SymbolRole.Definition)
        doc = simple_test_index.documents[0]
        main_sym = [s for s in doc.symbols.values() if s.display_name == "main"][0]
        assert f.match(main_sym, doc, simple_test_index)

    def test_documentation_filter(self, simple_test_index: Index):
        doc = simple_test_index.get_document("main.py")
        assert doc is not None
        main_sym = [s for s in doc.symbols.values() if s.display_name == "main"][0]
        f_has = DocumentationFilter(has_doc=True)
        assert f_has.match(main_sym, doc, simple_test_index)

        f_not = DocumentationFilter(has_doc=False)
        utils_doc = simple_test_index.get_document("utils.py")
        assert utils_doc is not None
        helper_sym = [s for s in utils_doc.symbols.values() if s.display_name == "helper"][0]
        assert not f_not.match(helper_sym, utils_doc, simple_test_index)
