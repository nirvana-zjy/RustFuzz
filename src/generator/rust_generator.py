"""
Rust Fuzz Target 生成器
"""

import random
from pathlib import Path
from loguru import logger
from typing import List, Dict


class RustFuzzGenerator:
    """
    Rust Fuzz Target 生成器
    """
    
    def __init__(self, llm_client, analysis_results: dict, config: dict):
        """
        初始化生成器
        
        :param llm_client: LLM 客户端
        :param analysis_results: 代码分析结果
        :param config: 配置
        """
        self.llm_client = llm_client
        self.analysis_results = analysis_results
        self.config = config
        self.functions = analysis_results.get("functions", [])
        self.structs = analysis_results.get("structs", [])
        self.enums = analysis_results.get("enums", [])
    
    def select_functions(self, target_functions: List[str], function_set_size: int = 3) -> List[str]:
        """
        选择要测试的函数集合
        
        :param target_functions: 目标函数列表
        :param function_set_size: 函数集合大小
        :return: 选中的函数列表
        """
        if len(target_functions) <= function_set_size:
            return target_functions
        return random.sample(target_functions, function_set_size)
    
    def generate_fuzz_target(self, selected_functions: List[str]) -> str:
        """
        生成 fuzz target 代码
        
        :param selected_functions: 选中的函数列表
        :return: 生成的代码
        """
        # 收集函数信息
        func_infos = []
        for func_name in selected_functions:
            func_info = self._get_function_info(func_name)
            if func_info:
                func_infos.append(func_info)
        
        if not func_infos:
            raise ValueError("未找到任何有效函数")
        
        # 使用 LLM 生成代码
        prompt = self._build_prompt(func_infos)
        generated_code = self.llm_client.generate(prompt)
        
        # 后处理
        final_code = self._post_process(generated_code)
        
        return final_code
    
    def _get_function_info(self, func_name: str) -> Dict:
        """
        获取函数信息
        """
        for func in self.functions:
            if func["name"] == func_name:
                return func
        return None
    
    def _build_prompt(self, func_infos: List[Dict]) -> str:
        """
        构建 LLM prompt
        """
        prompt = f"""你是一个 Rust fuzzing 专家。请为以下函数生成一个 fuzz target。

要求:
1. 使用 libfuzzer (cargo-fuzz) 格式
2. 正确处理 Rust 的所有权和生命周期
3. 生成合理的测试输入
4. 处理可能的错误情况
5. 使用 arbitrary crate 生成结构化输入

目标函数:
"""
        
        for func in func_infos:
            prompt += f"\n函数名: {func['name']}\n"
            prompt += f"参数: {func['params']}\n"
            prompt += f"返回类型: {func['return_type']}\n"
            if func.get('doc_comment'):
                prompt += f"文档: {func['doc_comment']}\n"
            prompt += "\n"
        
        prompt += """
请生成完整的 fuzz target 代码，包括:
1. 必要的 use 语句
2. fuzz_target! 宏定义
3. 输入数据解析
4. 函数调用
5. 错误处理

代码格式:
```rust
// fuzz target 代码
```
"""
        
        return prompt
    
    def _post_process(self, generated_code: str) -> str:
        """
        后处理生成的代码
        """
        # 提取代码块
        if "```rust" in generated_code:
            start = generated_code.find("```rust") + 7
            end = generated_code.find("```", start)
            generated_code = generated_code[start:end].strip()
        elif "```" in generated_code:
            start = generated_code.find("```") + 3
            end = generated_code.find("```", start)
            generated_code = generated_code[start:end].strip()
        
        # 确保包含基本的 use 语句
        if "use " not in generated_code and "libfuzzer_sys" not in generated_code:
            header = """#![no_main]
use libfuzzer_sys::fuzz_target;
use arbitrary::Arbitrary;

"""
            generated_code = header + generated_code
        
        return generated_code
