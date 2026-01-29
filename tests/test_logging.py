"""
测试 debug 日志功能
"""

import logging
from io import StringIO

from scip_parser.utils.logging_config import get_logger, setup_logging


def test_basic_logging():
    """测试基本的日志功能"""
    # 设置日志输出到字符串流
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))

    logger = get_logger("test_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # 测试各个日志级别
    logger.debug("这是一条 debug 消息")
    logger.info("这是一条 info 消息")
    logger.warning("这是一条 warning 消息")
    logger.error("这是一条 error 消息")

    # 验证输出
    output = log_stream.getvalue()
    print("日志输出:")
    print(output)

    assert "debug" in output
    assert "info" in output
    assert "warning" in output
    assert "error" in output
    print("✅ 日志功能测试通过")


def test_setup_logging():
    """测试 setup_logging 函数"""
    # 设置日志级别为 DEBUG
    setup_logging(level=logging.DEBUG)

    logger = get_logger("scip_parser.test")
    # logger.level 可能是 NOTSET (0),继承根logger的level
    # 我们检查根logger的level
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

    logger.debug("测试 setup_logging")
    print("✅ setup_logging 测试通过")


def test_module_loggers():
    """测试各个模块的专用 logger"""
    from scip_parser.utils.logging_config import (
        get_index_logger,
        get_parser_logger,
        get_query_logger,
    )

    parser_logger = get_parser_logger()
    assert parser_logger.name == "scip_parser.core.parser"

    index_logger = get_index_logger()
    assert index_logger.name == "scip_parser.core.types"

    query_logger = get_query_logger()
    assert query_logger.name == "scip_parser.query.api"

    print("✅ 模块 logger 测试通过")


if __name__ == "__main__":
    test_basic_logging()
    test_setup_logging()
    test_module_loggers()
    print("\n✅ 所有测试通过")
