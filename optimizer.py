"""
Prompt 优化核心模块
实现自动化的 Prompt 生成、优化和评估
"""
import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
from templates import get_strategy_by_scene, OPTIMIZATION_PRINCIPLES


class OptimizedPrompt(BaseModel):
    """优化后的 Prompt 结构"""
    thinking_process: str = Field(description="优化时的思考过程，分析原始 Prompt 的问题和改进方向")
    improved_prompt: str = Field(description="优化后的完整 Prompt，可直接使用")
    enhancement_techniques: list[str] = Field(description="使用的优化技术，如：增加角色设定、明确输出格式等")
    keywords_added: list[str] = Field(description="新增的关键词和专业术语")
    structure_applied: str = Field(description="应用的 Prompt 框架名称，如 CO-STAR、BROKE 等")


class PromptOptimizer:
    """Prompt 自动优化器"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "meta/llama-3.1-405b-instruct", 
                 base_url: Optional[str] = None,
                 provider: Literal["openai", "nvidia"] = "nvidia",
                 temperature: float = 0.7,
                 top_p: float = 0.7,
                 max_tokens: int = 2048):
        """
        初始化优化器
        
        Args:
            api_key: API Key，如果不提供则从环境变量读取
            model: 使用的模型名称
            base_url: API base URL
            provider: API 提供商 ("openai" 或 "nvidia")
            temperature: 温度参数
            top_p: Top-p 采样参数
            max_tokens: 最大生成 token 数
        """
        self.provider = provider
        self.model = model
        
        # 根据提供商初始化 LLM
        if provider == "nvidia":
            if api_key:
                os.environ["NVIDIA_API_KEY"] = api_key
            
            llm_params = {
                "model": model,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens
            }
            if base_url:
                llm_params["base_url"] = base_url
            
            self.llm = ChatNVIDIA(**llm_params)
            
        else:  # openai
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            
            llm_params = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if base_url:
                llm_params["base_url"] = base_url
            
            self.llm = ChatOpenAI(**llm_params)
    
    def optimize(self, 
                 user_prompt: str, 
                 scene_desc: str = "通用",
                 optimization_mode: str = "通用增强 (General)") -> OptimizedPrompt:
        """
        核心优化函数
        
        Args:
            user_prompt: 用户输入的原始 Prompt
            scene_desc: 场景描述
            optimization_mode: 优化模式
            
        Returns:
            OptimizedPrompt: 优化后的结构化 Prompt
        """
        # 打印优化开始信息
        print(f"\n{'='*60}")
        print(f"⚙️  开始 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"🎯 优化模式: {optimization_mode}")
        print(f"📝 原始 Prompt: {user_prompt[:50]}{'...' if len(user_prompt) > 50 else ''}")
        if scene_desc:
            print(f"🎬 场景描述: {scene_desc[:50]}{'...' if len(scene_desc) > 50 else ''}")
        print(f"{'='*60}\n")
        
        # 获取场景对应的优化策略
        strategy = get_strategy_by_scene(optimization_mode)
        
        # 构建 Meta-Prompt
        system_prompt = self._build_meta_prompt(strategy, scene_desc)
        
        # 构建消息链
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "用户原始 Prompt：{input}\n\n场景补充说明：{scene}")
        ])
        
        # 执行优化
        try:
            print("📤 正在调用 API...")
            
            # 构建完整提示
            messages = prompt_template.format_messages(
                input=user_prompt,
                scene=scene_desc if scene_desc else "无特殊说明"
            )
            
            print(f"💬 消息长度: {len(str(messages))} 字符")
            
            # 调用 LLM
            if self.provider == "openai":
                # OpenAI 支持 JSON mode
                print("🔧 使用 OpenAI JSON mode")
                response = self.llm.invoke(
                    messages,
                    response_format={"type": "json_object"}
                )
            else:
                # NVIDIA 使用普通调用
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            print(f"📄 响应前100字符: {content[:100]}...")
            
            # 尝试提取 JSON（可能包含在 markdown 代码块中）
            if "```json" in content:
                print("🔍 检测到 JSON 代码块，正在提取...")
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                print("🔍 检测到代码块，正在提取...")
                content = content.split("```")[1].split("```")[0].strip()
            
            print("⚙️ 正在解析 JSON...")
            result_dict = json.loads(content)
            
            print("✅ JSON 解析成功")
            print("🔨 正在验证数据结构...")
            optimized = OptimizedPrompt(**result_dict)
            
            print("✅ 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            # 错误处理：详细记录到终端
            print(f"\n❌ 优化失败！")
            print(f"{'='*60}")
            
            error_msg = str(e)
            print(f"🐛 错误类型: {type(e).__name__}")
            print(f"📝 错误详情: {error_msg[:500]}")
            
            # 如果是 Pydantic 验证错误，打印详细信息
            if "validation" in error_msg.lower() or "Field required" in error_msg:
                print("\n⚠️ 这是数据结构验证错误，可能原因：")
                print("   1. 模型返回的 JSON 格式不符合要求")
                print("   2. 缺少必需的字段（thinking_process, improved_prompt 等）")
                print("   3. 模型可能不支持 JSON 格式输出")
                print("\n💡 建议：尝试更换模型，推荐使用 meta/llama-3.1-405b-instruct")
            
            # 打印完整堆栈
            import traceback
            print(f"\n📄 完整堆栈信息：")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 根据错误类型抛出明确的异常
            if "404" in error_msg:
                raise Exception(f"API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。详细信息：{error_msg[:200]}")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"API Key 无效或已过期。请检查您的 API Key 配置。")
            elif "rate_limit" in error_msg.lower():
                raise Exception(f"API 请求频率超限，请稍后再试。")
            else:
                raise Exception(f"优化失败: {error_msg[:300]}")
    
    def _build_meta_prompt(self, strategy: dict, scene_desc: str) -> str:
        """构建 Meta-Prompt（教 LLM 如何优化 Prompt 的提示词）"""
        
        template_name = strategy.get("template", "CO-STAR")
        focus_principles = strategy.get("focus", ["clarity", "structure"])
        extra_requirements = strategy.get("extra_requirements", [])
        
        # 获取焦点原则的详细说明
        principles_text = "\n".join([
            f"   - {OPTIMIZATION_PRINCIPLES.get(p, p)}"
            for p in focus_principles
        ])
        
        # 构建额外要求文本
        extra_text = ""
        if extra_requirements:
            extra_text = "\n\n**场景特定要求**：\n" + "\n".join([
                f"   - {req}" for req in extra_requirements
            ])
        
        meta_prompt = f"""
你是一位世界级的 Prompt Engineering 专家，擅长将简单的指令转化为结构化、高性能的专家级 Prompt。

**你的任务流程**：

1. **深度理解**：仔细分析用户的原始 Prompt，识别其核心意图和隐含需求

2. **三大优化策略**：
   
   a) **语义扩展 (Semantic Expansion)**
      - 补充缺失的上下文信息
      - 明确隐含的约束条件
      - 规范输出格式要求
   
   b) **关键词增强 (Keywords Enhancement)**
      - 识别任务所属的专业领域
      - 加入该领域的专业术语和行业概念
      - 用精确的词汇替换模糊表达
   
   c) **结构化重写 (Template Application)**
      - 必须使用 **{template_name}** 框架进行重写
      - 确保 Prompt 逻辑清晰、层次分明

3. **优化原则**（本次优化重点关注）：
{principles_text}
{extra_text}

**场景上下文**：{scene_desc if scene_desc else "通用场景"}

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程（200字左右）
- improved_prompt: 优化后的完整 Prompt（可直接使用）
- enhancement_techniques: 使用的优化技术列表
- keywords_added: 新增的关键词列表
- structure_applied: 应用的框架名称

**重要**：improved_prompt 应该是一个完整的、可以直接复制使用的高质量 Prompt，不要包含任何元信息或说明。
"""
        return meta_prompt
    
    def _fallback_optimization(self, original_prompt: str, error: str) -> OptimizedPrompt:
        """当优化失败时的备用方案"""
        return OptimizedPrompt(
            thinking_process=f"优化过程中遇到错误：{error}。以下是基础优化版本。",
            improved_prompt=f"""
请以专业的态度完成以下任务：

{original_prompt}

要求：
1. 输出内容应该清晰、准确、完整
2. 使用恰当的格式组织信息
3. 注重细节和专业性
4. 如有需要，请展示你的思考过程
""",
            enhancement_techniques=["基础结构化", "添加通用要求"],
            keywords_added=[],
            structure_applied="简单优化"
        )
    
    def compare_results(self, original_prompt: str, optimized_prompt: str, 
                       test_query: Optional[str] = None) -> tuple[str, str]:
        """
        A/B 对比测试：分别运行原始和优化后的 Prompt
        
        Args:
            original_prompt: 原始 Prompt
            optimized_prompt: 优化后的 Prompt
            test_query: 可选的测试查询（如果 Prompt 本身不是直接的问题）
            
        Returns:
            (原始结果, 优化后结果)
        """
        try:
            # 运行原始 Prompt
            response_original = self.llm.invoke(original_prompt)
            result_original = response_original.content
            
            # 运行优化后的 Prompt
            response_optimized = self.llm.invoke(optimized_prompt)
            result_optimized = response_optimized.content
            
            return result_original, result_optimized
            
        except Exception as e:
            return f"运行失败: {str(e)}", f"运行失败: {str(e)}"
    
    def batch_optimize(self, prompts: list[str], 
                       scene_desc: str = "通用",
                       optimization_mode: str = "通用增强 (General)") -> list[OptimizedPrompt]:
        """
        批量优化多个 Prompt
        
        Args:
            prompts: Prompt 列表
            scene_desc: 场景描述
            optimization_mode: 优化模式
            
        Returns:
            优化结果列表
        """
        results = []
        for prompt in prompts:
            result = self.optimize(prompt, scene_desc, optimization_mode)
            results.append(result)
        return results


# 便捷函数
def quick_optimize(user_prompt: str, 
                   api_key: Optional[str] = None,
                   scene: str = "通用",
                   mode: str = "通用增强 (General)",
                   provider: str = "nvidia") -> OptimizedPrompt:
    """
    快速优化函数，适合简单调用
    
    Example:
        result = quick_optimize("写个贪吃蛇", scene="Python初学者", mode="代码生成 (Coding)")
        print(result.improved_prompt)
    """
    optimizer = PromptOptimizer(api_key=api_key, provider=provider)
    return optimizer.optimize(user_prompt, scene, mode)


if __name__ == "__main__":
    # 测试代码
    from dotenv import load_dotenv
    load_dotenv()
    
    # 示例测试
    test_prompt = "写个贪吃蛇游戏"
    
    optimizer = PromptOptimizer()
    result = optimizer.optimize(
        test_prompt, 
        scene_desc="Python, 给小孩学编程用",
        optimization_mode="代码生成 (Coding)"
    )
    
    print("=" * 50)
    print("优化思考过程：")
    print(result.thinking_process)
    print("\n" + "=" * 50)
    print("优化后的 Prompt：")
    print(result.improved_prompt)
    print("\n" + "=" * 50)
    print("使用的技术：", result.enhancement_techniques)
    print("新增关键词：", result.keywords_added)
