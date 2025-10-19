"""
Analyze 命令 - 分析 Fuzzing 结果
"""

import click
from pathlib import Path
from loguru import logger
import json

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path


@click.command(help="分析 fuzzing 结果和 crash")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称"
)
def analyze(library_name: str):
    """
    分析 fuzzing 结果
    """
    setup_library_config(library_name)
    
    output_path = get_output_path()
    fuzz_project_dir = output_path / "fuzz_project"
    
    if not fuzz_project_dir.exists():
        logger.error("未找到 fuzz 项目")
        return
    
    # 分析 artifacts
    artifacts_dir = fuzz_project_dir / "fuzz" / "artifacts"
    if not artifacts_dir.exists():
        logger.info("未发现任何 crash")
        return
    
    crashes = list(artifacts_dir.rglob("*"))
    logger.info(f"发现 {len(crashes)} 个 crash")
    
    # 分析每个 crash
    crash_reports = []
    for crash in crashes:
        if crash.is_file():
            logger.info(f"分析 crash: {crash.name}")
            
            report = {
                "file": crash.name,
                "path": str(crash),
                "size": crash.stat().st_size
            }
            crash_reports.append(report)
    
    # 保存报告
    report_file = output_path / "crash_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(crash_reports, f, indent=2)
    
    logger.info(f"分析报告已保存至: {report_file}")
