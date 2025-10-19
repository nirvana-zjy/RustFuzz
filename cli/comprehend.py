"""
Comprehend 命令 - 理解 API 语义
"""

import click
from pathlib import Path
from loguru import logger

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path


@click.command(help="使用 LLM 理解 API 语义和使用方式")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称"
)
def comprehend(library_name: str):
    """
    理解 API 语义
    """
    setup_library_config(library_name)
    
    logger.info("Comprehend 功能开发中...")
    logger.info("该功能将使用 LLM 理解 API 的语义和使用方式")
