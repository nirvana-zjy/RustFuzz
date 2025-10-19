"""
Stats 命令 - 统计信息
"""

import click
from pathlib import Path
from loguru import logger
import json

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path


@click.command(help="显示 fuzzing 统计信息")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称"
)
@click.option(
    "--coverage",
    is_flag=True,
    help="显示覆盖率信息"
)
def stats(library_name: str, coverage: bool):
    """
    显示统计信息
    """
    setup_library_config(library_name)
    
    output_path = get_output_path()
    
    # 加载分析结果
    ast_file = output_path / "ast.json"
    if ast_file.exists():
        with open(ast_file, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        logger.info("=" * 60)
        logger.info("代码分析统计")
        logger.info("=" * 60)
        logger.info(f"函数: {len(analysis.get('functions', []))}")
        logger.info(f"结构体: {len(analysis.get('structs', []))}")
        logger.info(f"枚举: {len(analysis.get('enums', []))}")
        logger.info(f"Trait: {len(analysis.get('traits', []))}")
        logger.info(f"Unsafe 块: {len(analysis.get('unsafe_blocks', []))}")
    
    # fuzz target 统计
    fuzz_targets_dir = output_path / "fuzz_targets"
    if fuzz_targets_dir.exists():
        targets = list(fuzz_targets_dir.glob("*.rs"))
        logger.info("=" * 60)
        logger.info("Fuzz Target 统计")
        logger.info("=" * 60)
        logger.info(f"已生成: {len(targets)}")
    
    if coverage:
        logger.info("=" * 60)
        logger.info("覆盖率统计")
        logger.info("=" * 60)
        logger.info("覆盖率功能开发中...")
