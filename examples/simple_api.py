"""
简化 API 使用示例

这个示例展示了如何使用 src 的简化 API，
无需了解 SCIP 协议细节即可完成常见任务。
"""



def example_1_get_all_functions():
    """示例 1: 获取所有函数定义"""
    print("=" * 80)
    print("示例 1: 获取所有函数定义")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser

    # 解析 SCIP 文件
    parser = SCIPParser()
    index = parser.parse_file("your_project.scip")

    # 获取所有函数定义
    functions = index.get_functions()

    print(f"找到 {len(functions)} 个函数")
    for func in functions:
        print(f"  - {func['display_name']} 在 {func['document']}")
    """)

    print("\n说明:")
    print("  - 使用 index.get_functions() 直接获取所有函数")
    print("  - 返回的字典包含: display_name, document, symbol 等")
    print("  - 无需了解 SCIP 协议细节")


def example_2_get_classes_and_interfaces():
    """示例 2: 获取所有类和接口"""
    print("\n" + "=" * 80)
    print("示例 2: 获取所有类和接口")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser

    parser = SCIPParser()
    index = parser.parse_file("your_project.scip")

    # 获取所有类
    classes = index.get_classes()
    print(f"找到 {len(classes)} 个类")

    # 获取所有接口
    interfaces = index.get_interfaces()
    print(f"找到 {len(interfaces)} 个接口")

    # 也可以一次获取多种类型
    from scip_parser.core.types import SymbolKind
    types = index.get_definitions_by_kinds([
        SymbolKind.Class,
        SymbolKind.Interface
    ])
    print(f"找到 {len(types)} 个类和接口")
    """)


def example_3_statistics():
    """示例 3: 统计符号类型分布"""
    print("\n" + "=" * 80)
    print("示例 3: 统计符号类型分布")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser

    parser = SCIPParser()
    index = parser.parse_file("your_project.scip")

    # 统计各类型符号数量
    counts = index.count_symbols_by_kind()

    print("符号类型统计:")
    total = sum(counts.values())
    for kind_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        percentage = (count / total) * 100
        print(f"  {kind_name:20s}: {count:5d} ({percentage:5.1f}%)")
    """)


def example_4_filter_by_language():
    """示例 4: 按编程语言过滤"""
    print("\n" + "=" * 80)
    print("示例 4: 按编程语言过滤")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser

    parser = SCIPParser()
    index = parser.parse_file("your_project.scip")

    # 只获取 Python 文件中的函数
    python_functions = [
        f for f in index.get_functions()
        if f['language'].lower() == 'python'
    ]

    # 或者使用便捷方法
    python_defs = index.get_definitions_by_language("python")

    print(f"Python 文件中有 {len(python_defs)} 个定义")
    """)


def example_5_custom_filter():
    """示例 5: 自定义过滤"""
    print("\n" + "=" * 80)
    print("示例 5: 自定义过滤")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser

    parser = SCIPParser()
    index = parser.parse_file("your_project.scip")

    # 获取所有定义
    all_defs = index.get_all_definitions()

    # 过滤出有文档注释的符号
    documented = [d for d in all_defs if d['documentation']]

    print(f"有文档注释的符号: {len(documented)} 个")

    # 过滤出名称包含 'test' 的函数
    test_functions = [
        f for f in index.get_functions()
        if 'test' in f['display_name'].lower()
    ]

    print(f"测试函数: {len(test_functions)} 个")

    # 按文档分组
    from collections import defaultdict
    by_document = defaultdict(list)

    for d in all_defs:
        by_document[d['document']].append(d['display_name'])

    for doc, symbols in sorted(by_document.items()):
        print(f"{doc}: {len(symbols)} 个符号")
    """)


def example_6_complete_workflow():
    """示例 6: 完整的工作流"""
    print("\n" + "=" * 80)
    print("示例 6: 完整的工作流")
    print("=" * 80)

    print("\n代码:")
    print("""
    from scip_parser import SCIPParser
    from scip_parser.core.types import SymbolKind

    def analyze_project(scip_file):
        \"\"\"分析项目中的符号定义\"\"\"

        # 解析 SCIP 文件
        parser = SCIPParser()
        index = parser.parse_file(scip_file)

        # 基本信息
        print(f"项目: {scip_file}")
        print(f"文档数: {len(index.documents)}")

        # 统计信息
        counts = index.count_symbols_by_kind()
        print(f"\\n符号统计:")
        print(f"  函数: {counts.get('Function', 0)}")
        print(f"  方法: {counts.get('Method', 0)}")
        print(f"  类: {counts.get('Class', 0)}")
        print(f"  接口: {counts.get('Interface', 0)}")

        # 获取所有类和方法
        classes = index.get_classes()
        methods = index.get_methods()

        print(f"\\n详细信息:")
        print(f"  类:")
        for cls in classes[:5]:  # 只显示前5个
            print(f"    - {cls['display_name']} ({cls['document']})")

        print(f"  方法 (显示前10个):")
        for method in methods[:10]:
            print(f"    - {method['display_name']} ({method['document']})")

    # 使用
    analyze_project("your_project.scip")
    """)


def comparison_old_vs_new():
    """对比: 旧方式 vs 新方式"""
    print("\n" + "=" * 80)
    print("对比: 使用简化 API 前后的差异")
    print("=" * 80)

    print("\n❌ 旧方式 (需要了解 SCIP 协议细节):")
    print("""
    from scip_parser import SCIPParser
    from scip_parser.core.types import SymbolKind

    parser = SCIPParser()
    index = parser.parse_file("project.scip")

    # 需要遍历文档，然后遍历 symbols 字典
    functions = []
    for document in index.documents:
        for symbol_str, symbol_info in document.symbols.items():
            if symbol_info.kind == SymbolKind.Function:
                functions.append({
                    'name': symbol_info.display_name,
                    'document': document.relative_path,
                    'symbol': symbol_str,
                })
    """)

    print("\n✅ 新方式 (简洁直观):")
    print("""
    from scip_parser import SCIPParser

    parser = SCIPParser()
    index = parser.parse_file("project.scip")

    # 一行代码搞定
    functions = index.get_functions()
    """)

    print("\n🎯 优势:")
    print("  - 代码更简洁 (1 行 vs 7 行)")
    print("  - 无需了解 SCIP 协议")
    print("  - 返回格式统一，便于使用")
    print("  - 方法名清晰直观")


def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("SCIP Parser 简化 API 使用示例")
    print("=" * 80)
    print("\n这些示例展示了如何使用简化的 API，无需了解 SCIP 协议细节。\n")

    example_1_get_all_functions()
    example_2_get_classes_and_interfaces()
    example_3_statistics()
    example_4_filter_by_language()
    example_5_custom_filter()
    example_6_complete_workflow()
    comparison_old_vs_new()

    print("\n" + "=" * 80)
    print("可用的简化 API 方法")
    print("=" * 80)
    print("""
Index 类提供的便捷方法:

1. 基础查询:
   - get_all_definitions()           获取所有定义
   - get_definitions_by_kind(kind)   按类型获取
   - get_definitions_by_kinds(kinds) 按多个类型获取
   - get_definitions_by_language(lang) 按语言获取

2. 类型快捷方法:
   - get_functions()    获取所有函数
   - get_methods()      获取所有方法
   - get_classes()      获取所有类
   - get_interfaces()   获取所有接口

3. 统计方法:
   - count_symbols_by_kind()  统计各类型符号数量

4. 返回格式:
   每个方法返回字典列表，包含:
   - symbol: 符号唯一标识符
   - display_name: 显示名称
   - kind: SymbolKind 枚举值
   - kind_name: 类型名称 (字符串)
   - document: 文档路径
   - language: 编程语言
   - documentation: 文档注释列表
    """)

    print("\n" + "=" * 80)
    print("完整文档请查看: docs/QUICK_START_DEFINITIONS.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
