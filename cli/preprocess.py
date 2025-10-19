"""
Preprocess 命令 - 预处理 Rust 代码
"""

import click
from pathlib import Path
from loguru import logger
from tqdm import tqdm
import json

from src import vars as global_vars
from src.utils import setup_library_config, get_output_path, get_crate_path


@click.command(help="分析 Rust crate 的代码结构")
@click.option(
    "-L",
    "--library",
    "library_name",
    default=None,
    help="目标库名称（在 libraries.toml 中配置）"
)
@click.option(
    "--force",
    is_flag=True,
    help="强制重新分析，即使已有分析结果"
)
def preprocess(library_name: str, force: bool):
    """
    预处理命令 - 分析 Rust 代码结构
    """
    setup_library_config(library_name)
    
    output_path = get_output_path()
    crate_path = get_crate_path()
    
    logger.info(f"开始预处理 crate: {crate_path}")
    
    # 检查是否已有分析结果
    ast_file = output_path / "ast.json"
    if ast_file.exists() and not force:
        logger.info("检测到已有分析结果，使用 --force 强制重新分析")
        return
    
    # 导入 Rust 分析器
    from processor.rust_analyzer import RustAnalyzer
    
    analyzer = RustAnalyzer(crate_path)
    
    # 分析源代码
    logger.info("正在分析源代码...")
    source_paths = global_vars.library_config.get("source_paths", ["src"])
    
    results = {
        "functions": [],
        "structs": [],
        "enums": [],
        "traits": [],
        "impls": [],
        "unsafe_blocks": [],
        "modules": []
    }
    
    for src_path in source_paths:
        full_path = crate_path / src_path
        if not full_path.exists():
            logger.warning(f"源代码路径不存在: {full_path}")
            continue
        
        logger.info(f"分析路径: {full_path}")
        rs_files = list(full_path.rglob("*.rs"))
        
        for rs_file in tqdm(rs_files, desc="分析 Rust 文件"):
            try:
                file_results = analyzer.analyze_file(rs_file)
                
                results["functions"].extend(file_results.get("functions", []))
                results["structs"].extend(file_results.get("structs", []))
                results["enums"].extend(file_results.get("enums", []))
                results["traits"].extend(file_results.get("traits", []))
                results["impls"].extend(file_results.get("impls", []))
                results["unsafe_blocks"].extend(file_results.get("unsafe_blocks", []))
                results["modules"].extend(file_results.get("modules", []))
                
            except Exception as e:
                logger.error(f"分析文件失败 {rs_file}: {e}")
    
    # 保存结果
    logger.info("保存分析结果...")
    with open(output_path / "ast.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 统计信息
    logger.info("=" * 60)
    logger.info("预处理完成!")
    logger.info(f"函数数量: {len(results['functions'])}")
    logger.info(f"结构体数量: {len(results['structs'])}")
    logger.info(f"枚举数量: {len(results['enums'])}")
    logger.info(f"Trait 数量: {len(results['traits'])}")
    logger.info(f"Impl 块数量: {len(results['impls'])}")
    logger.info(f"Unsafe 块数量: {len(results['unsafe_blocks'])}")
    logger.info(f"模块数量: {len(results['modules'])}")
    logger.info(f"结果保存至: {output_path}")
    logger.info("=" * 60)
