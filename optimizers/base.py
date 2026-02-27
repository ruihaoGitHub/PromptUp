"""
任务优化器基类
包含所有任务优化器的共享逻辑
"""
import time
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from utils import safe_json_loads


class OptimizerBase:
    """任务优化器基类"""
    
    def __init__(self, llm, provider: Literal["openai", "nvidia"], model: str):
        """
        初始化基类
        
        Args:
            llm: LangChain LLM 实例
            provider: API 提供商
            model: 模型名称
        """
        self.llm = llm
        self.provider = provider
        self.model = model
    
    def _call_llm(self, system_prompt: str, human_message: str = "请为这个任务生成优化的 Prompt。") -> str:
        """
        调用 LLM 并返回响应内容
        
        Args:
            system_prompt: 系统提示词（Meta-Prompt）
            human_message: 人类消息
            
        Returns:
            str: LLM 响应内容
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])
        
        print("📤 正在调用 API...")
        messages = prompt_template.format_messages()
        print(f"💬 消息长度: {len(str(messages))} 字符")
        
        # 调用 LLM
        if self.provider == "openai":
            print("🔧 使用 OpenAI JSON mode")
            response = self.llm.invoke(
                messages,
                response_format={"type": "json_object"}
            )
            time.sleep(0.5)  # API 调用延迟，避免频率过快
        else:
            print("🔧 使用 NVIDIA 标准调用")
            response = self.llm.invoke(messages)
            time.sleep(0.5)  # API 调用延迟，避免频率过快
        
        return response.content
    
    def _extract_json(self, content: str) -> str:
        """
        从响应内容中提取 JSON
        
        Args:
            content: LLM 响应内容
            
        Returns:
            str: 提取的 JSON 字符串
        """
        print(f"📥 收到响应，长度: {len(content)} 字符")
        print(f"📑 响应前200字符: {content[:200]}...")
        
        # 提取 JSON
        if "```json" in content:
            print("🔍 检测到 JSON 代码块，正在提取...")
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            print("🔍 检测到代码块，正在提取...")
            content = content.split("```")[1].split("```")[0].strip()
        
        return content
    
    def _parse_and_validate(self, content: str, model_class):
        """
        解析 JSON 并验证数据结构
        
        Args:
            content: JSON 字符串
            model_class: Pydantic 模型类
            
        Returns:
            model_class 的实例
        """
        print("⚙️ 正在解析 JSON...")
        print(f"📑 清理后的JSON前300字符: {content[:300]}...")
        result_dict = safe_json_loads(content)
        
        print("✅ JSON 解析成功")
        print(f"🔑 解析得到的字段: {list(result_dict.keys())}")
        print("🔨 正在验证数据结构...")
        
        # 修复常见的类型问题
        # 1. step_by_step_guide 可能是列表，需要转换为字符串
        if 'step_by_step_guide' in result_dict and isinstance(result_dict['step_by_step_guide'], list):
            result_dict['step_by_step_guide'] = '\n'.join(result_dict['step_by_step_guide'])
        
        # 2. extraction_rules 可能是列表，保持不变（符合 List[str]）
        # 3. negative_constraints 可能是列表，保持不变（符合 List[str]）
        
        return model_class(**result_dict)
    
    def _handle_error(self, e: Exception, task_name: str):
        """
        统一的错误处理
        
        Args:
            e: 异常对象
            task_name: 任务名称（用于错误消息）
        """
        print(f"\n❌ {task_name}优化失败！")
        print(f"{'='*60}")
        
        error_msg = str(e)
        print(f"🐛 错误类型: {type(e).__name__}")
        print(f"📝 错误详情: {error_msg[:500]}")
        
        # 如果是Pydantic验证错误，显示更详细的信息
        if hasattr(e, 'errors'):
            print("\n🔴 Pydantic 验证错误详情:")
            for err in e.errors():
                print(f"  - 字段: {err.get('loc', 'unknown')}")
                print(f"    错误: {err.get('msg', 'unknown')}")
                print(f"    类型: {err.get('type', 'unknown')}")
        
        import traceback
        print("\n📄 完整堆栈信息：")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        # 抛出异常
        if "404" in error_msg:
            raise Exception("API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。")
        elif "401" in error_msg or "Unauthorized" in error_msg:
            raise Exception("API Key 无效或已过期。")
        else:
            raise Exception(f"{task_name}优化失败: {error_msg[:300]}")
