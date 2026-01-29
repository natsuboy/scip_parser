"""
SCIP Parser 基础使用示例

这个示例展示了如何使用 SCIP Parser 来解析 SCIP 文件并进行基本的查询操作。
"""

from scip_parser import SCIPParser
from scip_parser.core.types import SymbolRole, SyntaxKind
from scip_parser.utils.symbol import SymbolParser


def example_parse_scip_file():
    """示例: 解析 SCIP 文件"""
    print("=" * 60)
    print("示例 1: 解析 SCIP 文件")
    print("=" * 60)

    # 创建解析器
    _ = SCIPParser(enable_indexing=True)

    # 解析 SCIP 文件
    # 注意: 需要提供一个真实的 SCIP 文件
    # index = parser.parse_file("path/to/your/project.scip")
    print("\n提示: 使用 parser.parse_file('path/to/project.scip') 解析 SCIP 文件")
    print("解析器会自动构建内部索引以加速查询")

    # 也可以从字节流解析
    # with open("project.scip", "rb") as f:
    #     data = f.read()
    # index = parser.parse_bytes(data)
    print("\n或者使用 parser.parse_bytes(data) 从字节流解析")


def example_symbol_parser():
    """示例: 解析 SCIP 符号字符串"""
    print("\n" + "=" * 60)
    print("示例 2: 解析 SCIP 符号字符串")
    print("=" * 60)

    # 创建符号解析器
    parser = SymbolParser()

    # 解析全局符号
    symbol_str = "python myproject myproject 1.0 main#main()."
    parsed = parser.parse(symbol_str)

    if parsed:
        print(f"\n符号字符串: {symbol_str}")
        print(f"方案: {parsed.scheme}")
        print(f"包: {parsed.package}")
        print(f"描述符: {[str(d) for d in parsed.descriptors]}")
        print(f"完全限定名: {parsed.get_fully_qualified_name()}")

    # 解析局部符号
    local_symbol = "local myVariable"
    parsed_local = parser.parse(local_symbol)

    if parsed_local:
        print(f"\n局部符号: {local_symbol}")
        print(f"方案: {parsed_local.scheme}")
        print(f"名称: {parsed_local.descriptors[0].name}")


def example_occurrence_analysis():
    """示例: 分析符号出现位置"""
    print("\n" + "=" * 60)
    print("示例 3: 分析符号出现位置")
    print("=" * 60)

    from scip_parser.core.types import Occurrence

    # 创建一个定义类型的出现位置
    definition = Occurrence(
        range=[10, 4, 10, 20],  # 第10行,第4-20字符
        symbol="python myfile.py mymodule#MyClass.myMethod().",
        symbol_roles=SymbolRole.Definition,
        syntax_kind=SyntaxKind.IdentifierFunctionDefinition,
    )

    print(f"\n定义位置: 行 {definition.get_start_line()}, 列 {definition.get_start_char()}")
    print(f"符号: {definition.symbol}")
    print(f"是否为定义: {definition.is_definition}")
    kind_name = definition.syntax_kind.name if definition.syntax_kind else "Unspecified"
    print(f"语法类型: {kind_name}")

    # 创建一个引用类型的出现位置
    reference = Occurrence(
        range=[15, 8, 15, 18],
        symbol="python myfile.py mymodule#MyClass.myMethod().",
        symbol_roles=SymbolRole.ReadAccess,
        syntax_kind=SyntaxKind.IdentifierFunction,
    )

    print(f"\n引用位置: 行 {reference.get_start_line()}, 列 {reference.get_start_char()}")
    print(f"符号: {reference.symbol}")
    print(f"是否为定义: {reference.is_definition}")
    print(f"是否为读取访问: {reference.is_read_access}")


def example_data_structures():
    """示例: 使用 SCIP 数据结构"""
    print("\n" + "=" * 60)
    print("示例 4: 使用 SCIP 数据结构")
    print("=" * 60)

    from scip_parser.core.types import (
        Descriptor,
        Document,
        Index,
        Metadata,
        Package,
        Symbol,
        SymbolInformation,
        SymbolKind,
        ToolInfo,
    )

    # 创建包信息
    package = Package(manager="npm", name="react", version="18.0.0")
    print(f"\n包信息: {package}")

    # 创建描述符
    descriptors = [
        Descriptor(name="App", suffix=Descriptor.TYPE),
        Descriptor(name="render", suffix=Descriptor.METHOD),
    ]
    print(f"\n描述符: {[str(d) for d in descriptors]}")

    # 创建符号
    symbol = Symbol(
        scheme="typescript",
        package=package,
        descriptors=descriptors,
    )
    print(f"\n符号: {symbol}")
    print(f"完全限定名: {symbol.get_fully_qualified_name()}")

    # 创建符号信息
    sym_info = SymbolInformation(
        symbol=str(symbol),
        kind=SymbolKind.Method,
        display_name="render",
        documentation=["Render method", "Returns React element"],
    )
    print(f"\n符号信息: {sym_info.display_name} ({sym_info.kind.name})")

    # 创建文档
    document = Document(
        relative_path="src/App.tsx",
        language="typescript",
        occurrences=[],
        symbols={str(symbol): sym_info},
    )
    print(f"\n文档: {document.relative_path} ({document.language})")

    # 创建元数据
    tool_info = ToolInfo(name="scip-typescript", version="0.4.0")
    metadata = Metadata(
        version=0,
        tool_info=tool_info,
        project_root="/path/to/project",
    )
    print(f"\n元数据: 生成工具 {metadata.tool_info.name} v{metadata.tool_info.version}")

    # 创建索引
    index = Index(
        metadata=metadata,
        documents=[document],
    )
    print(f"\n索引: 包含 {len(index.documents)} 个文档")

    # 构建内部索引
    index.build_indexes()
    print(f"内部索引: 已索引 {len(index.list_symbols())} 个符号")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("SCIP Parser 使用示例")
    print("=" * 60)

    example_parse_scip_file()
    example_symbol_parser()
    example_occurrence_analysis()
    example_data_structures()

    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
