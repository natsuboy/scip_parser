"""
SCIP Parser - 获取所有符号定义示例

这个示例展示了如何从 SCIP 文件中提取所有符号定义，
包括函数、方法、类、接口等。
"""


def get_all_definitions(index):
    """获取所有符号定义

    Args:
        index: SCIP Index 对象

    Returns:
        包含所有定义信息的列表，每个元素是一个字典
    """
    definitions = []

    # 遍历所有文档
    for document in index.documents:
        # document.symbols 是一个字典，包含了在该文档中定义的所有符号
        for symbol_str, symbol_info in document.symbols.items():
            definitions.append(
                {
                    "symbol": symbol_str,
                    "display_name": symbol_info.display_name,
                    "kind": symbol_info.kind,  # SymbolKind 枚举值
                    "kind_name": symbol_info.kind.name,  # 种类名称
                    "document": document.relative_path,
                    "language": document.language,
                    "documentation": symbol_info.documentation,
                }
            )

    return definitions


def filter_definitions_by_kind(definitions, kind):
    """按符号类型过滤定义

    Args:
        definitions: get_all_definitions() 返回的定义列表
        kind: SymbolKind 枚举值（如 SymbolKind.Function, SymbolKind.Method）

    Returns:
        过滤后的定义列表
    """
    return [d for d in definitions if d["kind"] == kind]


def filter_definitions_by_kinds(definitions, kinds):
    """按多个符号类型过滤定义

    Args:
        definitions: get_all_definitions() 返回的定义列表
        kinds: SymbolKind 枚举值列表

    Returns:
        过滤后的定义列表
    """
    kind_set = set(kinds)
    return [d for d in definitions if d["kind"] in kind_set]


def print_definitions(definitions, show_documentation=False):
    """打印定义列表

    Args:
        definitions: 定义列表
        show_documentation: 是否显示文档
    """
    print(f"\n找到 {len(definitions)} 个定义:")
    print("=" * 80)

    for i, definition in enumerate(definitions, 1):
        print(f"\n{i}. {definition['display_name']}")
        print(f"   符号: {definition['symbol']}")
        print(f"   类型: {definition['kind_name']}")
        print(f"   位置: {definition['document']}")

        if show_documentation and definition["documentation"]:
            print(f"   文档: {' '.join(definition['documentation'])}")


def example_find_all_functions():
    """示例: 查找所有函数定义"""
    print("=" * 80)
    print("示例 1: 查找所有函数定义")
    print("=" * 80)

    # 假设已经解析了 SCIP 文件
    # parser = SCIPParser()
    # index = parser.parse_file("your_project.scip")

    # 获取所有定义
    # definitions = get_all_definitions(index)

    # 过滤出函数
    # functions = filter_definitions_by_kind(definitions, SymbolKind.Function)

    # print(functions)

    print("\n# 代码示例:")
    print("""
from scip_parser import SCIPParser
from scip_parser.core.types import SymbolKind

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("your_project.scip")

# 获取所有定义
definitions = get_all_definitions(index)

# 方法1: 只获取函数
functions = filter_definitions_by_kind(definitions, SymbolKind.Function)
print(f"找到 {len(functions)} 个函数")

# 方法2: 获取函数和方法
functions_and_methods = filter_definitions_by_kinds(
    definitions,
    [SymbolKind.Function, SymbolKind.Method]
)
print(f"找到 {len(functions_and_methods)} 个函数和方法")
    """)


def example_find_classes_and_interfaces():
    """示例: 查找所有类和接口定义"""
    print("\n" + "=" * 80)
    print("示例 2: 查找所有类和接口定义")
    print("=" * 80)

    print("\n# 代码示例:")
    print("""
from scip_parser import SCIPParser
from scip_parser.core.types import SymbolKind

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("your_project.scip")

# 获取所有定义
definitions = get_all_definitions(index)

# 获取所有类
classes = filter_definitions_by_kind(definitions, SymbolKind.Class)
print(f"找到 {len(classes)} 个类")

# 获取所有接口
interfaces = filter_definitions_by_kind(definitions, SymbolKind.Interface)
print(f"找到 {len(interfaces)} 个接口")

# 获取所有类和接口
classes_and_interfaces = filter_definitions_by_kinds(
    definitions,
    [SymbolKind.Class, SymbolKind.Interface, SymbolKind.Trait]
)
print(f"找到 {len(classes_and_interfaces)} 个类/接口/Trait")
    """)


def example_find_all_symbols_with_details():
    """示例: 获取所有定义及其详细信息"""
    print("\n" + "=" * 80)
    print("示例 3: 获取所有定义的详细信息")
    print("=" * 80)

    print("\n# 代码示例:")
    print("""
from scip_parser import SCIPParser

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("your_project.scip")

# 获取所有定义
definitions = get_all_definitions(index)

# 按类型分组
from collections import defaultdict
by_kind = defaultdict(list)

for d in definitions:
    by_kind[d['kind_name']].append(d)

# 打印每种类型的数量
for kind_name, items in sorted(by_kind.items()):
    print(f"{kind_name}: {len(items)}")

# 查看所有函数定义
if 'Function' in by_kind:
    print("\\n所有函数:")
    for func in by_kind['Function']:
        print(f"  - {func['display_name']} 在 {func['document']}")
    """)


def example_get_definitions_from_document():
    """示例: 获取特定文档中的定义"""
    print("\n" + "=" * 80)
    print("示例 4: 获取特定文档中的定义")
    print("=" * 80)

    print("\n# 代码示例:")
    print("""
from scip_parser import SCIPParser
from scip_parser.core.types import SymbolKind

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("your_project.scip")

# 获取特定文档
doc = index.get_document("src/main.py")

if doc:
    print(f"文档: {doc.relative_path}")
    print(f"语言: {doc.language}")
    print(f"\\n该文档中定义的符号:")

    # 遍历该文档中定义的所有符号
    for symbol_str, symbol_info in doc.symbols.items():
        print(f"  - {symbol_info.display_name} ({symbol_info.kind.name})")
        if symbol_info.documentation:
            print(f"    文档: {' '.join(symbol_info.documentation)[:50]}...")
    """)


def example_find_all_occurrences_of_definition():
    """示例: 查找定义的所有出现位置"""
    print("\n" + "=" * 80)
    print("示例 5: 查找定义的所有出现位置")
    print("=" * 80)

    print("\n# 代码示例:")
    print("""
from scip_parser import SCIPParser

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("your_project.scip")

# 获取所有定义
definitions = get_all_definitions(index)

# 对于每个定义，查找它的所有出现位置（定义 + 引用）
for definition in definitions[:10]:  # 只看前10个
    symbol = definition['symbol']
    occurrences = index.get_symbol_occurrences(symbol)

    # 统计定义和引用数量
    definition_count = sum(1 for occ in occurrences if occ.is_definition)
    reference_count = len(occurrences) - definition_count

    print(f"\\n{definition['display_name']}:")
    print(f"  定义: {definition_count} 个")
    print(f"  引用: {reference_count} 个")

    # 打印所有引用位置
    if reference_count > 0:
        print(f"  引用位置:")
        for occ in occurrences:
            if not occ.is_definition:
                doc = index.get_document_by_occurrence(occ)  # 需要额外实现
                print(f"    - {doc.relative_path}:{occ.get_start_line()}")
    """)


def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("SCIP Parser - 获取所有符号定义示例")
    print("=" * 80)

    example_find_all_functions()
    example_find_classes_and_interfaces()
    example_find_all_symbols_with_details()
    example_get_definitions_from_document()
    example_find_all_occurrences_of_definition()

    print("\n" + "=" * 80)
    print("常用 SymbolKind 类型:")
    print("=" * 80)
    print("""
    SymbolKind.Function        - 函数
    SymbolKind.Method          - 方法
    SymbolKind.Class           - 类
    SymbolKind.Interface       - 接口
    SymbolKind.Trait           - Trait (Rust 等)
    SymbolKind.Struct          - 结构体 (Go, Rust 等)
    SymbolKind.Enum            - 枚举
    SymbolKind.Field           - 字段/属性
    SymbolKind.Variable        - 变量
    SymbolKind.Constant        - 常量
    SymbolKind.Module          - 模块
    SymbolKind.Namespace       - 命名空间
    SymbolKind.Constructor     - 构造函数
    SymbolKind.Getter          - Getter 方法
    SymbolKind.Setter          - Setter 方法
    """)

    print("\n" + "=" * 80)
    print("提示:")
    print("=" * 80)
    print("""
1. 使用 document.symbols 获取在该文档中定义的所有符号
2. 使用 index.get_symbol_occurrences(symbol) 获取符号的所有出现位置
3. 使用 Occurrence.is_definition 区分定义和引用
4. 使用 SymbolKind 枚举值过滤特定类型的符号
5. 所有数据结构都是不可变的，确保线程安全
    """)


if __name__ == "__main__":
    main()
