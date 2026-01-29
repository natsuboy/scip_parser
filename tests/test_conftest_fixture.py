"""测试 conftest.py 中的 real_index fixture 是否可用"""


def test_real_index_loads_successfully(real_index):
    """验证 real_index fixture 能正确加载 SCIP 文件"""
    assert real_index is not None
    assert len(real_index.documents) > 0


def test_real_index_has_symbols(real_index):
    """验证加载的索引包含符号数据"""
    assert len(real_index._symbol_index) > 0


def test_real_index_metadata(real_index):
    """验证元数据正确解析"""
    assert real_index.metadata.tool_info.name == "scip-go"
