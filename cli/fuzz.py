"""
Fuzz 命令 - 运行 Fuzzing
"""

import click
from pathlib import Path
from loguru import logger
import subprocess
import time

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path, get_crate_path


@click.command(help="运行 cargo-fuzz 进行 fuzzing 测试")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称"
)
@click.option(
    "--target",
    type=str,
    default="",
    help="指定要运行的 fuzz target"
)
@click.option(
    "--timeout",
    type=int,
    default=3600,
    help="运行时间（秒）"
)
@click.option(
    "--jobs",
    type=int,
    default=0,
    help="并行任务数（0 表示自动）"
)
def fuzz(library_name: str, target: str, timeout: int, jobs: int):
    """
    运行 fuzzing
    """
    setup_library_config(library_name)
    
    output_path = get_output_path()
    crate_path = get_crate_path()
    
    fuzz_targets_dir = output_path / "fuzz_targets"
    if not fuzz_targets_dir.exists():
        logger.error("未找到 fuzz target，请先运行 generate 命令")
        return
    
    # 设置 fuzz 项目
    fuzz_project_dir = output_path / "fuzz_project"
    if not fuzz_project_dir.exists():
        logger.info("初始化 cargo-fuzz 项目...")
        setup_fuzz_project(crate_path, fuzz_project_dir, fuzz_targets_dir)
    
    # 获取要运行的 target
    if target:
        targets = [target]
    else:
        targets = [f.stem for f in fuzz_targets_dir.glob("*.rs")]
    
    logger.info(f"准备运行 {len(targets)} 个 fuzz target")
    
    # 运行 fuzzing
    for target_name in targets:
        logger.info(f"运行 fuzz target: {target_name}")
        
        cmd = [
            "cargo", "fuzz", "run", target_name,
            "--", f"-max_total_time={timeout}"
        ]
        
        if jobs > 0:
            cmd.extend([f"-jobs={jobs}"])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=fuzz_project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Fuzzing 失败: {result.stderr}")
            else:
                logger.info(f"Fuzzing 完成: {target_name}")
                
        except Exception as e:
            logger.error(f"运行 fuzzing 失败: {e}")


def setup_fuzz_project(crate_path: Path, fuzz_project_dir: Path, fuzz_targets_dir: Path):
    """
    设置 cargo-fuzz 项目
    """
    fuzz_project_dir.mkdir(exist_ok=True)
    
    # 初始化 fuzz 项目
    logger.info("运行 cargo fuzz init...")
    subprocess.run(
        ["cargo", "fuzz", "init"],
        cwd=fuzz_project_dir,
        check=True
    )
    
    # 复制 fuzz target
    logger.info("复制 fuzz target...")
    fuzz_dir = fuzz_project_dir / "fuzz" / "fuzz_targets"
    fuzz_dir.mkdir(parents=True, exist_ok=True)
    
    for target_file in fuzz_targets_dir.glob("*.rs"):
        import shutil
        shutil.copy(target_file, fuzz_dir / target_file.name)
    
    logger.info("Fuzz 项目设置完成")
