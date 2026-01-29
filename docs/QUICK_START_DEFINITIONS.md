# 符号定义查询快速上手

`scip-parser` 提供了一系列便捷方法，让你能够轻松查询索引中的符号定义，而无需深入了解 SCIP 协议的底层细节。

## 基础查询方法

你可以直接通过 `Index` 对象访问以下方法：

### 1. 获取所有定义
返回索引中包含的所有符号定义的简明信息。
```python
definitions = index.get_all_definitions()
for d in definitions:
    print(f"符号: {d['display_name']}, 类型: {d['kind_name']}, 文档: {d['document']}")
```

### 2. 按类型获取定义
如果你只需要特定类型的符号（如类或函数），可以使用以下方法：

```python
from scip_parser.core.types import SymbolKind

# 获取所有函数
functions = index.get_functions()

# 获取所有类
classes = index.get_classes()

# 获取所有方法
methods = index.get_methods()

# 获取所有接口
interfaces = index.get_interfaces()

# 按自定义类型获取
enums = index.get_definitions_by_kind(SymbolKind.Enum)
```

### 3. 按语言过滤
```python
python_defs = index.get_definitions_by_language("python")
```

## 返回数据格式

上述所有便捷方法均返回一个字典列表（`list[dict]`），每个字典包含以下字段：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `symbol` | `str` | 符号的唯一 SCIP 标识符 |
| `display_name` | `str` | 符号的显示名称（如函数名、类名） |
| `kind` | `SymbolKind` | 符号类型的枚举值 |
| `kind_name` | `str` | 符号类型的字符串名称（如 "Function", "Class"） |
| `document` | `str` | 该符号定义所在的相对文件路径 |
| `language` | `str` | 编程语言名称 |
| `documentation` | `tuple[str]` | 关联的文档注释（Markdown 格式） |

## 统计信息

你还可以快速获取项目符号分布的统计数据：

```python
stats = index.get_statistics()
print(f"总文档数: {stats['total_documents']}")
print(f"总符号数: {stats['total_symbols']}")
print("语言分布:", stats['language_distribution'])
print("类型分布:", stats['kind_distribution'])
```

## 进阶查询

对于更复杂的过滤需求，建议使用 `QueryAPI`：

```python
from scip_parser import QueryAPI

query = QueryAPI(index)
results = (query
    .by_kind(SymbolKind.Function)
    .by_language("python")
    .has_documentation()
    .execute())
```
