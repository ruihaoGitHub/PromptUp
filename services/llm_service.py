"""
LLM 服务
负责 LLM 的初始化和配置
"""
import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA


class LLMService:
    """LLM 初始化和管理服务"""
    
    @staticmethod
    def create_llm(
        provider: Literal["openai", "nvidia"] = "nvidia",
        api_key: Optional[str] = None,
        model: str = "meta/llama-3.1-405b-instruct",
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        创建并配置 LLM 实例
        
        Args:
            provider: API 提供商 ("openai" 或 "nvidia")
            api_key: API Key，如果不提供则从环境变量读取
            model: 使用的模型名称
            base_url: API base URL（可选）
            temperature: 温度参数（控制输出随机性）
            top_p: Top-p 采样参数
            max_tokens: 最大生成 token 数
            
        Returns:
            配置好的 LLM 实例（ChatOpenAI 或 ChatNVIDIA）
            
        Raises:
            ValueError: 当 provider 不是 "openai" 或 "nvidia" 时
        """
        if provider == "nvidia":
            return LLMService._create_nvidia_llm(
                api_key=api_key,
                model=model,
                base_url=base_url,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        elif provider == "openai":
            return LLMService._create_openai_llm(
                api_key=api_key,
                model=model,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"不支持的 provider: {provider}。请使用 'openai' 或 'nvidia'")
    
    @staticmethod
    def _create_nvidia_llm(
        api_key: Optional[str],
        model: str,
        base_url: Optional[str],
        temperature: float,
        top_p: float,
        max_tokens: int
    ):
        """创建 NVIDIA LLM 实例"""
        # 设置 API Key 到环境变量
        if api_key:
            os.environ["NVIDIA_API_KEY"] = api_key
        
        # 构建参数
        llm_params = {
            "model": model,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        
        # 如果提供了 base_url，添加到参数中
        if base_url:
            llm_params["base_url"] = base_url
        
        return ChatNVIDIA(**llm_params)
    
    @staticmethod
    def _create_openai_llm(
        api_key: Optional[str],
        model: str,
        base_url: Optional[str],
        temperature: float,
        max_tokens: int
    ):
        """创建 OpenAI LLM 实例"""
        # 设置 API Key 到环境变量
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # 构建参数
        llm_params = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # 如果提供了 base_url，添加到参数中
        if base_url:
            llm_params["base_url"] = base_url
        
        return ChatOpenAI(**llm_params)
    
    @staticmethod
    def supports_json_mode(provider: str) -> bool:
        """
        检查提供商是否支持 JSON mode
        
        Args:
            provider: API 提供商名称
            
        Returns:
            bool: True 表示支持 JSON mode
        """
        return provider.lower() == "openai"
