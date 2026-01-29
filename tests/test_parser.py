"""
SCIP Parser 单元测试
"""

from unittest.mock import MagicMock, patch

import pytest

from scip_parser.core.parser import SCIPParser
from scip_parser.core.types import Index
from scip_parser.proto import scip_pb2


class TestSCIPParser:
    """测试 SCIPParser 类"""

    def test_parse_bytes_valid(self):
        """测试解析有效的 protobuf 字节流"""
        # 构造一个简单的 Index protobuf 消息
        pb_index = scip_pb2.Index()
        pb_index.metadata.version = 1
        pb_index.metadata.tool_info.name = "test-tool"
        pb_index.metadata.tool_info.version = "1.0.0"
        pb_index.metadata.project_root = "/test/root"

        doc = pb_index.documents.add()
        doc.relative_path = "test.py"
        doc.language = "python"

        data = pb_index.SerializeToString()

        # 解析
        parser = SCIPParser()
        index = parser.parse_bytes(data)

        # 验证
        assert isinstance(index, Index)
        assert index.metadata.tool_info.name == "test-tool"
        assert len(index.documents) == 1
        assert index.documents[0].relative_path == "test.py"

    def test_parse_bytes_invalid(self):
        """测试解析无效的字节流"""
        data = b"invalid-protobuf-data"
        parser = SCIPParser()

        with pytest.raises(ValueError, match="Failed to parse SCIP index"):
            parser.parse_bytes(data)

    def test_parse_file_normal(self):
        """测试解析普通文件"""
        with patch("builtins.open", create=True) as mock_open:
            # 模拟文件读取
            pb_index = scip_pb2.Index()
            pb_index.metadata.tool_info.name = "normal-file"
            mock_file = MagicMock()
            mock_file.read.return_value = pb_index.SerializeToString()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            parser = SCIPParser()
            index = parser.parse_file("test.scip")

            assert index.metadata.tool_info.name == "normal-file"
            mock_open.assert_called_once_with("test.scip", "rb")

    def test_parse_file_gz(self):
        """测试解析 gzip 文件"""
        with patch("gzip.open") as mock_gzip_open:
            # 模拟 gzip 文件读取
            pb_index = scip_pb2.Index()
            pb_index.metadata.tool_info.name = "gzip-file"
            mock_file = MagicMock()
            mock_file.read.return_value = pb_index.SerializeToString()
            mock_file.__enter__.return_value = mock_file
            mock_gzip_open.return_value = mock_file

            parser = SCIPParser()
            index = parser.parse_file("test.scip.gz")

            assert index.metadata.tool_info.name == "gzip-file"
            mock_gzip_open.assert_called_once_with("test.scip.gz", "rb")

    def test_enable_indexing(self):
        """测试索引构建开关"""
        # 构造包含符号的数据
        pb_index = scip_pb2.Index()
        doc = pb_index.documents.add()
        doc.relative_path = "test.py"
        occ = doc.occurrences.add()
        occ.symbol = "test_symbol"
        occ.range.extend([1, 1, 1, 5])

        data = pb_index.SerializeToString()

        # 1. 启用索引 (默认)
        parser_on = SCIPParser(enable_indexing=True)
        index_on = parser_on.parse_bytes(data)
        # 验证内部索引已构建
        assert "test_symbol" in index_on._symbol_index
        assert len(index_on.get_symbol_occurrences("test_symbol")) == 1

        # 2. 禁用索引
        parser_off = SCIPParser(enable_indexing=False)
        index_off = parser_off.parse_bytes(data)
        # 验证内部索引为空
        assert "test_symbol" not in index_off._symbol_index
        assert len(index_off.get_symbol_occurrences("test_symbol")) == 0

    def test_symbol_info_fallback_display_name(self):
        """测试 display_name 为空时的 fallback"""

        pb_index = scip_pb2.Index()
        pb_index.metadata.tool_info.name = "test-tool"
        doc = pb_index.documents.add()
        doc.relative_path = "test.py"

        sym = doc.symbols.add()
        sym.symbol = "python pip myproject 1.0.0 MyClass#"
        sym.kind = scip_pb2.SymbolInformation.Class
        # 不设置 display_name，测试 fallback

        data = pb_index.SerializeToString()
        parser = SCIPParser()
        index = parser.parse_bytes(data)

        sym_info = index.documents[0].symbols["python pip myproject 1.0.0 MyClass#"]
        assert sym_info.display_name == "MyClass"

    def test_symbol_info_fallback_kind(self):
        """测试 kind 为 Unspecified 时的 fallback"""
        from scip_parser.core.types import SymbolKind

        pb_index = scip_pb2.Index()
        pb_index.metadata.tool_info.name = "test-tool"
        doc = pb_index.documents.add()
        doc.relative_path = "test.py"

        sym = doc.symbols.add()
        sym.symbol = "python pip myproject 1.0.0 myFunction()."
        sym.kind = scip_pb2.SymbolInformation.UnspecifiedKind
        sym.display_name = "myFunction"

        data = pb_index.SerializeToString()
        parser = SCIPParser()
        index = parser.parse_bytes(data)

        sym_info = index.documents[0].symbols["python pip myproject 1.0.0 myFunction()."]
        assert sym_info.kind == SymbolKind.Method

    def test_symbol_info_no_fallback_for_local(self):
        """测试本地符号不应用 fallback"""
        from scip_parser.core.types import SymbolKind

        pb_index = scip_pb2.Index()
        pb_index.metadata.tool_info.name = "test-tool"
        doc = pb_index.documents.add()
        doc.relative_path = "test.py"

        sym = doc.symbols.add()
        sym.symbol = "local myLocalVar"
        sym.kind = scip_pb2.SymbolInformation.UnspecifiedKind
        # 不设置 display_name

        data = pb_index.SerializeToString()
        parser = SCIPParser()
        index = parser.parse_bytes(data)

        sym_info = index.documents[0].symbols["local myLocalVar"]
        assert sym_info.display_name == ""
        assert sym_info.kind == SymbolKind.Unspecified

    def test_symbol_info_existing_values_preserved(self):
        """测试已有值不受影响"""
        from scip_parser.core.types import SymbolKind

        pb_index = scip_pb2.Index()
        pb_index.metadata.tool_info.name = "test-tool"
        doc = pb_index.documents.add()
        doc.relative_path = "test.py"

        sym = doc.symbols.add()
        sym.symbol = "python pip myproject 1.0.0 MyClass#"
        sym.kind = scip_pb2.SymbolInformation.Class
        sym.display_name = "CustomDisplayName"

        data = pb_index.SerializeToString()
        parser = SCIPParser()
        index = parser.parse_bytes(data)

        sym_info = index.documents[0].symbols["python pip myproject 1.0.0 MyClass#"]
        assert sym_info.display_name == "CustomDisplayName"
        assert sym_info.kind == SymbolKind.Class


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
