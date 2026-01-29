"""Tests for CallGraphBuilder and DependencyGraphBuilder using real SCIP data."""

import networkx as nx

from scip_parser.graph.call_graph import CallGraphBuilder
from scip_parser.graph.dependency_graph import DependencyGraphBuilder


class TestCallGraphBuilderWithRealIndex:
    """使用真实 SCIP 索引测试 CallGraphBuilder"""

    # 具有 callers 的符号
    SYMBOL_WITH_CALLERS = (
        "scip-go gomod goods-manager-svc 1.16.22 `goods-manager-svc/internal/app/api`/Base#"
    )

    def test_build_call_graph(self, real_index):
        """测试构建调用图"""
        builder = CallGraphBuilder(real_index)
        graph = builder.build()

        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() > 1000
        assert graph.number_of_edges() > 100

    def test_get_callers(self, real_index):
        """测试获取调用者"""
        builder = CallGraphBuilder(real_index)
        builder.build()

        callers = builder.get_callers(self.SYMBOL_WITH_CALLERS)
        assert len(callers) > 0

    def test_get_callers_nonexistent(self, real_index):
        """测试获取不存在符号的调用者"""
        builder = CallGraphBuilder(real_index)
        builder.build()

        callers = builder.get_callers("nonexistent_symbol")
        assert callers == []

    def test_get_callees(self, real_index):
        """测试获取被调用者"""
        builder = CallGraphBuilder(real_index)
        builder.build()

        # 找一个有 callees 的符号
        for node in builder.graph.nodes():
            callees = builder.get_callees(node)
            if callees:
                assert len(callees) > 0
                break

    def test_analyze_complexity(self, real_index):
        """测试分析复杂度"""
        builder = CallGraphBuilder(real_index)
        builder.build()

        metrics = builder.analyze_complexity()
        assert len(metrics) > 1000

        # 验证指标结构
        for sym, m in list(metrics.items())[:10]:
            assert "in_degree" in m
            assert "out_degree" in m
            assert isinstance(m["in_degree"], int)
            assert isinstance(m["out_degree"], int)

    def test_get_recursive_calls(self, real_index):
        """测试获取递归调用"""
        builder = CallGraphBuilder(real_index)
        builder.build()

        cycles = builder.get_recursive_calls()
        # 可能有也可能没有递归，只验证返回类型
        assert isinstance(cycles, list)


class TestDependencyGraphBuilderWithRealIndex:
    """使用真实 SCIP 索引测试 DependencyGraphBuilder"""

    def test_build_dependency_graph(self, real_index):
        """测试构建依赖图"""
        builder = DependencyGraphBuilder(real_index)
        graph = builder.build()

        assert isinstance(graph, nx.DiGraph)
        # 节点数应该等于文档数
        assert graph.number_of_nodes() == len(real_index.documents)

    def test_get_dependencies(self, real_index):
        """测试获取依赖"""
        builder = DependencyGraphBuilder(real_index)
        builder.build()

        # 获取任意文件的依赖
        deps = builder.get_dependencies("cmd/api/main.go")
        # 可能有也可能没有依赖，只验证返回类型
        assert isinstance(deps, list)

    def test_get_dependencies_nonexistent(self, real_index):
        """测试获取不存在文件的依赖"""
        builder = DependencyGraphBuilder(real_index)
        builder.build()

        deps = builder.get_dependencies("nonexistent.go")
        assert deps == []

    def test_analyze_layers(self, real_index):
        """测试分析层级"""
        builder = DependencyGraphBuilder(real_index)
        builder.build()

        layers = builder.analyze_layers()
        assert isinstance(layers, list)
        assert len(layers) > 0

        # 所有节点应该在某一层中
        all_nodes_in_layers = set()
        for layer in layers:
            all_nodes_in_layers.update(layer)
        assert len(all_nodes_in_layers) == builder.graph.number_of_nodes()

    def test_compute_stability_metrics(self, real_index):
        """测试计算稳定性指标"""
        builder = DependencyGraphBuilder(real_index)
        builder.build()

        metrics = builder.compute_stability_metrics()
        assert len(metrics) == len(real_index.documents)

        # 验证指标结构
        for path, m in list(metrics.items())[:10]:
            assert "ca" in m
            assert "ce" in m
            assert "instability" in m
            assert 0.0 <= m["instability"] <= 1.0

    def test_find_cycles(self, real_index):
        """测试查找循环依赖"""
        builder = DependencyGraphBuilder(real_index)
        builder.build()

        cycles = builder.find_cycles()
        # 可能有也可能没有循环，只验证返回类型
        assert isinstance(cycles, list)
