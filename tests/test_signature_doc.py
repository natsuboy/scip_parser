from scip_parser.core.parser import SCIPParser
from scip_parser.proto import scip_pb2


def test_parse_signature_documentation():
    """验证解析器能否正确解析 signature_documentation 字段"""
    # 1. 创建一个包含 signature_documentation 的 protobuf 对象
    pb_doc = scip_pb2.Document(relative_path="test.py", text="void foo()", language="python")

    pb_symbol_info = scip_pb2.SymbolInformation(
        symbol="test_symbol", documentation=["docs"], signature_documentation=pb_doc
    )

    pb_index = scip_pb2.Index(
        documents=[scip_pb2.Document(relative_path="test.py", symbols=[pb_symbol_info])]
    )

    # 2. 序列化并解析
    parser = SCIPParser()
    index = parser._convert_pb_to_index(pb_index)

    # 3. 验证结果
    assert len(index.documents) == 1
    doc = index.documents[0]
    assert "test_symbol" in doc.symbols

    symbol_info = doc.symbols["test_symbol"]

    # 这里应该失败，因为 signature_documentation 尚未实现
    assert hasattr(symbol_info, "signature_documentation")
    assert symbol_info.signature_documentation is not None
    assert symbol_info.signature_documentation.text == "void foo()"
