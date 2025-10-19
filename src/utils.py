"""
工具函数
"""

import sys
from pathlib import Path
from loguru import logger

from . import vars as global_vars


def setup_library_config(library_name: str):
    """
    设置目标库配置
    
    :param library_name: 库名称
    """
    if not library_name:
        if len(global_vars.libraries) == 1:
            library_name = list(global_vars.libraries.keys())[0]
            logger.info(f"自动选择库: {library_name}")
        else:
            logger.error("请指定目标库名称（使用 -L 或 --library 选项）")
            logger.info(f"可用的库: {', '.join(global_vars.libraries.keys())}")
            sys.exit(1)
    
    if library_name not in global_vars.libraries:
        logger.error(f"库 '{library_name}' 未在 libraries.toml 中配置")
        logger.info(f"可用的库: {', '.join(global_vars.libraries.keys())}")
        sys.exit(1)
    
    global_vars.library_name = library_name
    global_vars.library_config = global_vars.libraries[library_name]
    global_vars.library_language = global_vars.SupportedLanguages.RUST
    
    logger.info(f"已选择目标库: {library_name}")
    logger.debug(f"库配置: {global_vars.library_config}")


def get_output_path() -> Path:
    """
    获取输出路径
    
    :return: 输出路径
    """
    output_path = Path(global_vars.library_config.get("output_path", f"output/{global_vars.library_name}"))
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_crate_path() -> Path:
    """
    获取 crate 路径
    
    :return: crate 路径
    """
    crate_path = Path(global_vars.library_config["crate_path"])
    if not crate_path.exists():
        logger.error(f"Crate 路径不存在: {crate_path}")
        sys.exit(1)
    return crate_path


def setup_llm(llm_name: str = ""):
    """
    设置 LLM 客户端
    
    :param llm_name: LLM 名称
    :return: LLM 客户端
    """
    from .llm.llm import LLMClient
    
    llm_config = global_vars.config.get("llm", {})
    
    if llm_config.get("use_ollama", False):
        return LLMClient(
            provider="ollama",
            model=llm_config.get("ollama_model", "codellama:13b"),
            host=llm_config.get("ollama_host", "http://localhost:11434")
        )
    else:
        return LLMClient(
            provider="openai",
            model=llm_config.get("openai_model", "gpt-4"),
            api_key=llm_config.get("openai_api_key", ""),
            api_base=llm_config.get("openai_api_base", "https://api.openai.com/v1")
        )
