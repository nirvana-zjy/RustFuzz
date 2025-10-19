#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RustFuzz - Rust 漏洞挖掘工具
基于 PromeFuzz 改进，专门针对 Rust 生态系统优化
"""

import sys
import tomllib
import click
import importlib
from pathlib import Path
from loguru import logger
import datetime
import tqdm

from src import vars as global_vars

SUBCOMMANDS = (
    "configure",
    "preprocess",
    "comprehend",
    "generate",
    "fuzz",
    "analyze",
    "stats",
)


def setup_subcommands():
    """
    导入命令行模块并添加命令
    """
    for cmd in SUBCOMMANDS:
        try:
            module = importlib.import_module(f"cli.{cmd}")
            method = getattr(module, cmd)
            butler.add_command(method)
        except ImportError as e:
            logger.warning(f"无法导入命令 {cmd}: {e}")


def setup_logger(debug: bool):
    """
    设置日志级别

    :param debug: 如果为 True，设置日志级别为 DEBUG
    """
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(
        sink=tqdm.tqdm.write,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <magenta>{thread.name}</magenta> <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        colorize=True,
    )
    Path("logs").mkdir(exist_ok=True)
    log_filename = f"logs/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{'_'.join(sys.argv).replace(' ', '_').replace('/', '_')}.log"
    if len(log_filename) > 255:
        log_filename = log_filename[:200] + ".log"
    logger.add(
        log_filename,
        level=level,
        enqueue=True,
        format="{time} | {thread.name} {level} | {name}:{function}:{line} | {message}",
        colorize=False,
    )
    logger.info(
        f"日志系统已设置，级别: {level}，日志文件: {log_filename}"
    )


def load_config(config_path: Path, library_path: Path):
    """
    加载 config.toml 和 libraries.toml

    :param config_path: RustFuzz 配置文件路径
    :param library_path: 库配置文件路径
    """
    help_flags = {"--help"}
    if any(arg in help_flags for arg in sys.argv[1:]):
        logger.debug("检测到帮助标志，跳过配置加载")
        return

    if click.get_current_context().invoked_subcommand == "configure":
        global_vars.config = {}
        global_vars.libraries = {}
        return

    try:
        if not config_path.exists():
            logger.error(f"配置文件未找到: {config_path}")
            logger.info("运行 'python RustFuzz.py configure' 创建配置文件")
            sys.exit(1)
        if not library_path.exists():
            logger.error(f"库配置文件未找到: {library_path}")
            sys.exit(1)

        global_vars.config = tomllib.loads(config_path.read_text())
        global_vars.libraries = tomllib.loads(library_path.read_text())

        logger.info("配置加载成功")
        logger.debug(f"已加载 {len(global_vars.libraries)} 个库配置")

    except Exception as e:
        logger.error(f"加载配置时出错: {e}")
        sys.exit(1)


@click.group(name="RustFuzz", invoke_without_command=False)
@click.option(
    "-D",
    "--debug",
    is_flag=True,
    default=False,
    help="启用调试模式，输出详细日志",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=False, path_type=Path),
    default=Path("config.toml"),
    help="配置文件路径",
    show_default=True,
)
@click.option(
    "-l",
    "--libraries",
    "library_path",
    type=click.Path(exists=False, path_type=Path),
    default=Path("libraries.toml"),
    help="库配置文件路径",
    show_default=True,
)
@click.pass_context
def butler(ctx: click.Context, debug: bool, config_path: Path, library_path: Path):
    """
    RustFuzz - 基于 LLM 的 Rust 漏洞挖掘工具

    自动生成 Rust Fuzz Harness，发现潜在的安全漏洞
    """
    global_vars.promefuzz_path = Path(__file__).parent.resolve()
    setup_logger(debug)
    load_config(config_path, library_path)


def main():
    """
    主入口函数
    """
    setup_subcommands()
    butler()


if __name__ == "__main__":
    main()
