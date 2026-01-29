"""
全局测试 Fixture 配置

此模块提供共享的 pytest fixture，用于在测试中复用真实的 SCIP 索引数据。
使用 session 级别作用域以避免每个测试都重新加载大型 SCIP 文件。
"""

import pytest

from scip_parser.core.parser import SCIPParser
from scip_parser.core.types import Index


@pytest.fixture(scope="session")
def real_index() -> Index:
    """加载真实的 SCIP 索引文件

    使用 goods-manager-svc.scip 文件（Go 项目）作为测试数据源。
    该文件包含约 1492 个文档和 12.3 万个符号。

    Returns:
        Index: 已构建索引的 SCIP Index 对象
    """
    parser = SCIPParser()
    index = parser.parse_file("tests/index.scip")
    return index


@pytest.fixture(scope="session")
def simple_test_index() -> Index:
    """加载手工创建的简单测试索引

    包含基本的符号、定义和引用。

    Returns:
        Index: 简单测试 SCIP Index 对象
    """
    parser = SCIPParser()
    return parser.parse_file("tests/fixtures/test_simple.scip")


@pytest.fixture(scope="session")
def hierarchy_test_index() -> Index:
    """加载层次结构测试索引

    包含接口实现和继承关系。

    Returns:
        Index: 层次结构测试 SCIP Index 对象
    """
    parser = SCIPParser()
    return parser.parse_file("tests/fixtures/test_hierarchy.scip")


@pytest.fixture(scope="session")
def call_graph_test_index() -> Index:
    """加载调用图测试索引

    包含函数调用关系。

    Returns:
        Index: 调用图测试 SCIP Index 对象
    """
    parser = SCIPParser()
    return parser.parse_file("tests/fixtures/test_call_graph.scip")
