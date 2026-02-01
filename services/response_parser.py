"""
响应解析服务
负责解析和清理 LLM 响应
"""
import json
from typing import Any, Dict
from utils import safe_json_loads, clean_improved_prompt


class ResponseParser:
    """LLM 响应解析和清理服务"""
    
    @staticmethod
    def extract_json_from_response(content: str) -> str:
        """
        从响应中提取 JSON 内容
        
        支持处理以下格式：
        - 纯 JSON 文本
        - Markdown 代码块包裹的 JSON (```json ... ```)
        - 普通代码块包裹的 JSON (``` ... ```)
        
        Args:
            content: LLM 响应的原始文本
            
        Returns:
            str: 提取后的 JSON 文本
        """
        # 检测并提取 JSON 代码块
        if "```json" in content:
            print("🔍 检测到 JSON 代码块，正在提取...")
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            print("🔍 检测到代码块，正在提取...")
            content = content.split("```")[1].split("```")[0].strip()
        
        return content
    
    @staticmethod
    def parse_json(content: str) -> Dict[str, Any]:
        """
        解析 JSON 字符串
        
        Args:
            content: JSON 字符串
            
        Returns:
            Dict: 解析后的字典
            
        Raises:
            json.JSONDecodeError: JSON 格式错误时
        """
        print("⚙️ 正在解析 JSON...")
        result = safe_json_loads(content)
        print("✅ JSON 解析成功")
        return result
    
    @staticmethod
    def clean_prompt_field(prompt_text: str) -> tuple[str, bool]:
        """
        清理 improved_prompt 字段
        
        移除可能被模型错误返回的 JSON 格式包裹
        
        Args:
            prompt_text: 原始的 prompt 文本
            
        Returns:
            tuple[str, bool]: (清理后的文本, 是否进行了清理)
        """
        print("🧹 检查并清理 improved_prompt 格式...")
        cleaned = clean_improved_prompt(prompt_text)
        was_cleaned = cleaned != prompt_text
        
        if was_cleaned:
            print(f"✨ improved_prompt 已从 {len(prompt_text)} 字符优化为 {len(cleaned)} 字符")
        else:
            print("✅ improved_prompt 格式正确，无需清理")
        
        return cleaned, was_cleaned
    
    @staticmethod
    def parse_optimization_response(response_content: str) -> Dict[str, Any]:
        """
        完整的优化响应解析流程
        
        执行以下步骤：
        1. 提取 JSON（如果在代码块中）
        2. 解析 JSON 为字典
        
        Args:
            response_content: LLM 响应的原始内容
            
        Returns:
            Dict: 解析后的结果字典
            
        Raises:
            json.JSONDecodeError: JSON 格式错误时
        """
        # Step 1: 提取 JSON
        json_content = ResponseParser.extract_json_from_response(response_content)
        
        # Step 2: 解析 JSON
        result_dict = ResponseParser.parse_json(json_content)
        
        return result_dict
    
    @staticmethod
    def handle_parsing_error(error: Exception, response_content: str) -> str:
        """
        处理解析错误，生成友好的错误消息
        
        Args:
            error: 捕获的异常
            response_content: 导致错误的响应内容
            
        Returns:
            str: 格式化的错误消息
        """
        error_msg = str(error)
        
        # 构建错误消息
        msg_parts = [
            f"❌ 响应解析失败！",
            f"错误类型: {type(error).__name__}",
            f"错误详情: {error_msg[:500]}"
        ]
        
        # 如果是验证错误，添加额外提示
        if "validation" in error_msg.lower() or "Field required" in error_msg:
            msg_parts.extend([
                "",
                "⚠️ 这是数据结构验证错误，可能原因：",
                "   1. 模型返回的 JSON 格式不符合要求",
                "   2. 缺少必需的字段（thinking_process, improved_prompt 等）",
                "   3. 模型可能不支持 JSON 格式输出",
                "",
                "💡 建议：尝试更换模型，推荐使用 meta/llama-3.1-405b-instruct"
            ])
        
        # 显示响应片段（用于调试）
        msg_parts.extend([
            "",
            f"📄 响应前200字符: {response_content[:200]}..."
        ])
        
        return "\n".join(msg_parts)
