"""
SCIP Parser 单元测试
"""

import pytest

from scip_parser.core.types import (
    Descriptor,
    Occurrence,
    Package,
    SymbolKind,
    SymbolRole,
    SyntaxKind,
)


def test_symbol_role_bitmask():
    """测试符号角色位掩码"""
    # 测试单个角色
    assert SymbolRole.Definition == 0x1
    assert SymbolRole.Import == 0x2
    assert SymbolRole.ReadAccess == 0x8

    # 测试角色组合
    role = SymbolRole.Definition | SymbolRole.Generated
    assert role & SymbolRole.Definition > 0
    assert role & SymbolRole.Generated > 0


def test_occurrence_properties():
    """测试 Occurrence 属性"""
    occ = Occurrence(
        range=(10, 5, 10, 15),
        symbol="test symbol",
        symbol_roles=SymbolRole.Definition,
    )

    assert occ.is_definition
    assert not occ.is_reference
    assert not occ.is_import
    assert occ.get_start_line() == 10
    assert occ.get_start_char() == 5
    assert occ.get_end_line() == 10
    assert occ.get_end_char() == 15


def test_occurrence_reference():
    """测试引用类型的 Occurrence"""
    occ = Occurrence(
        range=(5, 0, 5, 10),
        symbol="test symbol",
        symbol_roles=SymbolRole.ReadAccess,
    )

    assert not occ.is_definition
    assert occ.is_reference
    assert occ.is_read_access


def test_descriptor_suffix():
    """测试描述符后缀"""
    desc_type = Descriptor(name="MyClass", suffix=Descriptor.TYPE)
    assert desc_type.get_suffix_char() == "#"

    desc_method = Descriptor(name="myMethod", suffix=Descriptor.METHOD)
    assert desc_method.get_suffix_char() == "()."

    desc_namespace = Descriptor(name="mypackage", suffix=Descriptor.NAMESPACE)
    assert desc_namespace.get_suffix_char() == "/"


def test_package_string_format():
    """测试 Package 字符串格式化"""
    pkg = Package(manager="npm", name="react", version="18.0.0")
    assert str(pkg) == "npm react 18.0.0"


def test_syntax_kind_enum():
    """测试语法类型枚举"""
    assert SyntaxKind.Identifier.value == 6
    assert SyntaxKind.Keyword.value == 4
    assert SyntaxKind.StringLiteral.value == 27


def test_symbol_kind_enum():
    """测试符号类型枚举"""
    assert SymbolKind.Class.value == 7
    assert SymbolKind.Method.value == 26
    assert SymbolKind.Function.value == 17


def test_occurrence_three_element_range():
    """测试三元素范围格式"""
    occ = Occurrence(
        range=(10, 5, 15),  # [start_line, start_char, end_char]
        symbol="test",
    )

    assert occ.get_start_line() == 10
    assert occ.get_start_char() == 5
    assert occ.get_end_line() == 10  # 推断为与 start_line 相同
    assert occ.get_end_char() == 15


def test_symbol_role_combinations():
    """测试符号角色组合"""
    # Definition + Generated
    occ = Occurrence(
        range=(0, 0, 0, 0),
        symbol="test",
        symbol_roles=SymbolRole.Definition | SymbolRole.Generated,
    )

    assert occ.is_definition
    assert occ.is_generated
    assert not occ.is_test


def test_occurrence_with_all_roles():
    """测试包含所有角色的 Occurrence"""
    roles = (
        SymbolRole.Definition | SymbolRole.Import | SymbolRole.WriteAccess | SymbolRole.ReadAccess
    )

    occ = Occurrence(
        range=(0, 0, 0, 0),
        symbol="test",
        symbol_roles=roles,
    )

    assert occ.is_definition
    assert occ.is_import
    assert occ.is_write_access
    assert occ.is_read_access


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
