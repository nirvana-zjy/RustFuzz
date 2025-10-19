"""
全局变量
"""

from enum import Enum
from pathlib import Path


# ==================== 基础信息 ====================
class SupportedLanguages(Enum):
    """
    支持的编程语言
    """
    NONE = "none"
    RUST = "rust"


rustfuzz_path: Path = None

# ==================== 配置 ====================

# RustFuzz 配置
config = dict()

# 库配置
libraries = dict()

# ==================== 当前目标库 ====================

# 目标库名称
library_name = ""

# 目标库语言
library_language = SupportedLanguages.RUST

# 目标库配置
library_config = dict()
