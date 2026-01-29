#!/usr/bin/env python3
"""
SCIP 符号定义查询工具

这个脚本演示了如何使用 src 库来查询 SCIP 文件中的所有符号定义。

用法:
    python examples/list_all_symbols.py <path-to-scip-file> [options]

示例:
    # 列出所有函数
    python examples/list_all_symbols.py project.scip --kind Function

    # 列出所有类和接口
    python examples/list_all_symbols.py project.scip --kind Class --kind Interface

    # 列出所有定义，按类型分组
    python examples/list_all_symbols.py project.scip --group-by-kind

    # 显示文档注释
    python examples/list_all_symbols.py project.scip --show-doc
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scip_parser import SCIPParser


def get_all_definitions(index):
    """获取索引中所有符号定义

    Args:
        index: SCIP Index 对象

    Returns:
        定义字典列表
    """
    definitions = []

    for document in index.documents:
        for symbol_str, symbol_info in document.symbols.items():
            definitions.append(
                {
                    "symbol": symbol_str,
                    "display_name": symbol_info.display_name,
                    "kind": symbol_info.kind,
                    "kind_name": symbol_info.kind.name,
                    "document": document.relative_path,
                    "language": document.language,
                    "documentation": symbol_info.documentation,
                    "relationships": symbol_info.relationships,
                }
            )

    return definitions


def filter_by_kinds(definitions, kind_names):
    """按符号类型过滤

    Args:
        definitions: 定义列表
        kind_names: SymbolKind 名称列表

    Returns:
        过滤后的定义列表
    """
    if not kind_names:
        return definitions

    kind_set = set(kind_names)
    return [d for d in definitions if d["kind_name"] in kind_set]


def filter_by_language(definitions, language):
    """按编程语言过滤

    Args:
        definitions: 定义列表
        language: 编程语言名称

    Returns:
        过滤后的定义列表
    """
    if not language:
        return definitions

    return [d for d in definitions if d["language"].lower() == language.lower()]


def group_by_kind(definitions):
    """按符号类型分组

    Args:
        definitions: 定义列表

    Returns:
        字典，key 为类型名，value 为定义列表
    """
    grouped = defaultdict(list)
    for d in definitions:
        grouped[d["kind_name"]].append(d)
    return dict(grouped)


def print_definitions(definitions, show_doc=False, show_symbol=False):
    """打印定义列表

    Args:
        definitions: 定义列表
        show_doc: 是否显示文档
        show_symbol: 是否显示完整符号字符串
    """
    for i, d in enumerate(definitions, 1):
        print(f"\n{i}. {d['display_name']}")
        print(f"   类型: {d['kind_name']}")
        print(f"   位置: {d['document']}")
        print(f"   语言: {d['language']}")

        if show_symbol:
            print(f"   符号: {d['symbol']}")

        if show_doc and d["documentation"]:
            doc_text = " ".join(d["documentation"])
            if len(doc_text) > 100:
                doc_text = doc_text[:97] + "..."
            print(f"   文档: {doc_text}")


def print_grouped_definitions(grouped, show_doc=False, show_symbol=False):
    """打印分组的定义

    Args:
        grouped: 分组后的定义字典
        show_doc: 是否显示文档
        show_symbol: 是否显示完整符号字符串
    """
    for kind_name in sorted(grouped.keys()):
        definitions = grouped[kind_name]
        print(f"\n{'=' * 80}")
        print(f"{kind_name} ({len(definitions)} 个)")
        print("=" * 80)

        print_definitions(definitions, show_doc=show_doc, show_symbol=show_symbol)


def print_statistics(definitions):
    """打印统计信息

    Args:
        definitions: 定义列表
    """
    grouped = group_by_kind(definitions)

    print(f"\n{'=' * 80}")
    print(f"统计信息 (共 {len(definitions)} 个符号定义)")
    print("=" * 80)

    for kind_name in sorted(grouped.keys()):
        count = len(grouped[kind_name])
        percentage = (count / len(definitions)) * 100
        print(f"{kind_name:30s}: {count:5d} ({percentage:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="查询 SCIP 文件中的符号定义",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("scip_file", help="SCIP 文件路径")
    parser.add_argument(
        "--kind",
        "-k",
        action="append",
        dest="kinds",
        help="按符号类型过滤 (可多次使用，如 --kind Function --kind Method)",
    )
    parser.add_argument("--language", "-l", help="按编程语言过滤")
    parser.add_argument("--group-by-kind", "-g", action="store_true", help="按符号类型分组显示")
    parser.add_argument("--show-doc", "-d", action="store_true", help="显示文档注释")
    parser.add_argument("--show-symbol", "-s", action="store_true", help="显示完整符号字符串")
    parser.add_argument("--stats", "-S", action="store_true", help="显示统计信息")
    parser.add_argument("--limit", "-n", type=int, default=None, help="限制显示数量")

    args = parser.parse_args()

    # 检查文件是否存在
    if not Path(args.scip_file).exists():
        print(f"错误: 文件不存在: {args.scip_file}", file=sys.stderr)
        sys.exit(1)

    print(f"正在解析 SCIP 文件: {args.scip_file}")

    # 解析 SCIP 文件
    src = SCIPParser(enable_indexing=True)
    try:
        index = src.parse_file(args.scip_file)
    except Exception as e:
        print(f"错误: 解析 SCIP 文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    print("解析完成!")
    print(f"  文档数: {len(index.documents)}")
    print(f"  符号总数: {len(index.list_symbols())}")

    # 获取所有定义
    definitions = get_all_definitions(index)
    print(f"  定义数: {len(definitions)}")

    # 应用过滤条件
    definitions = filter_by_kinds(definitions, args.kinds)
    definitions = filter_by_language(definitions, args.language)

    if args.kinds:
        print(f"  过滤后: {len(definitions)} 个定义")

    # 限制数量
    if args.limit:
        definitions = definitions[: args.limit]
        print(f"  显示前 {len(definitions)} 个")

    # 显示结果
    if args.stats:
        print_statistics(definitions)
    elif args.group_by_kind:
        grouped = group_by_kind(definitions)
        print_grouped_definitions(grouped, show_doc=args.show_doc, show_symbol=args.show_symbol)
    else:
        print(f"\n{'=' * 80}")
        print(f"找到 {len(definitions)} 个定义")
        print("=" * 80)
        print_definitions(definitions, show_doc=args.show_doc, show_symbol=args.show_symbol)

    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    main()
