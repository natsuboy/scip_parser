# SCIP Parser

一个高性能的 SCIP (Source Code Intelligence Protocol) 文件 Python 解析工具库。

## 功能特性

- ✅ **完整的 SCIP 协议支持** - 支持最新版本的 SCIP 协议
- ✅ **高性能解析** - 优化的数据结构和索引机制,快速查询
- ✅ **丰富的查询 API** - 提供便捷的符号查询、引用查找等功能
- ✅ **关系图构建** - 自动构建函数调用图、依赖关系图、继承关系图
- ✅ **数据增强** - 支持通过扩展接口增强符号信息
- ✅ **类型安全** - 使用 Python 类型注解和不可变数据结构
- ✅ **易于使用** - 简洁的 API 设计,快速上手

## 安装

```bash
# 使用 uv (推荐)
uv add scip-parser

# 使用 pip
pip install scip-parser
```

## 快速开始

### 基础使用

```python
from scip_parser import SCIPParser, QueryAPI

# 1. 解析 SCIP 文件
parser = SCIPParser()
index = parser.parse_file("myproject.scip")

# 2. 创建查询 API
query = QueryAPI(index)

# 3. 查找函数定义
definitions = query.find_definitions("python myproject/main.py main#main().")
for definition in definitions:
    print(f"Found definition at line {definition.range[0]}")

# 4. 查找所有引用
references = query.find_references("python myproject/utils.py utils#Helper.help().")
print(f"Found {len(references)} references")
```

## 项目结构

```
.
├── src/                            # 源代码目录
│   └── scip_parser/               # 包主目录
│       ├── core/                  # 核心解析模块
│       │   ├── parser.py          # SCIP 文件解析器
│       │   └── types.py           # SCIP 数据模型
│       ├── query/                 # 查询 API 模块
│   │   ├── api.py                 # 高级查询接口
│   │   ├── filters.py             # 符号过滤器
│   │   └── search.py              # 符号搜索功能
│   ├── graph/                     # 关系图构建模块
│   │   ├── call_graph.py          # 函数调用图
│   │   ├── dependency_graph.py    # 依赖关系图
│   │   └── inheritance_graph.py   # 继承关系图
│   ├── enrich/                    # 数据增强模块
│   │   ├── adapter.py             # 适配器
│   │   └── enricher.py            # 增强器
│   ├── utils/                     # 工具模块
│   │   ├── symbol.py              # 符号解析工具
│   │   └── cache.py               # 缓存管理
│   └── proto/                     # Protocol Buffer 定义
├── tests/                         # 测试目录
├── examples/                      # 示例代码
├── scripts/                       # 维护脚本
├── pyproject.toml                # 项目配置
└── uv.lock                       # uv 锁定文件
```

## 开发

### 安装开发依赖

```bash
uv sync
```

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run black src/
```

### 类型检查

```bash
uv run mypy src/
```

## 项目文档

- [AI 代理开发指南](AGENTS.md) - 在本代码库工作的 AI 代理必须遵循的规则。
- [Debug 日志指南](docs/logging.md) - 如何配置和查看详细的调试日志。
- [SCIP Proto 管理](scripts/README.md) - 如何更新和编译 SCIP 协议定义。
- [代码审计报告 (2026-01-27)](docs/audit_report_2026_01_27.md) - 对项目进行的全面代码质量和架构审计。

## 许可证

MIT License

