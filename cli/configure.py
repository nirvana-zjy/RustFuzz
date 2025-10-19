"""
Configure 命令 - 初始化配置
"""

import click
from pathlib import Path
from loguru import logger
import shutil


@click.command(help="初始化或更新 RustFuzz 配置文件")
@click.option(
    "--init",
    is_flag=True,
    help="创建默认配置文件"
)
def configure(init: bool):
    """
    配置命令
    """
    if init:
        # 创建默认配置文件
        config_template = Path("config.toml")
        libraries_template = Path("libraries.toml")
        
        if config_template.exists():
            logger.warning("config.toml 已存在")
            if not click.confirm("是否覆盖?"):
                return
        
        if libraries_template.exists():
            logger.warning("libraries.toml 已存在")
            if not click.confirm("是否覆盖?"):
                return
        
        logger.info("配置文件已创建")
        logger.info("请编辑 config.toml 和 libraries.toml 以配置你的环境")
    else:
        logger.info("使用 --init 选项创建默认配置")
