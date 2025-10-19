"""
LLM 客户端
支持 OpenAI 和 Ollama
"""

from loguru import logger
from typing import Optional


class LLMClient:
    """
    LLM 客户端
    """
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4", 
                 api_key: str = "", api_base: str = "", host: str = ""):
        """
        初始化 LLM 客户端
        
        :param provider: 提供商 (openai, ollama)
        :param model: 模型名称
        :param api_key: API 密钥
        :param api_base: API 端点
        :param host: Ollama 主机
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.host = host
        
        if provider == "openai":
            self._init_openai()
        elif provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"不支持的 provider: {provider}")
    
    def _init_openai(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            logger.info(f"OpenAI 客户端初始化成功，模型: {self.model}")
        except ImportError:
            logger.error("未安装 openai 包，请运行: pip install openai")
            raise
    
    def _init_ollama(self):
        """初始化 Ollama 客户端"""
        try:
            import ollama
            self.client = ollama
            logger.info(f"Ollama 客户端初始化成功，模型: {self.model}")
        except ImportError:
            logger.error("未安装 ollama 包，请运行: pip install ollama")
            raise
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2000) -> str:
        """
        生成文本
        
        :param prompt: 输入提示
        :param temperature: 温度参数
        :param max_tokens: 最大 token 数
        :return: 生成的文本
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, temperature, max_tokens)
            elif self.provider == "ollama":
                return self._generate_ollama(prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"生成失败: {e}")
            raise
    
    def _generate_openai(self, prompt: str, temperature: float, 
                         max_tokens: int) -> str:
        """使用 OpenAI 生成"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个 Rust fuzzing 专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt: str, temperature: float, 
                         max_tokens: int) -> str:
        """使用 Ollama 生成"""
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        return response['response']
