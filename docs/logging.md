# Debug 日志使用指南

## 概述

SCIP Parser 支持完整的 debug 日志功能，可以帮助你跟踪和理解代码的执行流程。

## pytest 中的日志

### 自动配置 (推荐)

在 `pyproject.toml` 中已经配置了 pytest 的日志输出:

```toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**默认情况下, pytest 会自动显示 INFO 级别及以上的日志**, 包括:
- 解析文件的开始和完成
- 索引构建的统计信息
- 主要操作步骤

### 查看 DEBUG 日志

如果需要查看详细的 DEBUG 级别日志(包括每个符号的处理细节), 在运行 pytest 时添加 `--log-cli-level=DEBUG` 参数:

```bash
# 运行特定测试并查看详细日志
uv run pytest tests/test_parser.py -v --log-cli-level=DEBUG

# 运行所有测试并查看详细日志
uv run pytest -v --log-cli-level=DEBUG
```

---

## 常见问题与解决方案

### 问题: 在 conftest.py 中调用 enable_debug_logging() 没有输出

#### 原因
pytest 有自己的日志捕获机制 (`logcapture`)，会拦截并管理所有日志输出。即使在代码中调用 `logging.basicConfig()` 或 `enable_debug_logging()`，pytest 也会覆盖这些配置。

#### 解决方案
SCIP Parser 已经在 `pyproject.toml` 中配置了 pytest 的日志输出。建议直接使用命令行参数控制日志级别：

```bash
# 查看详细日志 (DEBUG 级别)
uv run pytest -v --log-cli-level=DEBUG

# 只查看错误/警告
uv run pytest -v --log-cli-level=ERROR
```

---

## 普通脚本中的日志

### 启用日志

```python
from scip_parser import SCIPParser
from scip_parser.utils.logging_config import enable_debug_logging, enable_info_logging

# 启用 debug 日志 (输出所有详细信息)
enable_debug_logging()

# 或仅启用 info 日志 (输出一般信息)
# enable_info_logging()

parser = SCIPParser()
index = parser.parse_file("example.scip")
```

### 自定义日志配置

```python
from scip_parser.utils.logging_config import setup_logging
import logging

# 自定义日志级别和格式
setup_logging(
    level=logging.WARNING,  # 只输出警告和错误
    log_file="scip_parser.log",  # 可选: 输出到文件
    format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

## 关键路径的日志输出

- **文件解析流程 (parser.py)**: `DEBUG` 级别记录文件解析状态、PB 消息大小等。
- **索引构建流程 (types.py)**: `INFO` 级别记录构建开始和完成统计，`DEBUG` 级别记录每个文档的添加。
- **查询执行流程 (query/api.py)**: `DEBUG` 级别记录过滤器应用和结果统计。
- **符号查找流程 (types.py)**: `DEBUG` 级别记录具体的定义和引用查找。

## 性能考虑

- 在生产环境中，建议使用 `INFO` 或 `WARNING` 级别。
- Debug 日志会产生大量输出，仅用于开发和调试。
- 如果需要长期记录日志，请使用 `setup_logging()` 并指定日志文件。
