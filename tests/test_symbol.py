"""
SCIP 符号解析工具单元测试
"""

import pytest

from scip_parser.core.types import Descriptor, Package
from scip_parser.utils.symbol import ParsedSymbol, SymbolParser


def test_parse_global_symbol():
    """测试解析全局符号"""
    symbol_str = "python pip mypackage 1.0.0 main/MyClass#my_method()."
    parsed = SymbolParser.parse(symbol_str)

    assert parsed is not None
    assert parsed.scheme == "python"
    assert parsed.package is not None
    assert parsed.package.manager == "pip"
    assert parsed.package.name == "mypackage"
    assert parsed.package.version == "1.0.0"

    assert len(parsed.descriptors) == 3
    assert parsed.descriptors[0].name == "main"
    assert parsed.descriptors[0].suffix == Descriptor.NAMESPACE
    assert parsed.descriptors[1].name == "MyClass"
    assert parsed.descriptors[1].suffix == Descriptor.TYPE
    assert parsed.descriptors[2].name == "my_method"
    assert parsed.descriptors[2].suffix == Descriptor.METHOD


def test_parse_local_symbol():
    """测试解析局部符号"""
    symbol_str = "local 123"
    parsed = SymbolParser.parse(symbol_str)

    assert parsed is not None
    assert parsed.scheme == "local"
    assert parsed.package is None
    assert len(parsed.descriptors) == 1
    assert parsed.descriptors[0].name == "123"
    assert parsed.descriptors[0].suffix == Descriptor.LOCAL


def test_format_symbol():
    """测试格式化符号"""
    pkg = Package(manager="pip", name="mypackage", version="1.0.0")
    descs = [
        Descriptor(name="main", suffix=Descriptor.NAMESPACE),
        Descriptor(name="MyClass", suffix=Descriptor.TYPE),
    ]
    sym = ParsedSymbol(scheme="python", package=pkg, descriptors=descs)

    formatted = SymbolParser.format(sym)
    assert formatted == "python pip mypackage 1.0.0 main/MyClass#"


def test_format_local_symbol():
    """测试格式化局部符号"""
    descs = [Descriptor(name="local_var", suffix=Descriptor.LOCAL)]
    sym = ParsedSymbol(scheme="local", descriptors=descs)

    formatted = SymbolParser.format(sym)
    assert formatted == "local local_var"


def test_get_fully_qualified_name():
    """测试获取完全限定名"""
    descs = [
        Descriptor(name="a", suffix=Descriptor.NAMESPACE),
        Descriptor(name="b", suffix=Descriptor.TYPE),
        Descriptor(name="c", suffix=Descriptor.TERM),
    ]
    sym = ParsedSymbol(scheme="test", descriptors=descs)
    assert sym.get_fully_qualified_name() == "a.b.c"


def test_get_parent_symbol():
    """测试获取父符号"""
    descs = [
        Descriptor(name="a", suffix=Descriptor.NAMESPACE),
        Descriptor(name="b", suffix=Descriptor.TYPE),
    ]
    sym = ParsedSymbol(scheme="test", descriptors=descs)
    parent = sym.get_parent_symbol()

    assert parent is not None
    assert len(parent.descriptors) == 1
    assert parent.descriptors[0].name == "a"

    # 只有一个描述符时没有父符号
    assert parent.get_parent_symbol() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
