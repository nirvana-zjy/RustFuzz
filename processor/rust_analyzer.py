"""
Rust 代码分析器
基于 tree-sitter 解析 Rust 代码
"""

import json
from pathlib import Path
from loguru import logger
from tree_sitter import Language, Parser, Node
import tree_sitter_rust as ts_rust


class RustAnalyzer:
    """
    Rust 代码分析器
    """
    
    def __init__(self, crate_path: Path):
        """
        初始化分析器
        
        :param crate_path: Crate 路径
        """
        self.crate_path = crate_path
        self.language = Language(ts_rust.language())
        self.parser = Parser(self.language)
    
    def analyze_file(self, file_path: Path) -> dict:
        """
        分析单个 Rust 文件
        
        :param file_path: 文件路径
        :return: 分析结果
        """
        try:
            code = file_path.read_text(encoding="utf-8")
            tree = self.parser.parse(code.encode())
            
            result = {
                "file": str(file_path.relative_to(self.crate_path)),
                "functions": [],
                "structs": [],
                "enums": [],
                "traits": [],
                "impls": [],
                "unsafe_blocks": [],
                "modules": []
            }
            
            self._traverse(tree.root_node, result, code)
            return result
            
        except Exception as e:
            logger.error(f"分析文件失败 {file_path}: {e}")
            return {}
    
    def _traverse(self, node: Node, result: dict, code: str):
        """
        遍历 AST 节点
        """
        if node.type == "function_item":
            self._extract_function(node, result, code)
        elif node.type == "struct_item":
            self._extract_struct(node, result, code)
        elif node.type == "enum_item":
            self._extract_enum(node, result, code)
        elif node.type == "trait_item":
            self._extract_trait(node, result, code)
        elif node.type == "impl_item":
            self._extract_impl(node, result, code)
        elif node.type == "unsafe_block":
            self._extract_unsafe_block(node, result, code)
        elif node.type == "mod_item":
            self._extract_module(node, result, code)
        
        # 递归遍历子节点
        for child in node.children:
            self._traverse(child, result, code)
    
    def _extract_function(self, node: Node, result: dict, code: str):
        """提取函数信息"""
        func_info = {
            "name": self._get_name(node),
            "is_pub": self._is_pub(node),
            "is_unsafe": self._is_unsafe(node),
            "params": self._get_params(node),
            "return_type": self._get_return_type(node),
            "doc_comment": self._get_doc_comment(node, code),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["functions"].append(func_info)
    
    def _extract_struct(self, node: Node, result: dict, code: str):
        """提取结构体信息"""
        struct_info = {
            "name": self._get_name(node),
            "is_pub": self._is_pub(node),
            "fields": self._get_fields(node),
            "doc_comment": self._get_doc_comment(node, code),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["structs"].append(struct_info)
    
    def _extract_enum(self, node: Node, result: dict, code: str):
        """提取枚举信息"""
        enum_info = {
            "name": self._get_name(node),
            "is_pub": self._is_pub(node),
            "variants": self._get_enum_variants(node),
            "doc_comment": self._get_doc_comment(node, code),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["enums"].append(enum_info)
    
    def _extract_trait(self, node: Node, result: dict, code: str):
        """提取 trait 信息"""
        trait_info = {
            "name": self._get_name(node),
            "is_pub": self._is_pub(node),
            "methods": self._get_trait_methods(node),
            "doc_comment": self._get_doc_comment(node, code),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["traits"].append(trait_info)
    
    def _extract_impl(self, node: Node, result: dict, code: str):
        """提取 impl 块信息"""
        impl_info = {
            "type": self._get_impl_type(node),
            "trait": self._get_impl_trait(node),
            "methods": self._get_impl_methods(node),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["impls"].append(impl_info)
    
    def _extract_unsafe_block(self, node: Node, result: dict, code: str):
        """提取 unsafe 块信息"""
        unsafe_info = {
            "code": code[node.start_byte:node.end_byte],
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["unsafe_blocks"].append(unsafe_info)
    
    def _extract_module(self, node: Node, result: dict, code: str):
        """提取模块信息"""
        mod_info = {
            "name": self._get_name(node),
            "is_pub": self._is_pub(node),
            "location": {
                "start": node.start_point,
                "end": node.end_point
            }
        }
        result["modules"].append(mod_info)
    
    def _get_name(self, node: Node) -> str:
        """获取名称"""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode()
        return ""
    
    def _is_pub(self, node: Node) -> bool:
        """检查是否为公开"""
        for child in node.children:
            if child.type == "visibility_modifier":
                return child.text.decode() == "pub"
        return False
    
    def _is_unsafe(self, node: Node) -> bool:
        """检查是否为 unsafe"""
        for child in node.children:
            if child.type == "unsafe":
                return True
        return False
    
    def _get_params(self, node: Node) -> list:
        """获取函数参数"""
        params = []
        for child in node.children:
            if child.type == "parameters":
                for param in child.children:
                    if param.type == "parameter":
                        params.append({
                            "name": self._get_param_name(param),
                            "type": self._get_param_type(param)
                        })
        return params
    
    def _get_param_name(self, param_node: Node) -> str:
        """获取参数名"""
        for child in param_node.children:
            if child.type == "identifier":
                return child.text.decode()
        return ""
    
    def _get_param_type(self, param_node: Node) -> str:
        """获取参数类型"""
        for i, child in enumerate(param_node.children):
            if child.type == ":":
                if i + 1 < len(param_node.children):
                    return param_node.children[i + 1].text.decode()
        return ""
    
    def _get_return_type(self, node: Node) -> str:
        """获取返回类型"""
        for child in node.children:
            if child.type == "->":
                next_sibling = child.next_sibling
                if next_sibling:
                    return next_sibling.text.decode()
        return "()"
    
    def _get_fields(self, node: Node) -> list:
        """获取结构体字段"""
        fields = []
        for child in node.children:
            if child.type == "field_declaration_list":
                for field in child.children:
                    if field.type == "field_declaration":
                        fields.append({
                            "name": self._get_name(field),
                            "type": self._get_field_type(field),
                            "is_pub": self._is_pub(field)
                        })
        return fields
    
    def _get_field_type(self, field_node: Node) -> str:
        """获取字段类型"""
        for child in field_node.children:
            if child.type == ":":
                next_sibling = child.next_sibling
                if next_sibling:
                    return next_sibling.text.decode()
        return ""
    
    def _get_enum_variants(self, node: Node) -> list:
        """获取枚举变体"""
        variants = []
        for child in node.children:
            if child.type == "enum_variant_list":
                for variant in child.children:
                    if variant.type == "enum_variant":
                        variants.append(self._get_name(variant))
        return variants
    
    def _get_trait_methods(self, node: Node) -> list:
        """获取 trait 方法"""
        # 简化实现
        return []
    
    def _get_impl_type(self, node: Node) -> str:
        """获取 impl 的类型"""
        for child in node.children:
            if child.type == "type_identifier":
                return child.text.decode()
        return ""
    
    def _get_impl_trait(self, node: Node) -> str:
        """获取 impl 的 trait"""
        for child in node.children:
            if child.type == "for":
                next_sibling = child.next_sibling
                if next_sibling:
                    return next_sibling.text.decode()
        return ""
    
    def _get_impl_methods(self, node: Node) -> list:
        """获取 impl 方法"""
        # 简化实现
        return []
    
    def _get_doc_comment(self, node: Node, code: str) -> str:
        """获取文档注释"""
        # 查找节点前的注释
        start_line = node.start_point[0]
        lines = code.split('\n')
        
        doc_lines = []
        for i in range(start_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("///") or line.startswith("//!"):
                doc_lines.insert(0, line)
            elif line:
                break
        
        return '\n'.join(doc_lines)
