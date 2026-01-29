"""
示例: 使用 debug 日志

这个示例展示了如何启用并使用 SCIP Parser 的 debug 日志功能。
"""

from scip_parser import QueryAPI, SCIPParser
from scip_parser.core.types import SymbolKind
from scip_parser.utils.logging_config import enable_debug_logging

# 启用 debug 日志
enable_debug_logging()

# 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("example.scip")

# 创建查询 API
query = QueryAPI(index)

# 查找符号定义
print("查找函数定义:")
functions = query.by_kind(SymbolKind.Function).execute()
print(f"找到 {len(functions)} 个函数")

# 查找特定符号的引用
if functions:
    first_function = functions[0]
    print(f"\n查找 '{first_function.display_name}' 的引用:")
    references = query.find_references(first_function.symbol)
    print(f"找到 {len(references)} 个引用")

# 使用索引方法
print("\n使用 Index 方法:")
symbols = index.list_symbols()
print(f"总共有 {len(symbols)} 个符号")

# 查找定义
if symbols:
    first_symbol = list(symbols)[0]
    definition = index.find_definition(first_symbol)
    if definition:
        print(f"定义位置: {definition.range}")
