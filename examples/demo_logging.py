"""
演示 debug 日志输出的脚本

这个脚本创建一个小的 SCIP 索引并展示 debug 日志的输出。
"""


from scip_parser.core.types import (
    Document,
    Index,
    Metadata,
    Occurrence,
    PositionEncoding,
    SymbolInformation,
    SymbolKind,
    TextEncoding,
    ToolInfo,
)
from scip_parser.query.api import QueryAPI
from scip_parser.utils.logging_config import enable_debug_logging

# 启用 debug 日志
enable_debug_logging()

# 创建一个简单的 SCIP 索引
print("创建示例 SCIP 索引...\n")

metadata = Metadata(
    version=1,
    tool_info=ToolInfo(name="test-tool", version="1.0.0"),
    project_root="/test/project",
    text_document_encoding=TextEncoding.UTF8,
)

# 创建一个文档
doc = Document(
    relative_path="test.py",
    language="python",
    occurrences=[
        Occurrence(
            range=[0, 0, 5, 0],
            symbol="python test.py test#foo().",
            symbol_roles=64,  # Definition
            syntax_kind=None,
        ),
        Occurrence(
            range=[2, 4, 2, 7],
            symbol="python test.py test#foo().",
            symbol_roles=0,  # Reference
            syntax_kind=None,
        ),
    ],
    symbols={
        "python test.py test#foo().": SymbolInformation(
            symbol="python test.py test#foo().",
            kind=SymbolKind.Function,
            display_name="foo",
            documentation=["测试函数"],
            relationships=[],
            enclosing_symbol=None,
            signature_documentation=None,
        )
    },
    text="def foo():\n    pass\nfoo()\n",
    position_encoding=PositionEncoding.UTF8CodeUnitOffsetFromLineStart,
)

# 创建索引
index = Index(
    metadata=metadata,
    documents=[doc],
    external_symbols=[],
)

# 构建索引
index.build_indexes()

print("\n" + "=" * 60)
print("使用 QueryAPI 查询...")
print("=" * 60 + "\n")

# 使用查询 API
query = QueryAPI(index)
functions = query.by_kind(SymbolKind.Function).execute()
print(f"找到 {len(functions)} 个函数\n")

if functions:
    func = functions[0]
    print(f"函数名称: {func.display_name}")
    print(f"函数符号: {func.symbol}\n")

    print("查找引用...")
    refs = query.find_references(func.symbol)
    print(f"找到 {len(refs)} 个引用\n")

    print("使用 Index 方法查找定义...")
    definition = index.find_definition(func.symbol)
    if definition:
        print(f"定义位置: 行 {definition.range[0]} 到 行 {definition.range[2]}\n")

print("\n" + "=" * 60)
print("debug 日志演示完成")
print("=" * 60)
