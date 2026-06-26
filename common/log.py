"""
日志模块

提供统一的日志配置和管理。
企业级设计：支持日志级别配置、日志文件轮转、结构化日志。

Usage:
    from common.log import logger

    logger.info("这是一条信息")
    logger.error("这是一条错误", exc_info=True)
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path


def setup_logger(
    name: str = "ai_service",
    log_file: str = "logs/app.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    配置日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的旧日志文件数量
        console_output: 是否输出到控制台

    Returns:
        配置好的日志记录器
    """
    # 创建日志记录器
    log = logging.getLogger(name)

    # 避免重复添加handler
    if log.handlers:
        return log

    log.setLevel(level)

    # 日志格式
    formatter = logging.Formatter(
        "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 文件handler（支持日志轮转）
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Failed to create log file handler: {e}", file=sys.stderr)

    # 控制台handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)

    # 阻止日志向上传播
    log.propagate = False

    return log


# 创建默认日志记录器
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """
    获取子日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        子日志记录器

    Example:
        ```python
        from common.log import get_logger

        logger = get_logger(__name__)
        logger.info("这是一条信息")
        ```
    """
    return logging.getLogger(f"ai_service.{name}")
