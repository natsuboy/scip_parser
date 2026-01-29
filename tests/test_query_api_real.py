"""Tests for QueryAPI using real SCIP index data."""

from scip_parser.core.types import SymbolKind
from scip_parser.query.api import QueryAPI


class TestQueryAPIWithRealIndex:
    """使用真实 SCIP 索引测试 QueryAPI 功能"""

    def test_by_language_go(self, real_index):
        """测试按语言过滤 - Go 项目应有大量符号"""
        results = QueryAPI(real_index).by_language("go").execute()
        assert len(results) > 1000

    def test_by_language_nonexistent(self, real_index):
        """测试按不存在的语言过滤"""
        results = QueryAPI(real_index).by_language("python").execute()
        assert len(results) == 0

    def test_by_document_specific_file(self, real_index):
        """测试按文档路径过滤"""
        results = QueryAPI(real_index).by_document("cmd/api/main.go").execute()
        assert len(results) == 4

    def test_by_document_nonexistent(self, real_index):
        """测试按不存在的文档过滤"""
        results = QueryAPI(real_index).by_document("nonexistent.go").execute()
        assert len(results) == 0

    def test_by_pattern_main(self, real_index):
        """测试按模式过滤 - 匹配 main 相关符号"""
        results = QueryAPI(real_index).by_pattern("*main*").execute()
        assert len(results) > 0

    def test_by_pattern_srv(self, real_index):
        """测试按模式过滤 - 匹配 srv 变量（Go 项目中常见变量名）"""
        results = QueryAPI(real_index).by_pattern("*srv*").execute()
        assert len(results) > 0

    def test_chaining_language_and_document(self, real_index):
        """测试链式过滤 - 语言 + 文档"""
        results = QueryAPI(real_index).by_language("go").by_document("cmd/api/main.go").execute()
        assert len(results) == 4

    def test_count_method(self, real_index):
        """测试 count 方法"""
        count = QueryAPI(real_index).by_document("cmd/api/main.go").count()
        assert count == 4

    def test_first_method(self, real_index):
        """测试 first 方法"""
        first = QueryAPI(real_index).by_document("cmd/api/main.go").first()
        assert first is not None
        assert first.symbol is not None

    def test_exists_method_true(self, real_index):
        """测试 exists 方法 - 存在"""
        exists = QueryAPI(real_index).by_document("cmd/api/main.go").exists()
        assert exists is True

    def test_exists_method_false(self, real_index):
        """测试 exists 方法 - 不存在"""
        exists = QueryAPI(real_index).by_document("nonexistent.go").exists()
        assert exists is False

    def test_by_kind_unspecified(self, real_index):
        """测试按类型过滤 - fallback 后大多是本地符号"""
        results = QueryAPI(real_index).by_kind(SymbolKind.Unspecified).execute()
        # fallback 逻辑会推断非本地符号的 kind，所以 Unspecified 主要应该是本地符号
        # 验证大部分是本地符号
        local_count = sum(1 for r in results if r.symbol.startswith("local "))
        assert local_count / len(results) > 0.9  # 90% 以上应该是本地符号

    def test_group_by_document(self, real_index):
        """测试按文档分组"""
        grouped = QueryAPI(real_index).by_pattern("*main*").group_by_document()
        assert len(grouped) > 0
        # 匹配 *main* 的符号可能在各种文件中，不一定在 main.go
        assert any("main" in k.lower() for k in grouped)

    def test_aggregate_stats(self, real_index):
        """测试聚合统计"""
        stats = QueryAPI(real_index).by_document("cmd/api/main.go").aggregate_stats()
        assert stats["count"] == 4
        assert "kind_distribution" in stats
