"""
性能基准测试
"""

import pytest

from scip_parser.core.parser import SCIPParser
from scip_parser.proto import scip_pb2
from scip_parser.query.api import QueryAPI


@pytest.fixture
def large_index_data():
    pb_index = scip_pb2.Index()
    # 创建 50 个文档，每个文档 100 个符号
    for i in range(50):
        doc = pb_index.documents.add()
        doc.relative_path = f"file_{i}.py"
        doc.language = "python"
        for j in range(100):
            sym_name = f"sym_{i}_{j}"
            occ = doc.occurrences.add()
            occ.range.extend([j, 0, j, 10])
            occ.symbol = sym_name
            occ.symbol_roles = scip_pb2.Definition

            sym_info = doc.symbols.add()
            sym_info.symbol = sym_name
            sym_info.display_name = sym_name
            sym_info.kind = scip_pb2.SymbolInformation.Function

    return pb_index.SerializeToString()


def test_benchmark_parse(benchmark, large_index_data):
    parser = SCIPParser()
    result = benchmark(parser.parse_bytes, large_index_data)
    assert len(result.documents) == 50


def test_benchmark_query(benchmark, large_index_data):
    parser = SCIPParser()
    index = parser.parse_bytes(large_index_data)
    api = QueryAPI(index)

    def run_query():
        return api.by_name("sym_25_50").execute()

    benchmark(run_query)


def test_benchmark_hotspots(benchmark, large_index_data):
    parser = SCIPParser()
    index = parser.parse_bytes(large_index_data)

    benchmark(index.find_hotspots, n=10)
