# SCIP Proto 管理脚本

这个目录包含用于管理 SCIP Protocol Buffer 文件的脚本。

## 前置要求

在使用脚本之前，确保安装了以下工具：

### 1. Protocol Buffers 编译器 (protoc)

**macOS:**
```bash
brew install protobuf
```

**Ubuntu/Debian:**
```bash
apt install protobuf-compiler
```

**其他系统:**
访问 https://grpc.io/docs/protoc-installation/

### 2. Python 依赖

项目依赖会自动通过 `uv` 安装，包括：
- `protobuf`: Protocol Buffers 运行时库
- `mypy-protobuf`: 生成 Python 类型存根
- `types-protobuf`: Protocol Buffers 类型定义

## 使用方法

### 查看帮助

```bash
uv run python scripts/manage_proto.py --help
```

### 常用命令

#### 1. 检查依赖

```bash
uv run python scripts/manage_proto.py check
```

验证 `protoc` 和 `mypy-protobuf` 是否已正确安装。

#### 2. 查看状态

```bash
uv run python scripts/manage_proto.py status
```

显示当前 proto 文件的状态：
- Proto 源文件
- 生成的 Python 代码
- 类型存根文件
- py.typed 标记

#### 3. 下载 Proto 文件

```bash
# 下载最新的 proto 文件
uv run python scripts/manage_proto.py download

# 强制重新下载（覆盖已存在的文件）
uv run python scripts/manage_proto.py download --force

# 从指定 URL 下载
uv run python scripts/manage_proto.py download --url https://example.com/scip.proto
```

#### 4. 编译 Proto 文件

```bash
uv run python scripts/manage_proto.py compile
```

这将：
1. 使用 `protoc` 编译 `scip.proto`
2. 生成 `scip_pb2.py` (Python 代码)
3. 生成 `scip_pb2.pyi` (类型存根文件)
4. 创建 `py.typed` 标记文件

#### 5. 验证类型存根

```bash
uv run python scripts/manage_proto.py verify
```

使用 mypy 验证生成的类型存根是否正常工作。

#### 6. 清理生成的文件

```bash
uv run python scripts/manage_proto.py clean
```

删除所有生成的文件（proto 源文件、Python 代码、类型存根等）。

#### 7. 执行完整流程

```bash
uv run python scripts/manage_proto.py all
```

自动执行以下步骤：
1. ✓ 检查依赖
2. ✓ 下载 proto 文件（强制覆盖）
3. ✓ 编译 proto 文件
4. ✓ 创建 py.typed 标记
5. ✓ 验证生成的类型存根

### 组合命令

你可以组合多个命令：

```bash
# 下载并编译
uv run python scripts/manage_proto.py download compile

# 下载、编译并验证
uv run python scripts/manage_proto.py download compile verify
```

## 文件结构

编译后的文件位于 `src/proto/` 目录：

```
src/proto/
├── scip.proto          # Proto 源文件（从 SCIP 官方仓库下载）
├── scip_pb2.py         # 生成的 Python 代码
├── scip_pb2.pyi        # 生成的类型存根文件（用于编辑器类型提示）
├── py.typed            # 标记文件，表明此包包含类型信息
└── __init__.py         # 包初始化文件
```

## 类型检查

生成的 `.pyi` 文件提供完整的类型信息，支持：

- **编辑器自动补全**: VS Code、PyCharm 等编辑器可以识别类型
- **静态类型检查**: 使用 mypy 进行类型检查
- **IDE 类型提示**: 鼠标悬停查看类型信息

### 示例

```python
from src.proto.scip_pb2 import Index, Document, ToolInfo

# 创建 Index 实例（编辑器会提供类型提示）
index = Index()

# 创建并设置 metadata（类型检查会验证参数类型）
tool_info = ToolInfo(name="my-tool", version="1.0.0")
metadata = Metadata(
    version=0,
    tool_info=tool_info,
    project_root="/path/to/project"
)

# 添加文档（类型检查会验证 Document 类型）
document = Document(
    language="Python",
    relative_path="example.py",
    text="print('hello world')"
)
index.documents.append(document)
```

## 故障排除

### 问题：protoc 未找到

**错误信息:**
```
✗ protoc 未安装或不在 PATH 中
```

**解决方案:**
1. 安装 Protocol Buffers 编译器（见"前置要求"）
2. 确保 `protoc` 在你的 PATH 中：`which protoc`

### 问题：mypy-protobuf 未安装

**错误信息:**
```
✗ mypy-protobuf 未安装
```

**解决方案:**
```bash
uv pip install mypy-protobuf
```

### 问题：类型检查失败

**错误信息:**
```
⚠ mypy 检查发现问题（建议安装 types-protobuf）
```

**解决方案:**
```bash
uv pip install types-protobuf
```

### 问题：编辑器无法识别类型

**解决方案:**
1. 确保 `py.typed` 文件存在
2. 重启语言服务器（VS Code：Ctrl+Shift+P → "Python: Restart Language Server"）
3. 确保编辑器安装了 Python 扩展和 Pylance

## 更新 Proto 文件

当 SCIP 协议更新时，运行：

```bash
# 更新到最新版本
uv run python scripts/manage_proto.py all

# 或者从特定的分支/标签下载
uv run python scripts/manage_proto.py download --url <URL>
uv run python scripts/manage_proto.py compile
```

## 相关文档

- [SCIP 协议规范](https://github.com/sourcegraph/scip)
- [Protocol Buffers 文档](https://developers.google.com/protocol-buffers)
- [mypy-protobuf 文档](https://github.com/nipunn1313/mypy-protobuf)
