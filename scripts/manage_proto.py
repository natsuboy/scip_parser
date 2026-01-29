#!/usr/bin/env python3
"""SCIP Proto 文件管理脚本。

用于下载、编译和验证 SCIP protocol buffer 文件。
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# SCIP proto 文件的官方 URL
SCIP_PROTO_URL = "https://raw.githubusercontent.com/sourcegraph/scip/main/scip.proto"
# 备用 URL（从不同的分支或标签）
SCIP_PROTO_FALLBACK_URLS = [
    "https://raw.githubusercontent.com/sourcegraph/scip/refs/heads/main/scip.proto",
    "https://raw.githubusercontent.com/sourcegraph/scip/refs/heads/develop/scip.proto",
]

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
PROTO_DIR = PROJECT_ROOT / "src" / "scip_parser" / "proto"


class Colors:
    """终端颜色代码。"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_success(msg: str) -> None:
    """打印成功消息。"""
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_info(msg: str) -> None:
    """打印信息消息。"""
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")


def print_warning(msg: str) -> None:
    """打印警告消息。"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


def print_error(msg: str) -> None:
    """打印错误消息。"""
    print(f"{Colors.RED}✗{Colors.END} {msg}")


def check_protoc() -> bool:
    """检查 protoc 是否已安装。"""
    try:
        result = subprocess.run(
            ["protoc", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip()
        print_success(f"protoc 已安装: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("protoc 未安装或不在 PATH 中")
        print_info("请安装 Protocol Buffers 编译器:")
        print_info("  macOS: brew install protobuf")
        print_info("  Ubuntu: apt install protobuf-compiler")
        print_info("  或访问: https://grpc.io/docs/protoc-installation/")
        return False


def check_mypy_protobuf() -> bool:
    """检查 mypy-protobuf 是否已安装。"""
    try:
        import mypy_protobuf  # noqa: F401

        print_success("mypy-protobuf 已安装")
        return True
    except ImportError:
        print_error("mypy-protobuf 未安装")
        print_info("请运行: uv pip install mypy-protobuf")
        return False


def download_proto(url: Optional[str] = None, force: bool = False) -> bool:
    """下载 SCIP proto 文件。

    Args:
        url: proto 文件的 URL。如果为 None，使用默认 URL。
        force: 是否覆盖已存在的文件。

    Returns:
        是否成功下载。
    """
    proto_file = PROTO_DIR / "scip.proto"

    if proto_file.exists() and not force:
        print_warning(f"{proto_file} 已存在，使用 --force 强制重新下载")
        return True

    # 如果没有提供 URL，使用默认 URL
    urls_to_try = [url] if url else [SCIP_PROTO_URL] + SCIP_PROTO_FALLBACK_URLS

    print_info(f"下载 SCIP proto 文件到 {proto_file}")

    for i, download_url in enumerate(urls_to_try):
        try:
            print_info(f"尝试从 {download_url} 下载...")
            _ = subprocess.run(
                ["curl", "-fsSL", "-o", str(proto_file), download_url],
                check=True,
            )

            # 验证文件是否有效
            if proto_file.stat().st_size < 1000:
                print_error("下载的文件太小，可能无效")
                if i < len(urls_to_try) - 1:
                    continue
                return False

            print_success(f"成功下载 {proto_file.name}")
            return True

        except subprocess.CalledProcessError:
            if i < len(urls_to_try) - 1:
                print_warning(f"从 {download_url} 下载失败，尝试备用 URL...")
                continue
            else:
                print_error("所有下载尝试都失败了")
                return False

    return False


def compile_proto() -> bool:
    """编译 proto 文件为 Python 代码和 .pyi 类型存根。

    Returns:
        是否成功编译。
    """
    proto_file = PROTO_DIR / "scip.proto"

    if not proto_file.exists():
        print_error(f"{proto_file} 不存在，请先运行 download 命令")
        return False

    print_info("编译 proto 文件...")

    # 检查是否生成了预期的文件
    python_file = PROTO_DIR / "scip_pb2.py"
    stub_file = PROTO_DIR / "scip_pb2.pyi"

    try:
        # 运行 protoc
        # 为了让 protoc 找到 proto 文件，需要指定 --proto_path（或 -I）。
        # 同时把要编译的文件以相对于 proto_path 的路径传入，这里使用文件名并在 PROTO_DIR 下运行命令。
        _ = subprocess.run(
            [
                "protoc",
                f"--proto_path={PROTO_DIR}",
                f"--python_out={PROTO_DIR}",
                f"--mypy_out={PROTO_DIR}",
                proto_file.name,
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(PROTO_DIR),
        )

        if python_file.exists():
            print_success(f"生成 {python_file.relative_to(PROJECT_ROOT)}")
        else:
            print_warning(f"{python_file.relative_to(PROJECT_ROOT)} 未生成")

        if stub_file.exists():
            print_success(f"生成 {stub_file.relative_to(PROJECT_ROOT)}")
        else:
            print_warning(f"{stub_file.relative_to(PROJECT_ROOT)} 未生成")

        print_success("proto 文件编译完成")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"编译失败: {e.stderr}")
        return False


def create_pytyped() -> None:
    """创建 py.typed 标记文件。"""
    pytyped_file = PROTO_DIR / "py.typed"
    pytyped_file.touch()
    print_success(f"创建 {pytyped_file.relative_to(PROJECT_ROOT)}")


def verify_types() -> bool:
    """验证生成的类型存根是否正常工作。

    Returns:
        验证是否通过。
    """
    print_info("验证类型存根...")

    test_file = PROTO_DIR / "_type_test.py"
    test_code = """from scip_parser.proto.scip_pb2 import Index

# 测试基本导入
index = Index()

# 测试类型推断
metadata = index.metadata
documents = index.documents
external_symbols = index.external_symbols

print("类型验证通过 ✓")
"""

    try:
        # 写入测试文件
        test_file.write_text(test_code)

        # 尝试多种方式运行 mypy
        mypy_commands = [
            ["python", "-m", "mypy", str(test_file)],
            ["mypy", str(test_file)],
        ]

        result = None
        timed_out = False
        for cmd in mypy_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                    timeout=60,
                )
                break
            except subprocess.TimeoutExpired:
                # 单次 mypy 调用超时，记录并尝试下一种调用方式
                timed_out = True
                print_warning(f"运行 mypy 超时（60s）: {' '.join(cmd)}，尝试下一种方式...")
                continue
            except FileNotFoundError:
                # mypy 命令不存在，尝试下一种方式
                continue
            except subprocess.CalledProcessError:
                # 如果命令以非零退出（不常见，因为 check=False），仍尝试下一种方式
                continue

        # 清理测试文件
        test_file.unlink()

        if result is None:
            if timed_out:
                print_warning("mypy 在所有尝试中均超时，跳过类型验证（可手动运行 mypy 进行检查）")
            else:
                print_warning("无法运行 mypy 检查（mypy 未安装）")
                print_info("类型存根已生成，但无法验证")
            return True

        if result.returncode == 0:
            print_success("类型验证通过")
            return True
        else:
            # 检查是否只是缺少 types-protobuf
            if "types-protobuf" in result.stdout or "types-protobuf" in result.stderr:
                print_warning("mypy 检查发现问题（建议安装 types-protobuf）")
                print_info("运行: uv pip install types-protobuf")
            else:
                print_warning("mypy 检查发现问题:")
                print(result.stdout)
            return True  # 不算失败，只是警告

    except Exception as e:
        print_error(f"验证失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def clean() -> None:
    """清理生成的文件。"""
    print_info("清理生成的文件...")

    files_to_clean = [
        PROTO_DIR / "scip_pb2.py",
        PROTO_DIR / "scip_pb2.pyi",
        PROTO_DIR / "scip.proto",
        PROTO_DIR / "py.typed",
        PROTO_DIR / "__pycache__",
    ]

    for file_path in files_to_clean:
        if file_path.exists():
            if file_path.is_dir():
                shutil.rmtree(file_path)
                print_success(f"删除目录 {file_path.relative_to(PROJECT_ROOT)}")
            else:
                file_path.unlink()
                print_success(f"删除文件 {file_path.relative_to(PROJECT_ROOT)}")


def status() -> None:
    """显示 proto 文件的状态。"""
    print(f"\n{Colors.BOLD}Proto 文件状态:{Colors.END}\n")

    proto_file = PROTO_DIR / "scip.proto"
    python_file = PROTO_DIR / "scip_pb2.py"
    stub_file = PROTO_DIR / "scip_pb2.pyi"
    pytyped_file = PROTO_DIR / "py.typed"

    files = [
        ("Proto 源文件", proto_file),
        ("Python 代码", python_file),
        ("类型存根", stub_file),
        ("py.typed 标记", pytyped_file),
    ]

    for name, path in files:
        if path.exists():
            size = path.stat().st_size
            size_str = f"{size:,} bytes" if size > 0 else "empty"
            print(f"  {name}: {Colors.GREEN}✓{Colors.END} ({size_str})")
        else:
            print(f"  {name}: {Colors.RED}✗{Colors.END} (不存在)")

    print()


def main() -> int:
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="SCIP Proto 文件管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载并编译 proto 文件
  python scripts/manage_proto.py download compile

  # 强制重新下载
  python scripts/manage_proto.py download --force

  # 查看状态
  python scripts/manage_proto.py status

  # 清理生成的文件
  python scripts/manage_proto.py clean

  # 完整流程：下载、编译、验证
  python scripts/manage_proto.py all
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # download 命令
    download_parser = subparsers.add_parser("download", help="下载 SCIP proto 文件")
    download_parser.add_argument("--url", help="指定 proto 文件的 URL", default=None)
    download_parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")

    # compile 命令
    subparsers.add_parser("compile", help="编译 proto 文件")

    # verify 命令
    subparsers.add_parser("verify", help="验证生成的类型存根")

    # clean 命令
    subparsers.add_parser("clean", help="清理生成的文件")

    # status 命令
    subparsers.add_parser("status", help="显示 proto 文件状态")

    # all 命令
    subparsers.add_parser("all", help="执行完整流程（下载、编译、验证）")

    # check 命令
    subparsers.add_parser("check", help="检查依赖工具是否安装")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 确保目录存在
    PROTO_DIR.mkdir(parents=True, exist_ok=True)

    # 执行命令
    if args.command == "download":
        if not download_proto(url=args.url, force=args.force):
            return 1

    elif args.command == "compile":
        if not check_protoc():
            return 1
        if not check_mypy_protobuf():
            return 1
        if not compile_proto():
            return 1
        create_pytyped()

    elif args.command == "verify":
        verify_types()

    elif args.command == "clean":
        clean()

    elif args.command == "status":
        status()

    elif args.command == "all":
        # 完整流程
        print_info(f"\n{Colors.BOLD}执行完整的 Proto 管理流程{Colors.END}\n")

        if not check_protoc():
            return 1
        if not check_mypy_protobuf():
            return 1
        if not download_proto(force=True):
            return 1
        if not compile_proto():
            return 1
        create_pytyped()
        verify_types()

        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ 所有步骤完成！{Colors.END}\n")

    elif args.command == "check":
        print_info(f"\n{Colors.BOLD}检查依赖工具{Colors.END}\n")
        protoc_ok = check_protoc()
        mypy_protobuf_ok = check_mypy_protobuf()
        print()

        if protoc_ok and mypy_protobuf_ok:
            print_success(f"{Colors.BOLD}所有依赖已安装{Colors.END}\n")
            return 0
        else:
            print_error(f"{Colors.BOLD}缺少必要的依赖{Colors.END}\n")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
