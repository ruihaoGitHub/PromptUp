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
    """优化后的 Prompt 结构（生成任务）"""
    thinking_process: str = Field(description="优化时的思考过程，分析原始 Prompt 的问题和改进方向")
    improved_prompt: str = Field(description="优化后的完整 Prompt，可直接使用")
    enhancement_techniques: list[str] = Field(description="使用的优化技术，如：增加角色设定、明确输出格式等")
    keywords_added: list[str] = Field(description="新增的关键词和专业术语")
    structure_applied: str = Field(description="应用的 Prompt 框架名称，如 CO-STAR、BROKE 等")


class ClassificationPrompt(BaseModel):
    """优化后的分类任务 Prompt 结构"""
    thinking_process: str = Field(description="优化分析过程")
    role_definition: str = Field(description="角色设定，例如：你是一个资深的情感分析专家")
    label_definitions: dict[str, str] = Field(description="标签详细定义字典，Key是标签名，Value是详细判断标准")
    few_shot_examples: list[dict[str, str]] = Field(description="自动合成的3-5个高质量少样本示例")
    reasoning_guidance: str = Field(description="思维链引导语，帮助模型逐步分析")
    output_format: str = Field(description="严格的输出格式要求")
    final_prompt: str = Field(description="组合好的最终可用的完整 Prompt")

class SummarizationPrompt(BaseModel):
    """优化后的摘要任务 Prompt 结构"""
    thinking_process: str = Field(description="优化分析过程")
    role_setting: str = Field(description="角色设定，如：你是一位专业的技术文档编写专家")
    extraction_rules: list[str] = Field(description="具体的提取规则，如：必须保留所有数字、日期和责任人")
    negative_constraints: list[str] = Field(description="负面约束，明确告诉模型不要做什么")
    format_template: str = Field(description="严格的输出格式模板，通常包含Markdown结构")
    step_by_step_guide: str = Field(description="给模型的思考步骤，如：通读全文 -> 标记重点 -> 撰写初稿")
    focus_areas: list[str] = Field(description="核心关注点，针对用户需求强调的信息")
    final_prompt: str = Field(description="组合好的最终可用的摘要 Prompt，{{text}}占位符")


class TranslationPrompt(BaseModel):
    """优化后的翻译任务 Prompt 结构"""
    thinking_process: str = Field(description="优化分析过程")
    role_definition: str = Field(description="角色设定，例如：你是精通中英双语的《自然》杂志编辑")
    style_guidelines: list[str] = Field(description="风格指南列表，例如：['保持学术严谨', '避免口语化', '保留被动语态']")
    glossary_section: str = Field(description="构建的术语对照表部分，如果没有则留空")
    workflow_steps: str = Field(description="翻译的工作流指令，推荐使用'直译-反思-润色'三步法")
    final_prompt: str = Field(description="最终组合好的 Prompt 模板，待翻译文本用 {{text}} 占位")


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
    
    def optimize_classification(self,
                               task_description: str,
                               labels: list[str],
                               example_texts: Optional[list[str]] = None) -> ClassificationPrompt:
        """
        针对分类任务的优化函数
        
        Args:
            task_description: 分类任务描述，如 "判断用户评论的情感倾向"
            labels: 目标标签列表，如 ["Positive", "Negative", "Neutral"]
            example_texts: 可选的示例文本，用于生成 Few-Shot 样本
            
        Returns:
            ClassificationPrompt: 优化后的分类 Prompt
        """
        print(f"\n{'='*60}")
        print(f"🏷️  开始分类任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📝 任务描述: {task_description[:50]}...")
        print(f"🏷️  目标标签: {', '.join(labels)}")
        print(f"{'='*60}\n")
        
        # 构建分类任务专用的 Meta-Prompt
        # 不使用 f-string，避免花括号冲突
        system_prompt = """
你是一个专门构建 AI 文本分类器的专家。你的目标是编写一个**高精度**的分类 Prompt。

**任务描述**：TASK_DESCRIPTION
**目标标签**：TARGET_LABELS

**你的任务**：

1. **标签消歧 (Label Disambiguation)**
   - 为每个标签编写清晰、具体的定义
   - 明确边界情况（Edge Cases）和判断标准
   - 说明什么样的文本属于该标签，什么不属于

2. **样本合成 (Few-Shot Generation)**
   - 根据标签定义，创作 3-5 个典型的高质量示例
   - 示例必须覆盖不同标签，具有代表性
   - 每个示例包含 input（输入文本）和 label（对应标签）

3. **思维链设计 (Chain of Thought)**
   - 设计引导语，让模型先分析特征，再给出分类结果
   - 对于复杂分类任务，使用 "Let's think step by step"

4. **格式锁定 (Output Format)**
   - 明确要求模型只输出特定格式（如 JSON）
   - 禁止模型输出多余的解释或废话
   - 确保输出可以被代码轻松解析

5. **角色设定**
   - 为分类器设定一个专业的角色身份
   - 增强模型对任务的理解和执行准确度

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程
- role_definition: 角色设定描述
- label_definitions: 标签定义字典（键为标签名，值为详细定义）
- few_shot_examples: 示例列表（每个包含 input 和 label 字段）
- reasoning_guidance: 思维链引导语
- output_format: 输出格式要求说明
- final_prompt: 完整的、可直接使用的分类 Prompt
- enhancement_techniques: 使用的优化技术列表

**关键要求 - final_prompt 必须包含占位符**：
- final_prompt 必须是一个完整的、结构清晰的、可以直接复制使用的分类 Prompt
- **必须在 Prompt 中明确标注待分类文本的位置**，使用以下任一占位符格式：
  * [待分类文本] （推荐）
  * {{text}} （两个花括号）
  * [输入评论]
  * [待处理文本]
- 占位符应该放在合理的位置，比如：
  * "评论内容：[待分类文本]"
  * "请分析以下文本：[待分类文本]"
  * "文本：{{text}}"
- **不要**只说"分析这个评论"或"判断情感"而不提供具体的插入位置
- final_prompt 必须是可以通过简单的字符串替换就能使用的模板

**示例正确格式**：
```
你是专业的情感分析师。
标签定义：...
示例：...
现在请分析以下评论的情感倾向：
[待分类文本]
请输出标签名称即可。
```

**示例错误格式（不要生成这样的）**：
```
你是专业的情感分析师。
标签定义：...
示例：...
让我们分析评论的情感倾向。（❌ 缺少明确的文本插入位置）
```
"""
        
        # 手动替换变量
        system_prompt = system_prompt.replace("TASK_DESCRIPTION", task_description)
        system_prompt = system_prompt.replace("TARGET_LABELS", ', '.join(labels))
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "请为这个分类任务生成优化的 Prompt。")
        ])
        
        try:
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
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            
            # 提取 JSON
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
            optimized = ClassificationPrompt(**result_dict)
            
            print("✅ 分类 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            # 错误处理
            print(f"\n❌ 分类优化失败！")
            print(f"{'='*60}")
            
            error_msg = str(e)
            print(f"🐛 错误类型: {type(e).__name__}")
            print(f"📝 错误详情: {error_msg[:500]}")
            
            import traceback
            print(f"\n📄 完整堆栈信息：")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 抛出异常
            if "404" in error_msg:
                raise Exception(f"API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"API Key 无效或已过期。")
            else:
                raise Exception(f"分类优化失败: {error_msg[:300]}")
    
    def optimize_summarization(self,
                              task_description: str,
                              source_type: str,
                              target_audience: str,
                              focus_points: str,
                              length_constraint: Optional[str] = None) -> SummarizationPrompt:
        """
        针对摘要任务的优化函数
        
        Args:
            task_description: 摘要任务描述，如 "总结技术会议的核心决策"
            source_type: 源文本类型，如 "会议记录"、"学术论文"、"新闻报道"
            target_audience: 目标读者，如 "技术经理"、"普通用户"
            focus_points: 核心关注点，如 "行动计划和负责人"
            length_constraint: 篇幅限制，如 "100字以内"、"3-5个要点"
            
        Returns:
            SummarizationPrompt: 优化后的摘要 Prompt
        """
        print(f"\n{'='*60}")
        print(f"📝 开始摘要任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📝 任务描述: {task_description[:50]}...")
        print(f"📄 源文本类型: {source_type}")
        print(f"👥 目标受众: {target_audience}")
        print(f"🎯 关注点: {focus_points[:50]}...")
        if length_constraint:
            print(f"📏 篇幅限制: {length_constraint}")
        print(f"{'='*60}\n")
        
        # 构建摘要任务专用的 Meta-Prompt
        length_text = f"\n**篇幅限制**：{length_constraint}" if length_constraint else ""
        
        system_prompt = f"""
你是一位精通信息压缩和摘要撰写的 Prompt Engineering 专家。
用户的目标是针对特定场景生成一个**高质量的摘要 Prompt**。

**任务信息**：
- 任务描述：{task_description}
- 源文本类型：{source_type}
- 目标受众：{target_audience}
- 核心关注点：{focus_points}{length_text}

**你的任务**：

1. **角色沉浸 (Role Immersion)**
   - 根据源文本类型和目标受众，设定最合适的专家角色
   - 例如：会议记录 → "专业的会议纪要秘书"；学术论文 → "资深的科研编辑"

2. **提取规则制定 (Extraction Rules)**
   - 明确告诉模型必须保留什么信息（如：数字、日期、人名、关键决策）
   - 针对用户的核心关注点，强调相关信息的重要性
   - 至少提供 3-5 条具体的提取规则

3. **负面约束 (Negative Constraints)**
   - 明确告诉模型"不要"做什么
   - 例如：不要使用模糊词汇、不要遗漏数据、不要添加原文没有的信息
   - 防止模型"幻觉"（编造细节）

4. **结构化输出 (Structured Format)**
   - 根据源文本类型设计合适的输出格式
   - 会议记录 → 表格或分层结构（背景、决策、行动计划）
   - 新闻报道 → TL;DR + 关键事实
   - 学术论文 → 研究目的、方法、结论、意义

5. **思考步骤设计 (Step-by-Step Guide)**
   - 给模型明确的处理流程，如：
     Step 1: 通读全文，标记关键信息
     Step 2: 根据关注点筛选内容
     Step 3: 按结构组织信息
     Step 4: 精简表达，确保准确

6. **关注点锚定 (Focus Areas)**
   - 将用户的核心关注点转化为具体的信息类别
   - 在 Prompt 中多次强调这些关注点的优先级

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程
- role_setting: 角色设定描述
- extraction_rules: 提取规则列表（至少3-5条）
- negative_constraints: 负面约束列表（至少3条）
- format_template: 输出格式模板（使用 Markdown）
- step_by_step_guide: 处理步骤说明
- focus_areas: 核心关注点列表
- final_prompt: 完整的、可直接使用的摘要 Prompt（用 {{{{text}}}} 作为待摘要文本的占位符）

**重要**：
- final_prompt 必须是一个完整的、结构清晰的、可以直接复制使用的摘要 Prompt
- 其中待摘要的文本用 {{{{text}}}} 占位符表示
- 所有规则和约束都要整合进 final_prompt 中
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "请为这个摘要任务生成优化的 Prompt。")
        ])
        
        try:
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
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            
            # 提取 JSON
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
            optimized = SummarizationPrompt(**result_dict)
            
            print("✅ 摘要 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            # 错误处理
            print(f"\n❌ 摘要优化失败！")
            print(f"{'='*60}")
            
            error_msg = str(e)
            print(f"🐛 错误类型: {type(e).__name__}")
            print(f"📝 错误详情: {error_msg[:500]}")
            
            import traceback
            print(f"\n📄 完整堆栈信息：")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 抛出异常
            if "404" in error_msg:
                raise Exception(f"API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"API Key 无效或已过期。")
            else:
                raise Exception(f"摘要优化失败: {error_msg[:300]}")
    
    def optimize_translation(self,
                           source_lang: str,
                           target_lang: str,
                           domain: str,
                           tone: str,
                           user_glossary: str = "") -> TranslationPrompt:
        """
        针对翻译任务的优化函数
        
        Args:
            source_lang: 源语言，如 "中文"、"英文"
            target_lang: 目标语言
            domain: 应用领域，如 "通用日常"、"IT/技术文档"、"法律合同"等
            tone: 期望风格，如 "标准/准确"、"地道/口语化"
            user_glossary: 用户提供的术语表，格式如 "Prompt=提示词\nLLM=大语言模型"
            
        Returns:
            TranslationPrompt: 优化后的翻译 Prompt
        """
        print(f"\n{'='*60}")
        print(f"🌍 开始翻译任务 Prompt 优化")
        print(f"{'='*60}")
        print(f"🔌 API 提供商: {self.provider.upper()}")
        print(f"🤖 使用模型: {self.model}")
        print(f"🔄 翻译方向: {source_lang} → {target_lang}")
        print(f"📚 应用领域: {domain}")
        print(f"🎨 期望风格: {tone}")
        if user_glossary:
            print(f"📖 术语表: {len(user_glossary.split(chr(10)))} 条")
        print(f"{'='*60}\n")
        
        # 处理术语表
        glossary_text = ""
        if user_glossary.strip():
            glossary_text = f"""
**用户指定术语表**：
用户强制指定了以下术语对应关系，必须在 Prompt 中创建一个明确的 Glossary Section 来锁定这些翻译：
{user_glossary}
"""
        
        # 构建翻译任务专用的 Meta-Prompt
        system_prompt = f"""
你是一位精通多语言转换的 Prompt Engineering 专家。
你的任务是构建一个**专家级的翻译 Prompt**，以解决机器翻译生硬、缺乏语境、风格不一致的问题。

**任务信息**：
- 语言方向：{source_lang} → {target_lang}
- 应用领域：{domain}
- 期望风格：{tone}{glossary_text}

**翻译任务的核心挑战**：
1. **语境偏差（Context Nuance）**：同一个词在不同场景有不同含义（如 "Bank" 是"银行"还是"河岸"？）
2. **风格一致性（Tone & Style）**：是"信达雅"的文学翻译，还是"精准直白"的技术翻译？
3. **术语一致性（Glossary Consistency）**：特定的专有名词不能乱翻，需要统一标准

**你的任务**：
构建一个包含以下高级策略的翻译 Prompt：

1. **领域沉浸（Domain Immersion）**
   - 根据领域设定最权威的专家角色
   - IT文档 → "精通中英双语的资深软件工程师和技术文档编辑"
   - 法律合同 → "资深国际法律翻译专家，熟悉中英法律术语体系"
   - 文学作品 → "专业文学译者，曾翻译多部获奖作品"
   - 学术论文 → "《自然》杂志编辑，精通学术规范和科研表达"

2. **术语锁定（Glossary Locking）**
   - 如果用户提供了术语表，必须在 Prompt 中生成一个清晰的 Mapping Table
   - 要求模型"严格遵守"（Strictly Adhere）这些术语对应关系
   - 格式示例：
     ```
     **术语表（必须严格遵守）**：
     - Apple → 苹果公司（而非"苹果"水果）
     - Prompt → 提示词（技术术语，不翻译为"提示"）
     ```

3. **三步翻译法（Three-Step Translation）**
   - 在 Prompt 中要求模型按以下流程处理：
     Step 1: 分析上下文和专业术语，进行初步直译
     Step 2: 根据语境和领域特点，调整表达方式，确保语义准确
     Step 3: 润色风格，使译文符合目标语言的表达习惯和期望风格
   - 这种"慢思考"模式能显著提升质量

4. **风格指南（Style Guidelines）**
   - 根据期望风格给出具体指导：
   - "标准/准确"：保持客观、严谨，避免添加主观色彩
   - "地道/口语化"：使用目标语言的自然表达，避免"翻译腔"
   - "优美/文学性"：注重韵律和美感，可适当意译
   - "极简/摘要式"：简洁明了，去除冗余

5. **保留规则（Preservation Rules）**
   - 对于以下内容，明确要求保留原文：
   - 代码块、命令行、文件路径
   - 专有名词（人名、地名、品牌名）
   - 无法翻译或不宜翻译的术语（用括号注释原文）

6. **格式规范（Format Requirements）**
   - 保持原文的段落结构和格式
   - 数字、标点符号的规范（如：中文用全角，英文用半角）

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程，分析这个翻译任务的特点和难点
- role_definition: 角色设定描述，要具体到该领域最权威的专家
- style_guidelines: 风格指南列表（list），针对期望风格的具体要求（3-5条）
- glossary_section: 术语对照表部分的文本（如果用户提供了术语表）。如果没有则返回空字符串
- workflow_steps: 翻译工作流指令，推荐使用"三步翻译法"的详细描述
- final_prompt: 完整的、可直接使用的翻译 Prompt（用 {{{{text}}}} 作为待翻译文本的占位符）

**重要**：
- final_prompt 必须是一个完整的、结构清晰的、可以直接复制使用的翻译 Prompt
- 其中待翻译的文本用 {{{{text}}}} 占位符表示
- 所有规则、术语表、风格指南都要整合进 final_prompt 中
- 务必体现"领域专家 + 术语锁定 + 三步翻译法"的核心策略
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "请为这个翻译任务生成优化的 Prompt。")
        ])
        
        try:
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
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            
            # 提取 JSON
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
            optimized = TranslationPrompt(**result_dict)
            
            print("✅ 翻译 Prompt 优化完成！")
            print(f"{'='*60}\n")
            
            return optimized
            
        except Exception as e:
            # 错误处理
            print(f"\n❌ 翻译优化失败！")
            print(f"{'='*60}")
            
            error_msg = str(e)
            print(f"🐛 错误类型: {type(e).__name__}")
            print(f"📝 错误详情: {error_msg[:500]}")
            
            import traceback
            print(f"\n📄 完整堆栈信息：")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 抛出异常
            if "404" in error_msg:
                raise Exception(f"API 调用失败 (404): 请检查 API Key 是否有效，或模型名称是否正确。")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception(f"API Key 无效或已过期。")
            else:
                raise Exception(f"翻译优化失败: {error_msg[:300]}")
    
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
