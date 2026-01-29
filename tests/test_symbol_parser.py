"""测试 SymbolParser 状态机解析能力"""

from scip_parser.core.types import Descriptor, SymbolKind
from scip_parser.utils.symbol import SymbolParser


class TestSymbolParserBasic:
    """基础解析测试"""

    def test_parse_simple_namespace(self):
        """测试简单命名空间符号"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 main/")
        assert result is not None
        assert result.package is not None
        assert result.scheme == "scip-go"
        assert result.package.manager == "gomod"
        assert result.package.name == "pkg"
        assert result.package.version == "1.0"
        assert len(result.descriptors) == 1
        assert result.descriptors[0].name == "main"
        assert result.descriptors[0].suffix == Descriptor.NAMESPACE

    def test_parse_type_and_method(self):
        """测试类型和方法符号"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 Foo#bar().")
        assert result is not None
        assert len(result.descriptors) == 2
        assert result.descriptors[0].name == "Foo"
        assert result.descriptors[0].suffix == Descriptor.TYPE
        assert result.descriptors[1].name == "bar"
        assert result.descriptors[1].suffix == Descriptor.METHOD

    def test_parse_method_with_disambiguator(self):
        """测试带消歧义符的方法"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 Foo#bar(+1).")
        assert result is not None
        assert len(result.descriptors) == 2
        assert result.descriptors[1].name == "bar"
        assert result.descriptors[1].disambiguator == "+1"
        assert result.descriptors[1].suffix == Descriptor.METHOD

    def test_parse_local_symbol(self):
        """测试局部符号"""
        result = SymbolParser.parse("local 42")
        assert result is not None
        assert result.scheme == "local"
        assert len(result.descriptors) == 1
        assert result.descriptors[0].name == "42"
        assert result.descriptors[0].suffix == Descriptor.LOCAL


class TestSymbolParserEscaping:
    """转义解析测试"""

    def test_parse_double_space_in_scheme(self):
        """测试 scheme 中的双空格转义"""
        result = SymbolParser.parse("my  scheme pip pkg 1.0 main/")
        assert result is not None
        assert result.scheme == "my scheme"

    def test_parse_double_space_in_package_name(self):
        """测试 package name 中的双空格转义"""
        result = SymbolParser.parse("scip-go gomod my  pkg 1.0 main/")
        assert result is not None
        assert result.package is not None
        assert result.package.name == "my pkg"

    def test_parse_backtick_escaped_identifier(self):
        """测试反引号转义的标识符"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 `path/to/file`/")
        assert result is not None
        assert len(result.descriptors) == 1
        assert result.descriptors[0].name == "path/to/file"
        assert result.descriptors[0].suffix == Descriptor.NAMESPACE

    def test_parse_backtick_with_double_backtick(self):
        """测试反引号内的双反引号转义"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 `contains``backtick`.")
        assert result is not None
        assert result.descriptors[0].name == "contains`backtick"
        assert result.descriptors[0].suffix == Descriptor.TERM


class TestSymbolParserComplex:
    """复杂符号解析测试"""

    def test_parse_nested_descriptors(self):
        """测试嵌套描述符"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 outer/Inner#method().(self)[T]")
        assert result is not None
        assert len(result.descriptors) == 5
        assert result.descriptors[0].name == "outer"
        assert result.descriptors[0].suffix == Descriptor.NAMESPACE
        assert result.descriptors[1].name == "Inner"
        assert result.descriptors[1].suffix == Descriptor.TYPE
        assert result.descriptors[2].name == "method"
        assert result.descriptors[2].suffix == Descriptor.METHOD
        assert result.descriptors[3].name == "self"
        assert result.descriptors[3].suffix == Descriptor.PARAMETER
        assert result.descriptors[4].name == "T"
        assert result.descriptors[4].suffix == Descriptor.TYPE_PARAMETER

    def test_parse_term_vs_method_priority(self):
        """测试 Method 优先于 Term 的解析"""
        # "foo()." 应该解析为 Method，不是 Term
        result = SymbolParser.parse("scip-go gomod pkg 1.0 foo().")
        assert result is not None
        assert len(result.descriptors) == 1
        assert result.descriptors[0].suffix == Descriptor.METHOD

    def test_parse_real_go_symbol(self):
        """测试真实的 Go 符号"""
        result = SymbolParser.parse(
            "scip-go gomod goods-manager-svc 1.16.9 `goods-manager-svc/internal/app/api`/Base#"
        )
        assert result is not None
        assert result.package is not None
        assert result.package.name == "goods-manager-svc"
        assert len(result.descriptors) == 2
        assert result.descriptors[0].name == "goods-manager-svc/internal/app/api"
        assert result.descriptors[1].name == "Base"


class TestSymbolParserFormat:
    """格式化测试"""

    def test_format_simple_symbol(self):
        """测试简单符号格式化"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 main/")
        assert result is not None
        formatted = SymbolParser.format(result)
        assert formatted == "scip-go gomod pkg 1.0 main/"

    def test_format_method_with_disambiguator(self):
        """测试带消歧义符的方法格式化"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 Foo#bar(+1).")
        assert result is not None
        formatted = SymbolParser.format(result)
        # 正确格式应该是 "bar(+1)." 而不是 "bar(+1)()."
        assert "bar(+1)." in formatted
        assert "bar(+1)()." not in formatted

    def test_format_local_symbol(self):
        """测试局部符号格式化"""
        result = SymbolParser.parse("local 42")
        assert result is not None
        formatted = SymbolParser.format(result)
        assert formatted == "local 42"


class TestSymbolParserInferMetadata:
    """元数据推断测试 (为 Task 2 预留)"""

    def test_infer_display_name_from_method(self):
        """测试从方法描述符推断显示名称"""
        result = SymbolParser.parse("scip-go gomod pkg 1.0 Foo#bar().")
        assert result is not None
        # 预期：infer_display_name 返回最后一个描述符的 name
        name, kind = SymbolParser.infer_metadata("scip-go gomod pkg 1.0 Foo#bar().")
        assert name == "bar"
        assert kind == SymbolKind.Method

    def test_infer_kind_from_type_suffix(self):
        """测试从类型后缀推断 SymbolKind"""
        name, kind = SymbolParser.infer_metadata("scip-go gomod pkg 1.0 Foo#")
        assert name == "Foo"
        # kind 应该映射到 Type
        assert kind == SymbolKind.Type

    def test_infer_kind_from_method_suffix(self):
        """测试从方法后缀推断 SymbolKind"""
        name, kind = SymbolParser.infer_metadata("scip-go gomod pkg 1.0 bar().")
        assert name == "bar"
        # kind 应该映射到 Method/Function
        assert kind == SymbolKind.Method
