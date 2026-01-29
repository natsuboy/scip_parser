"""Tests for Index relationship query methods using real SCIP data."""




class TestIndexRelationshipsWithRealIndex:
    """使用真实 SCIP 索引测试符号关系查询功能"""

    # 测试用的符号常量
    SYMBOL_WITH_REFS = "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/cmd/job`/run()."
    IMPLEMENTER_SYMBOL = (
        "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/internal/app/api`/Base#"
    )
    IMPLEMENTED_INTERFACE = (
        "scip-go gomod github.com/apache/thrift v0.13.0 "
        "`github.com/apache/thrift/lib/go/thrift`/TException#"
    )

    def test_find_definition_exists(self, real_index):
        """测试 find_definition - 符号有定义"""
        definition = real_index.find_definition(self.SYMBOL_WITH_REFS)
        assert definition is not None
        assert definition.is_definition

    def test_find_definition_nonexistent(self, real_index):
        """测试 find_definition - 符号不存在"""
        definition = real_index.find_definition("nonexistent_symbol")
        assert definition is None

    def test_find_references_exists(self, real_index):
        """测试 find_references - 符号有引用"""
        refs = real_index.find_references(self.SYMBOL_WITH_REFS)
        assert len(refs) >= 1
        for ref in refs:
            assert ref.is_reference

    def test_find_references_nonexistent(self, real_index):
        """测试 find_references - 符号不存在"""
        refs = real_index.find_references("nonexistent_symbol")
        assert len(refs) == 0

    def test_get_symbol_occurrences(self, real_index):
        """测试 get_symbol_occurrences - 获取所有出现"""
        occs = real_index.get_symbol_occurrences(self.SYMBOL_WITH_REFS)
        assert len(occs) >= 2
        defs = [o for o in occs if o.is_definition]
        refs = [o for o in occs if o.is_reference]
        assert len(defs) >= 1
        assert len(refs) >= 1

    def test_find_implementations(self, real_index):
        """测试 find_implementations - 查找接口实现"""
        impls = real_index.find_implementations(self.IMPLEMENTED_INTERFACE)
        assert len(impls) >= 1
        assert self.IMPLEMENTER_SYMBOL in impls

    def test_find_implementations_no_impl(self, real_index):
        """测试 find_implementations - 符号无实现"""
        impls = real_index.find_implementations(self.SYMBOL_WITH_REFS)
        assert len(impls) == 0

    def test_get_symbol_info(self, real_index):
        """测试 get_symbol_info - 获取符号信息"""
        info = real_index.get_symbol_info(self.IMPLEMENTER_SYMBOL)
        assert info is not None
        assert len(info.relationships) > 0

    def test_get_symbol_info_nonexistent(self, real_index):
        """测试 get_symbol_info - 符号不存在"""
        info = real_index.get_symbol_info("nonexistent_symbol")
        assert info is None

    def test_list_symbols(self, real_index):
        """测试 list_symbols - 获取所有符号"""
        symbols = real_index.list_symbols()
        assert len(symbols) > 10000

    def test_get_document(self, real_index):
        """测试 get_document - 获取文档"""
        doc = real_index.get_document("cmd/api/main.go")
        assert doc is not None
        assert doc.relative_path == "cmd/api/main.go"
        assert doc.language == "go"

    def test_get_document_nonexistent(self, real_index):
        """测试 get_document - 文档不存在"""
        doc = real_index.get_document("nonexistent.go")
        assert doc is None
