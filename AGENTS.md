# Agent Guidelines (AGENTS.md)

本文件为在 SCIP Parser 代码库中工作的 AI 代理提供指导。SCIP Parser 是一个高性能的 SCIP (Source Code Intelligence Protocol) 文件 Python 解析工具库。

## 1. 基本指令

- **语言要求**: 
  - **代码和注释**: 必须使用 **English**。这包括所有 docstrings、行内注释和变量命名。
  - **文档和交互**: 必须使用 **简体中文**。这包括本文件、PR 描述、Issue 回复以及与用户的对话。
- **环境**: 使用 `uv` 作为包管理器。所有命令应通过 `uv run` 执行。
- **核心原则**: 优先保持不可变性，确保高性能，遵循 SCIP 协议规范。

## 2. 常用开发命令

### 环境设置
```bash
uv sync                  # 安装依赖
```

### 运行测试 (pytest)
```bash
uv run pytest                        # 运行所有测试
uv run pytest tests/test_parser.py    # 运行单个测试文件
uv run pytest tests/test_parser.py::test_symbol_role_bitmask  # 运行特定测试
uv run pytest -v                      # 详细输出
uv run pytest --benchmark-only        # 运行性能基准测试
```

### 代码质量与格式化
```bash
uv run black src/             # 格式化代码 (行宽 100)
uv run ruff check src/        # 运行 Linter
uv run ruff check --fix src/           # 自动修复 Linter 问题
uv run mypy src/              # 静态类型检查
```

### Protocol Buffer 管理
```bash
uv run python scripts/manage_proto.py all      # 下载并编译最新 proto
uv run python scripts/manage_proto.py compile  # 仅编译 proto
uv run python scripts/manage_proto.py status   # 检查 proto 状态
```

## 3. 代码风格指南

### 格式规范
- **行长度**: 100 字符。
- **格式化工具**: 严格遵循 `black` 的输出。
- **导入顺序**: 使用 `ruff` (isort 兼容模式) 自动排序。
  - 标准库 -> 第三方库 -> 本地模块。

### 命名约定
- **类名**: `PascalCase` (如 `SCIPParser`, `SymbolInformation`)。
- **函数/变量/方法**: `snake_case` (如 `parse_file`, `symbol_index`)。
- **常量**: `UPPER_SNAKE_CASE`。
- **内部变量**: 以单下划线开头 (如 `_symbol_index`)。

### 类型与数据结构
- **不可变性**: 核心数据模型必须使用 `@dataclass(frozen=True)`。
- **类型注解**:
  - 所有文件必须包含 `from __future__ import annotations`。
  - 所有函数签名和类属性必须包含完整的类型提示。
  - 优先使用内置集合类型：使用 `list[]`, `dict[]`, `set[]` 而非 `List`, `Dict`, `Set`。
  - 使用 `Type | None` 而非 `Optional[Type]`。
  - 覆盖方法时必须使用 `typing_extensions.override` 装饰器。
  - 在 dataclass 中，可变默认值（如列表）必须使用 `field(default_factory=list)`。
- **SCIP 符号**: 符号字符串格式为 `<scheme> <package_manager> <package_name> <version> <descriptors>`。

### 错误处理
- 使用具体的异常类而非通用的 `Exception`。
- 关键逻辑应包含清晰的错误消息（English）。
- 对于解析错误，提供详细的上下文信息（如行号或偏移量）。

## 4. 项目架构与关键组件

### 核心数据流
```
SCIP 文件 → SCIPParser → Index → (Document, Occurrence, SymbolInformation)
                                    ↓
                            内部索引 (_symbol_index, _document_index)
                                    ↓
                            查询操作 (get_symbol_occurrences, list_symbols, etc.)
```

### 关键设计决策
1. **不可变数据结构**: 所有核心数据类使用 `@dataclass(frozen=True)`，确保线程安全和数据一致性。
2. **延迟索引构建**: `Index.build_indexes()` 在解析后构建 O(1) 查找索引。
3. **符号字符串格式**: SCIP 符号使用特殊格式，如 `python myproject myproject 1.0 main#main().`
   - 格式: `<scheme> <package_manager> <package_name> <version> <descriptors>`
   - 描述符通过后缀区分类型: `#` (Type), `().` (Method), `.` (Term), `/` (Namespace)

### 模块职责
- `src/scip_parser/core/`:
  - `types.py`: 核心数据模型 (frozen dataclasses)。
  - `parser.py`: 基于 `protobuf` 的二进制解析器。
- `src/scip_parser/query/`:
  - `api.py`: 封装了复杂的索引查询逻辑。
- `src/scip_parser/graph/`:
  - `call_graph.py`: 使用 `networkx` 构建和分析函数调用图。
  - `dependency_graph.py`: 处理模块间的导入和依赖关系。
- `src/scip_parser/utils/`:
  - `symbol.py`: 提供 `SymbolParser` 用于处理复杂的 SCIP 符号字符串。
- `src/scip_parser/proto/`: 包含 `scip_pb2.py` (Do not edit directly)。

## 5. 开发最佳实践

### 性能优化
- **避免循环搜索**: 不要遍历 `Index.documents` 来查找符号。应先调用 `Index.build_indexes()`，然后通过 `_symbol_index` 进行 O(1) 查询。
- **内存管理**: 对于大型 SCIP 文件，优先使用生成器和迭代器处理数据。
- **字符串优化**: 使用 `sys.intern` 或类似的机制处理频繁出现的字符串（如路径和 scheme）。

### 类型安全
- 始终使用最新的 Python 类型语法（如 `|` 取代 `Union`）。
- 确保所有 `list` 和 `dict` 都有明确的泛型定义。
- 在涉及位运算的角色判断时，务必编写单元测试。
- **处理 Optional**: 访问可能为 `None` 的属性前必须进行显式检查或使用安全访问模式。

## 6. 任务执行流程

1. **评估阶段**: 
   - 检查 `AGENTS.md` 获取最新指令。
   - 检查代码库中的 `docs/` 目录了解相关背景。
2. **设计阶段**:
   - 如果涉及核心数据结构修改，必须先评估对现有索引构建逻辑的影响。
   - 优先设计不可变的数据转换流程。
3. **实施阶段**:
   - 编写代码前先考虑数据不可变性。
   - 实现新功能时，同步更新测试用例。
   - **注意**: 确保新增代码的注释为英文。
4. **验证阶段**:
   - 必须运行 `uv run black .` 和 `uv run ruff check .` 确保风格一致。
   - 必须运行 `uv run mypy .` 验证类型安全。
   - 必须运行 `uv run pytest` 确保功能正确且无回归。

## 7. 代码审查清单 (Checklist)

在提交任何更改或完成任务前，请确保：
- [ ] 逻辑正确性：是否处理了所有边界情况？
- [ ] 性能影响：是否引入了不必要的 O(n) 搜索？
- [ ] 类型完整性：所有新增函数是否都有类型提示？Mypy 是否通过？
- [ ] 测试覆盖：是否为新功能编写了单元测试？
- [ ] 格式规范：是否运行了 `black` 和 `ruff`？
- [ ] 语言规范：代码和注释使用英文？文档和交互使用中文？

## 8. 常见反模式 (Anti-patterns)

- **直接编辑 `scip_pb2.py`**: 这是自动生成的，修改会被覆盖。
- **使用 `Union`/`Optional`**: 应使用 `TypeA | TypeB`。
- **使用 `List`/`Dict`/`Set`**: 应使用 `list`, `dict`, `set`。
- **捕获所有异常**: 避免 `except Exception: pass`。
- **硬编码符号前缀**: 使用 `SymbolParser`。
- **忽略 `SymbolRole` 位掩码**: 始终使用 `&` 运算符。
- **Dataclass 默认值错误**: 使用 `field(default_factory=list)`。
