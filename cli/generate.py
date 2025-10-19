"""
Generate 命令 - 生成 Fuzz Target
"""

import click
from pathlib import Path
from loguru import logger
from tqdm import tqdm
import json

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path, setup_llm


@click.command(help="使用 LLM 生成 fuzz target")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称"
)
@click.option(
    "--count",
    type=int,
    default=10,
    help="生成的 fuzz target 数量"
)
@click.option(
    "--task",
    type=click.Choice(["given", "autoscale", "allcover"]),
    default="allcover",
    help="生成任务类型"
)
@click.option(
    "--functions",
    type=str,
    default="",
    help="指定要测试的函数（逗号分隔）"
)
def generate(library_name: str, count: int, task: str, functions: str):
    """
    生成 fuzz target
    """
    setup_library_config(library_name)
    
    output_path = get_output_path()
    
    # 检查预处理结果
    ast_file = output_path / "ast.json"
    if not ast_file.exists():
        logger.error("未找到预处理结果，请先运行 preprocess 命令")
        return
    
    logger.info("加载分析结果...")
    with open(ast_file, "r", encoding="utf-8") as f:
        analysis_results = json.load(f)
    
    # 设置 LLM
    logger.info("初始化 LLM...")
    llm_client = setup_llm()
    
    # 创建生成器
    from src.generator.rust_generator import RustFuzzGenerator
    
    generator = RustFuzzGenerator(
        llm_client=llm_client,
        analysis_results=analysis_results,
        config=global_vars.config
    )
    
    # 准备目标函数列表
    target_functions = []
    if task == "given" and functions:
        target_functions = [f.strip() for f in functions.split(",")]
    elif task == "allcover":
        # 覆盖所有公开函数
        all_funcs = analysis_results.get("functions", [])
        target_functions = [f["name"] for f in all_funcs if f.get("is_pub", False)]
    elif task == "autoscale":
        # 自动缩放
        all_funcs = analysis_results.get("functions", [])
        target_functions = [f["name"] for f in all_funcs if f.get("is_pub", False)]
        count = min(count, len(target_functions))
    
    logger.info(f"目标函数数量: {len(target_functions)}")
    
    # 创建 fuzz_targets 目录
    fuzz_targets_dir = output_path / "fuzz_targets"
    fuzz_targets_dir.mkdir(exist_ok=True)
    
    # 生成 fuzz target
    logger.info(f"开始生成 {count} 个 fuzz target...")
    
    generated_count = 0
    for i in tqdm(range(count), desc="生成 fuzz target"):
        try:
            # 选择函数集合
            selected_funcs = generator.select_functions(
                target_functions,
                function_set_size=global_vars.config.get("generator", {}).get("function_set_size", 3)
            )
            
            # 生成代码
            fuzz_code = generator.generate_fuzz_target(selected_funcs)
            
            # 保存
            target_file = fuzz_targets_dir / f"fuzz_target_{i+1}.rs"
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(fuzz_code)
            
            generated_count += 1
            
        except Exception as e:
            logger.error(f"生成 fuzz target {i+1} 失败: {e}")
    
    logger.info("=" * 60)
    logger.info(f"成功生成 {generated_count} 个 fuzz target")
    logger.info(f"保存位置: {fuzz_targets_dir}")
    logger.info("=" * 60)
