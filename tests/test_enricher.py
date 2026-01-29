"""
测试 SourceEnricher 框架
"""

from dataclasses import replace

from scip_parser.core.types import SymbolInformation, SymbolKind
from scip_parser.enrich.enricher import SourceEnricher
from scip_parser.enrich.provider import SourceProvider


class MockProvider(SourceProvider):
    def get_content(self, relative_path: str):
        if relative_path == "test.go":
            return "package main\n\n// @Title Test API\nfunc Test() {}"
        return None


class MockGoAdapter:
    def enrich(self, symbol: SymbolInformation, source_code: str) -> SymbolInformation:
        # 简单模拟：如果在源码中找到 @Title，添加到文档
        if "@Title Test API" in source_code:
            new_doc = list(symbol.documentation)
            new_doc.append("Title: Test API")
            return replace(symbol, documentation=new_doc)
        return symbol


def test_enricher_flow():
    provider = MockProvider()
    enricher = SourceEnricher(provider)
    enricher.register_adapter(".go", MockGoAdapter())

    symbol = SymbolInformation(
        symbol="scip-go gomod pkg 1.0 Test().",
        kind=SymbolKind.Function,
        display_name="Test",
        documentation=[],
    )

    # 测试成功补全
    enriched = enricher.enrich_symbol(symbol, "test.go")
    assert "Title: Test API" in enriched.documentation

    # 测试不支持的文件类型
    unchanged = enricher.enrich_symbol(symbol, "test.py")
    assert unchanged == symbol

    # 测试文件不存在
    unchanged_missing = enricher.enrich_symbol(symbol, "missing.go")
    assert unchanged_missing == symbol
