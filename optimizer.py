"""
Prompt 优化核心模块
实现自动化的 Prompt 生成、优化和评估
"""
import os
import time
import re
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import random
from templates import get_strategy_by_scene, OPTIMIZATION_PRINCIPLES
from metrics import MetricsCalculator

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️ Optuna 未安装，贝叶斯优化功能不可用。运行: pip install optuna")


def check_unescaped_braces(template: str, template_name: str = "模板") -> None:
    """
    检查模板字符串中是否存在未转义的花括号（会导致 format_messages KeyError）
    
    Args:
        template: 要检查的模板字符串
        template_name: 模板名称（用于错误提示）
    
    Raises:
        ValueError: 如果检测到可疑的未转义花括号
    """
    # 检测单个花括号（可能是未转义的）
    # 排除已经转义的 {{ 和 }}，以及合法的占位符如 {scene_desc}
    
    # 查找所有花括号
    single_open = re.findall(r'(?<!\{)\{(?!\{)', template)
    single_close = re.findall(r'(?<!\})\}(?!\})', template)
    
    # 查找合法的占位符（如 {scene_desc}, {template_name} 等）
    valid_placeholders = re.findall(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', template)
    
    # 如果单花括号数量不等于合法占位符数量，说明有问题
    suspicious_count = len(single_open) - len(valid_placeholders)
    
    if suspicious_count > 0:
        print(f"⚠️ 警告：{template_name} 中检测到 {suspicious_count} 个可疑的未转义花括号")
        print(f"   这可能会导致 format_messages() 时出现 KeyError")
        print(f"   合法占位符: {valid_placeholders}")
        print(f"   如果模板中包含示例JSON或其他需要显示花括号的内容，请使用 {{{{ 和 }}}} 进行转义")


def parse_markdown_response(content: str) -> dict:
    """
    解析Markdown格式的响应（当模型返回 **字段名**: 而不是JSON时）
    
    Args:
        content: Markdown格式的响应
        
    Returns:
        解析后的字典
    """
    print("🔍 尝试从Markdown格式中提取字段...")
    
    result = {}
    
    # 提取 thinking_process
    thinking_match = re.search(r'\*\*thinking_process\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if thinking_match:
        result['thinking_process'] = thinking_match.group(1).strip()
    
    # 提取 improved_prompt
    improved_match = re.search(r'\*\*improved_prompt\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if improved_match:
        result['improved_prompt'] = improved_match.group(1).strip()
    
    # 提取 enhancement_techniques（列表形式）
    techniques_match = re.search(r'\*\*enhancement_techniques\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if techniques_match:
        techniques_text = techniques_match.group(1).strip()
        # 解析列表项（以 - 开头）
        techniques = re.findall(r'-\s*([^\n]+)', techniques_text)
        if techniques:
            # 清理每个技术项，去除括号中的英文说明
            result['enhancement_techniques'] = [re.sub(r'\s*（.*?）|\s*\(.*?\)', '', t).strip() for t in techniques]
        else:
            # 如果没有列表项，尝试按逗号分割
            result['enhancement_techniques'] = [t.strip() for t in techniques_text.split(',') if t.strip()]
    
    # 提取 keywords_added（列表形式）
    keywords_match = re.search(r'\*\*keywords_added\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if keywords_match:
        keywords_text = keywords_match.group(1).strip()
        keywords = re.findall(r'-\s*([^\n]+)', keywords_text)
        if keywords:
            result['keywords_added'] = [k.strip() for k in keywords]
        else:
            result['keywords_added'] = [k.strip() for k in keywords_text.split(',') if k.strip()]
    
    # 提取 structure_applied
    structure_match = re.search(r'\*\*structure_applied\*\*[：:]\s*([^\n]+)', content)
    if structure_match:
        result['structure_applied'] = structure_match.group(1).strip()
    
    # 设置默认值（如果某些字段缺失）
    if 'thinking_process' not in result:
        result['thinking_process'] = "优化过程分析"
    if 'improved_prompt' not in result:
        result['improved_prompt'] = ""
    if 'enhancement_techniques' not in result:
        result['enhancement_techniques'] = []
    if 'keywords_added' not in result:
        result['keywords_added'] = []
    if 'structure_applied' not in result:
        result['structure_applied'] = "通用框架"
    
    print(f"✅ 从Markdown中提取了 {len(result)} 个字段")
    return result


def safe_json_loads(content: str) -> dict:
    """
    安全地解析JSON字符串，处理控制字符和Markdown格式问题
    
    Args:
        content: JSON字符串或Markdown格式文本
        
    Returns:
        解析后的字典
        
    Raises:
        JSONDecodeError: 如果所有尝试都失败
    """
    # 首先检测是否是Markdown格式（包含 **字段名**: 或 **字段名**： 的模式）
    if '**thinking_process**' in content or '**improved_prompt**' in content:
        print("🔍 检测到Markdown格式响应，优先尝试Markdown解析...")
        try:
            result = parse_markdown_response(content)
            if result.get('improved_prompt'):
                print("✅ Markdown格式解析成功")
                return result
        except Exception as e:
            print(f"⚠️ Markdown解析失败: {str(e)}")
    
    try:
        # 尝试直接解析
        return json.loads(content)
    except json.JSONDecodeError as json_err:
        print(f"⚠️ JSON解析失败: {str(json_err)}")
        
        # 尝试使用 strict=False 参数（允许某些控制字符）
        try:
            result = json.loads(content, strict=False)
            print("✅ 使用 strict=False 解析成功")
            return result
        except:
            pass
        
        # 尝试手动清理控制字符
        try:
            print("⚠️ 尝试手动清理JSON内容")
            # 替换未转义的控制字符
            cleaned_content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            # 但是JSON结构本身的换行需要保留，所以这个方法可能不完美
            # 更好的方法是只清理字符串值内的控制字符
            result = json.loads(cleaned_content)
            print("✅ 清理后解析成功")
            return result
        except:
            pass
        
        # 如果上面都失败了，尝试更激进的清理
        try:
            print("⚠️ 尝试使用正则表达式清理")
            # 移除所有ASCII控制字符，除了空格、换行、制表符（JSON结构需要）
            cleaned_content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            result = json.loads(cleaned_content)
            print("✅ 正则清理后解析成功")
            return result
        except Exception as final_err:
            print(f"❌ 所有JSON解析尝试均失败")
            print(f"原始内容前500字符: {content[:500]}")
            raise json_err  # 抛出原始错误
            print("✅ 正则清理后解析成功")
            return result
        except Exception as final_err:
            print(f"❌ 所有JSON解析尝试均失败")
            print(f"原始内容前500字符: {content[:500]}")
            raise json_err  # 抛出原始错误


def clean_improved_prompt(improved_prompt: str) -> str:
    """
    清理 improved_prompt 字段，确保不包含JSON格式的文本
    处理大模型误将JSON当作优化结果的情况
    
    Args:
        improved_prompt: 原始的 improved_prompt 内容
        
    Returns:
        清理后的纯文本 prompt
    """
    # 去除首尾空白
    cleaned = improved_prompt.strip()
    
    # 检测是否是JSON格式（以 { 开头，} 结尾）
    if cleaned.startswith('{') and cleaned.endswith('}'):
        print("⚠️ 检测到 improved_prompt 是JSON格式，尝试转换为自然语言...")
        
        try:
            # 尝试解析JSON
            json_data = json.loads(cleaned)
            
            # 将JSON转换为自然语言描述
            prompt_parts = []
            
            # 检查常见字段并构建自然语言描述
            if "任务描述" in json_data:
                prompt_parts.append(f"任务：{json_data['任务描述']}")
            
            if "约束条件" in json_data:
                constraints = json_data["约束条件"]
                if isinstance(constraints, dict):
                    prompt_parts.append("\n约束条件：")
                    for key, value in constraints.items():
                        prompt_parts.append(f"- {key}：{value}")
            
            if "输出要求" in json_data:
                output_req = json_data["输出要求"]
                if isinstance(output_req, dict):
                    prompt_parts.append("\n输出要求：")
                    for key, value in output_req.items():
                        if value:  # 如果值非空
                            prompt_parts.append(f"- {key}：{value}")
                        else:
                            prompt_parts.append(f"- {key}")
            
            if "语气风格" in json_data:
                prompt_parts.append(f"\n语气风格：{json_data['语气风格']}")
            
            if "平台" in json_data:
                prompt_parts.append(f"\n目标平台：{json_data['平台']}")
            
            if prompt_parts:
                converted = "\n".join(prompt_parts)
                print(f"✅ 已将JSON格式转换为自然语言（{len(converted)}字符）")
                
                # 添加友好的提示文本
                result = f"""请完成以下任务：

{converted}

请用专业且{json_data.get('语气风格', '友好')}的语气完成这个任务，确保输出符合所有要求。"""
                
                return result
        
        except json.JSONDecodeError:
            print("⚠️ JSON解析失败，保持原样")
            pass
    
    # 检测是否包含大量JSON特征（即使不是完整JSON）
    if cleaned.count('{') > 3 and cleaned.count(':') > 3 and cleaned.count('"') > 6:
        print("⚠️ 检测到类似JSON的结构化文本，但不是完整JSON格式")
        # 保持原样，但添加警告
    
    return cleaned


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
    enhancement_techniques: list[str] = Field(description="使用的优化技术列表", default=[])
    enhancement_techniques: list[str] = Field(description="使用的优化技术列表", default=[])

class SummarizationPrompt(BaseModel):
    """优化后的摘要任务 Prompt 结构"""
    thinking_process: str = Field(description="优化分析过程")
    role_setting: str = Field(description="角色设定，如：你是一位专业的技术文档编写专家")
    extraction_rules: list[str] = Field(description="具体的提取规则，如：必须保留所有数字、日期和责任人")
    negative_constraints: list[str] = Field(description="负面约束，明确告诉模型不要做什么")
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


class SearchSpace(BaseModel):
    """随机搜索的变量空间"""
    roles: list[str] = Field(description="5个适合该任务的不同角色设定")
    styles: list[str] = Field(description="5种不同的回答风格")
    techniques: list[str] = Field(description="3种不同的提示技巧，如: step-by-step, few-shot, direct")


class SearchResult(BaseModel):
    """单次搜索的结果"""
    iteration_id: int = Field(description="迭代编号")
    role: str = Field(description="使用的角色")
    style: str = Field(description="使用的风格")
    technique: str = Field(description="使用的技巧")
    full_prompt: str = Field(description="完整的组合 Prompt")
    avg_score: float = Field(description="在验证集上的平均得分")
    task_type: str = Field(description="任务类型：classification/summarization/translation")


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
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            else:
                # NVIDIA 使用普通调用
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            
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
            result_dict = safe_json_loads(content)
            
            print("✅ JSON 解析成功")
            print("🔨 正在验证数据结构...")
            optimized = OptimizedPrompt(**result_dict)
            
            # 清理 improved_prompt 字段（如果大模型错误地返回了JSON格式）
            print("🧹 检查并清理 improved_prompt 格式...")
            original_prompt = optimized.improved_prompt
            cleaned_prompt = clean_improved_prompt(original_prompt)
            
            if cleaned_prompt != original_prompt:
                print(f"✨ improved_prompt 已从 {len(original_prompt)} 字符优化为 {len(cleaned_prompt)} 字符")
                # 创建新的优化结果对象
                optimized = OptimizedPrompt(
                    thinking_process=optimized.thinking_process,
                    improved_prompt=cleaned_prompt,
                    enhancement_techniques=optimized.enhancement_techniques,
                    keywords_added=optimized.keywords_added,
                    structure_applied=optimized.structure_applied
                )
            else:
                print("✅ improved_prompt 格式正确，无需清理")
            
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
                               labels: list[str]) -> ClassificationPrompt:
        """
        针对分类任务的优化函数
        
        Args:
            task_description: 分类任务描述，如 "判断用户评论的情感倾向"
            labels: 目标标签列表，如 ["Positive", "Negative", "Neutral"]
            
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
        
        # 构建分类任务专用的 Meta-Prompt（简化版）
        # 不使用 f-string，避免花括号示例被解析
        labels_str = ', '.join(labels)
        first_label = labels[0] if labels else '标签'
        
        system_prompt = """
你是一个专门构建 AI 文本分类器的专家。你的目标是编写一个**简洁高效**的分类 Prompt。

**任务描述**：TASK_DESCRIPTION_PLACEHOLDER
**目标标签**：LABELS_PLACEHOLDER

**你的任务**：

1. **角色设定**
   - 为分类器设定一个专业的角色身份
   - 增强模型对任务的理解和执行准确度

2. **格式锁定 (Output Format)**
   - **关键要求**：模型必须**只输出标签名称本身**，不要输出JSON格式、不要加引号、不要解释
   - 例如：如果标签是"积极"，就只输出：积极
   - **禁止**输出：带花括号的JSON格式 或 带引号 或 带说明文字
   - 确保输出可以被代码轻松解析
   - 在 Prompt 末尾明确强调："请只输出标签名称，不要输出其他任何内容"

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程
- role_definition: 角色设定描述
- label_definitions: 空字典
- few_shot_examples: 空列表
- reasoning_guidance: 空字符串
- output_format: 输出格式要求说明
- final_prompt: 完整的、可直接使用的分类 Prompt
- enhancement_techniques: 使用的优化技术列表

**关键要求 - final_prompt 必须包含占位符**：
- final_prompt 必须是一个完整的、结构清晰的、可以直接复制使用的分类 Prompt
- **必须在 Prompt 中明确标注待分类文本的位置**，使用以下任一占位符格式：
  * [待分类文本] （推荐）
  * [输入评论]
  * [待处理文本]
- 占位符应该放在合理的位置，比如：
  * "评论内容：[待分类文本]"
  * "请分析以下文本：[待分类文本]"
- **不要**只说"分析这个评论"或"判断情感"而不提供具体的插入位置
- final_prompt 必须是可以通过简单的字符串替换就能使用的模板

**示例正确格式**：
```
你是专业的分类专家。
可选的标签有：LABELS_PLACEHOLDER

现在请对以下文本进行分类：
[待分类文本]

**重要**：请只输出标签名称（如：FIRST_LABEL_PLACEHOLDER），不要输出JSON格式，不要加任何解释。
```
"""
        
        # 手动替换占位符
        system_prompt = system_prompt.replace("TASK_DESCRIPTION_PLACEHOLDER", task_description)
        system_prompt = system_prompt.replace("LABELS_PLACEHOLDER", labels_str)
        system_prompt = system_prompt.replace("FIRST_LABEL_PLACEHOLDER", first_label)
        
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
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            print(f"📑 响应前200字符: {content[:200]}...")
            
            # 提取 JSON
            if "```json" in content:
                print("🔍 检测到 JSON 代码块，正在提取...")
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                print("🔍 检测到代码块，正在提取...")
                content = content.split("```")[1].split("```")[0].strip()
            
            print("⚙️ 正在解析 JSON...")
            print(f"📑 清理后的JSON前300字符: {content[:300]}...")
            result_dict = safe_json_loads(content)
            
            print("✅ JSON 解析成功")
            print(f"🔑 解析得到的字段: {list(result_dict.keys())}")
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
            
            # 如果是Pydantic验证错误，显示更详细的信息
            if hasattr(e, 'errors'):
                print(f"\n🔴 Pydantic 验证错误详情:")
                for err in e.errors():
                    print(f"  - 字段: {err.get('loc', 'unknown')}")
                    print(f"    错误: {err.get('msg', 'unknown')}")
                    print(f"    类型: {err.get('type', 'unknown')}")
            
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

4. **思考步骤设计 (Step-by-Step Guide)**
   - 给模型明确的处理流程，如：
     Step 1: 通读全文，标记关键信息
     Step 2: 根据关注点筛选内容
     Step 3: 按结构组织信息
     Step 4: 精简表达，确保准确

5. **关注点锚定 (Focus Areas)**
   - 将用户的核心关注点转化为具体的信息类别
   - 在 Prompt 中多次强调这些关注点的优先级

**输出要求**：
请以 JSON 格式返回结果，包含以下字段：
- thinking_process: 你的优化思考过程
- role_setting: 角色设定描述
- extraction_rules: 提取规则列表（至少3-5条）
- negative_constraints: 负面约束列表（至少3条）
- step_by_step_guide: 处理步骤说明
- focus_areas: 核心关注点列表
- final_prompt: 完整的、可直接使用的摘要 Prompt（用 {{{{text}}}} 作为待摘要文本的占位符）

**重要**：
- final_prompt 必须是一个完整的、结构清晰的、可以直接复制使用的摘要 Prompt
- 其中待摘要的文本用双花括号包裹的text占位符表示
- 所有规则和约束都要整合进 final_prompt 中
- 确保JSON格式正确，字符串中的换行符需要正确转义
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
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            print(f"📑 响应前200字符: {content[:200]}...")
            
            # 提取 JSON
            if "```json" in content:
                print("🔍 检测到 JSON 代码块，正在提取...")
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                print("🔍 检测到代码块，正在提取...")
                content = content.split("```")[1].split("```")[0].strip()
            
            print("⚙️ 正在解析 JSON...")
            print(f"📑 清理后的JSON前300字符: {content[:300]}...")
            result_dict = safe_json_loads(content)
            
            print("✅ JSON 解析成功")
            print(f"🔑 解析得到的字段: {list(result_dict.keys())}")
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
            
            # 如果是Pydantic验证错误，显示更详细的信息
            if hasattr(e, 'errors'):
                print(f"\n🔴 Pydantic 验证错误详情:")
                for err in e.errors():
                    print(f"  - 字段: {err.get('loc', 'unknown')}")
                    print(f"    错误: {err.get('msg', 'unknown')}")
                    print(f"    类型: {err.get('type', 'unknown')}")
            
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
- 其中待翻译的文本用双花括号包裹的text占位符表示
- 所有规则、术语表、风格指南都要整合进 final_prompt 中
- 务必体现"领域专家 + 术语锁定 + 三步翻译法"的核心策略
- 确保JSON格式正确，字符串中的换行符需要正确转义
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
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            else:
                print("🔧 使用 NVIDIA 标准调用")
                response = self.llm.invoke(messages)
                time.sleep(0.5)  # API 调用延迟，避免频率过快
            
            # 解析结果
            content = response.content
            print(f"📥 收到响应，长度: {len(content)} 字符")
            print(f"📑 响应前200字符: {content[:200]}...")
            
            # 提取 JSON
            if "```json" in content:
                print("🔍 检测到 JSON 代码块，正在提取...")
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                print("🔍 检测到代码块，正在提取...")
                content = content.split("```")[1].split("```")[0].strip()
            
            print("⚙️ 正在解析 JSON...")
            print(f"📑 清理后的JSON前300字符: {content[:300]}...")
            result_dict = safe_json_loads(content)
            
            print("✅ JSON 解析成功")
            print(f"🔑 解析得到的字段: {list(result_dict.keys())}")
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
            
            # 如果是Pydantic验证错误，显示更详细的信息
            if hasattr(e, 'errors'):
                print(f"\n🔴 Pydantic 验证错误详情:")
                for err in e.errors():
                    print(f"  - 字段: {err.get('loc', 'unknown')}")
                    print(f"    错误: {err.get('msg', 'unknown')}")
                    print(f"    类型: {err.get('type', 'unknown')}")
            
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

⚠️ **重要：明确你的角色定位**
- 你的角色：Prompt 优化专家，负责改进和优化 Prompt
- 你的任务：分析并优化用户提供的原始 Prompt，而不是执行这个 Prompt
- 关键区别：
  * ❌ 错误理解：用户说"推荐索尼耳机" → 你直接推荐耳机（执行任务）
  * ✅ 正确理解：用户说"推荐索尼耳机" → 你优化这句话，生成一个更好的 Prompt（优化任务）
  
**举例说明**：
- 用户输入："写一篇关于AI的文章"
- 你不应该：直接写文章
- 你应该：优化这个请求，生成类似"你是一位资深科技作家。请撰写一篇关于AI的深度分析文章，要求：1. 涵盖AI的发展历史... 2. 字数2000字... 3. 包含具体案例..."

**你的任务流程**：

1. **深度理解**：仔细分析用户的原始 Prompt 和场景描述，识别其核心意图和隐含需求
   - 记住：你是在分析这个 Prompt 本身，不是在执行它

2. **场景融合（关键步骤）**：
   - ⚠️ **必须将场景上下文信息完整融入到优化后的 Prompt 中**
   - 场景描述中的所有关键信息（如目标平台、受众、语气风格、特殊要求等）都必须在 improved_prompt 中明确体现

3. **三大优化策略**：
   
   a) **语义扩展 (Semantic Expansion)**
      - 补充缺失的上下文信息
      - 明确隐含的约束条件
      - 规范输出格式要求
      - **将场景描述中的信息转化为明确的要求**
   
   b) **关键词增强 (Keywords Enhancement)**
      - 识别任务所属的专业领域
      - 加入该领域的专业术语和行业概念
      - 用精确的词汇替换模糊表达
      - **提取场景中的关键特征词**
   
   c) **结构化重写 (Template Application)**
      - 必须使用 **{template_name}** 框架进行重写
      - 确保 Prompt 逻辑清晰、层次分明

4. **优化原则**（本次优化重点关注）：
{principles_text}
{extra_text}

**场景上下文**：{scene_desc if scene_desc else "通用场景"}

⚠️ **再次强调**：优化后的 Prompt 必须包含场景上下文中的所有关键信息（平台、受众、语气、特殊要求等），不要遗漏！

**输出要求**：
你必须以标准JSON格式返回结果，包含以下5个字段（全部必需）：

1. thinking_process - 字符串类型，记录你的优化思考过程（约200字）。说明你如何理解原始Prompt，以及为什么这样优化。
2. improved_prompt - 字符串类型，优化后的完整Prompt文本（自然语言形式）。⚠️ 这是优化后的指令，不是执行结果！
3. enhancement_techniques - 数组类型，包含使用的优化技术，如["语义扩展", "关键词增强"]
4. keywords_added - 数组类型，包含新增的关键词，如["专业术语1", "专业术语2"]
5. structure_applied - 字符串类型，应用的框架名称，如"CO-STAR"

⚠️ 重要提示：
- 不要使用Markdown格式（即不要用 **字段名**: 的形式）
- 必须返回纯JSON格式
- improved_prompt字段必须是自然语言文本，不能是JSON对象或结构化数据
- improved_prompt是一个"改进后的指令"，不是"执行这个指令的结果"
- 如果用户输入本身是JSON格式，请理解其含义后转换为自然语言的Prompt

正确的JSON结构应该是：根对象包含5个字段，其中3个是字符串，2个是字符串数组。

**关键说明 - improved_prompt 字段的正确格式**：

⚠️ **再次强调：你是在优化Prompt，不是在执行Prompt！**

improved_prompt字段应该是自然语言形式的完整指令文本，而不是JSON或结构化数据。

错误做法：在improved_prompt中返回JSON对象或键值对形式的数据。

❌ **常见错误示例（小模型容易犯的错误）**：

用户输入："推荐索尼降噪耳机"

错误输出（直接执行任务）：
```
improved_prompt: "我推荐索尼WH-1000XM5降噪耳机，价格约2000元，降噪效果出色..."
```
这是错误的！因为你直接推荐了耳机，而不是生成一个让别人推荐耳机的Prompt。

✅ **正确示例（优化Prompt）**：

用户输入："推荐索尼降噪耳机"
场景："发在小红书上，目标是学生党，突出性价比和降噪，语气要活泼"

正确输出（生成优化后的指令）：
```
improved_prompt: "你是一位……，擅长……。请为用户……"
```

看到区别了吗？improved_prompt 是一个"指令"（告诉AI做什么），不是"结果"（直接给出答案）。

注意：如果用户的原始输入本身就是JSON格式，你需要理解其含义后转换为流畅的自然语言Prompt。
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
            time.sleep(0.3)  # API 调用延迟，避免频率过快（A/B 测试需要较长等待）
            result_original = response_original.content
            
            # 运行优化后的 Prompt
            response_optimized = self.llm.invoke(optimized_prompt)
            time.sleep(0.3)  # API 调用延迟，避免频率过快（A/B 测试需要较长等待）
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


    def generate_search_space(self, task_description: str, task_type: str = "classification") -> SearchSpace:
        """
        让 LLM 自动分析任务，生成可供搜索的变量池
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            
        Returns:
            SearchSpace 对象，包含 roles, styles, techniques
        """
        print(f"\n{'='*60}")
        print(f"🧠 生成搜索空间")
        print(f"{'='*60}")
        print(f"任务类型: {task_type}")
        print(f"任务描述: {task_description}")
        print(f"{'='*60}\n")
        
        system_prompt = """
你是一个 Prompt 策略生成器。你的任务是为给定的任务设计多种可能的 Prompt 组件。

**输出要求：**
请以 JSON 格式返回，包含三个数组：
- roles: 5个不同的角色设定
- styles: 5种不同的语气/风格  
- techniques: 3种不同的提示工程技巧

**角色示例**：
- 对于分类任务：资深数据分析师、心理学家、客服经理、产品经理、社交媒体专家
- 对于摘要任务：新闻编辑、技术文档专家、会议记录员、研究员、顾问
- 对于翻译任务：专业译者、双语作家、本地化专家、技术翻译、文学翻译

**风格示例**：
- 严谨学术、通俗易懂、简洁明了、详尽全面、创意幽默

**技巧示例**：
- "Let's think step by step" (思维链)
- "Provide only the label without explanation" (直接回答)
- "First analyze the features, then make a decision" (特征分析)
- "Use few-shot examples" (少样本学习)
- "Output in JSON format" (格式化输出)

请确保输出是有效的 JSON 格式。
"""
        
        user_prompt = f"""
任务类型：{task_type}
任务描述：{task_description}

请为这个任务设计：
1. 5个不同的角色定位（从保守到创新，覆盖不同专业背景）
2. 5种不同的回答风格/语气
3. 3种不同的提示工程技巧或指令模式

确保输出纯 JSON 格式。
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        try:
            # 调用 LLM
            print("📡 调用 LLM 生成搜索空间...")
            messages = prompt_template.format_messages(task_type=task_type, task_description=task_description)
            response = self.llm.invoke(messages)
            
            time.sleep(0.5)  # API 调用延迟，避免频率过快（搜索空间生成较快）
            
            print(f"✅ LLM 响应成功")
            print(f"原始响应长度: {len(response.content)} 字符")
            
            # 解析 JSON
            content = response.content.strip()
            print(f"\n🔍 解析 JSON 响应...")
            print(f"原始内容前100字符: {content[:100]}...")
            
            # 移除可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
                print("  移除了 ```json 标记")
            if content.startswith("```"):
                content = content[3:]
                print("  移除了 ``` 标记")
            if content.endswith("```"):
                content = content[:-3]
                print("  移除了尾部 ``` 标记")
            content = content.strip()
            
            # 提取 JSON 部分（从第一个 { 到最后一个 }）
            # 这样可以忽略 JSON 前后的额外文本
            try:
                start_idx = content.index('{')
                end_idx = content.rindex('}') + 1
                content = content[start_idx:end_idx]
                print(f"  提取了纯 JSON 内容（从第 {start_idx} 到第 {end_idx} 字符）")
            except ValueError:
                print("  ⚠️ 未找到完整的 JSON 对象，尝试直接解析")
            
            print(f"清理后内容前100字符: {content[:100]}...")
            
            data = json.loads(content)
            print(f"✅ JSON 解析成功")
            print(f"  - roles: {len(data.get('roles', []))} 个")
            print(f"  - styles: {len(data.get('styles', []))} 个")
            print(f"  - techniques: {len(data.get('techniques', []))} 个")
            
            # 处理 LLM 可能返回对象数组的情况
            # 如果返回 [{"name": "xxx", "description": "yyy"}]，提取 name 字段
            def extract_names(items):
                """提取字符串或对象数组中的名称"""
                if not items:
                    return []
                result = []
                for item in items:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict) and 'name' in item:
                        result.append(item['name'])
                        print(f"    提取: {item['name']}")
                return result
            
            # 转换数据格式
            print(f"🔄 处理数据格式...")
            data['roles'] = extract_names(data.get('roles', []))
            data['styles'] = extract_names(data.get('styles', []))
            data['techniques'] = extract_names(data.get('techniques', []))
            
            print(f"  ✅ roles: {data['roles']}")
            print(f"  ✅ styles: {data['styles']}")
            print(f"  ✅ techniques: {data['techniques']}")
            
            result = SearchSpace(**data)
            print(f"\n✅ 搜索空间生成完成！\n")
            return result
            
        except Exception as e:
            print(f"\n❌ 生成搜索空间失败！")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {e}")
            
            import traceback
            print(f"\n完整错误堆栈：")
            traceback.print_exc()
            
            print(f"\n⚠️ 使用默认搜索空间...\n")
            # 返回默认的搜索空间
            return SearchSpace(
                roles=[
                    "资深专家",
                    "数据分析师",
                    "领域顾问",
                    "实践者",
                    "研究员"
                ],
                styles=[
                    "严谨学术",
                    "通俗易懂",
                    "简洁明了",
                    "详尽全面",
                    "系统化"
                ],
                techniques=[
                    "Let's think step by step",
                    "Provide direct answer without explanation",
                    "Analyze features then decide"
                ]
            )
    
    
    def run_random_search(
        self, 
        task_description: str,
        task_type: str,
        test_dataset: list[dict],
        search_space: SearchSpace,
        iterations: int = 5,
        progress_callback=None
    ) -> tuple[list[SearchResult], SearchResult]:
        """
        执行随机搜索优化
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{'input': '...', 'ground_truth': '...'}]
            search_space: 搜索空间
            iterations: 搜索迭代次数
            progress_callback: 进度回调函数 callback(current, total, message)
            
        Returns:
            (所有结果列表, 最佳结果)
        """
        from metrics import MetricsCalculator
        
        results_log = []
        calc = MetricsCalculator()
        
        print(f"\n{'='*60}")
        print(f"开始随机搜索优化 - {iterations} 次迭代")
        print(f"{'='*60}\n")
        
        for i in range(iterations):
            # 1. 随机采样：摇骰子组合 Prompt
            chosen_role = random.choice(search_space.roles)
            chosen_style = random.choice(search_space.styles)
            chosen_tech = random.choice(search_space.techniques)
            
            print(f"迭代 {i+1}/{iterations}")
            print(f"  角色: {chosen_role}")
            print(f"  风格: {chosen_style}")
            print(f"  技巧: {chosen_tech}")
            
            # 2. 拼装候选 Prompt
            if task_type == "classification":
                candidate_prompt = f"""你是一位{chosen_role}。

任务：{task_description}

风格要求：{chosen_style}

指令：{chosen_tech}

请对以下文本进行分类：
[待分类文本]

只输出分类标签，不要额外解释。
"""
            elif task_type == "summarization":
                candidate_prompt = f"""你是一位{chosen_role}。

任务：{task_description}

风格要求：{chosen_style}

指令：{chosen_tech}

请对以下文本进行摘要：
[待摘要文本]

请按照要求输出摘要。
"""
            elif task_type == "translation":
                candidate_prompt = f"""你是一位{chosen_role}。

任务：{task_description}

风格要求：{chosen_style}

指令：{chosen_tech}

请翻译以下文本：
[待翻译文本]

只输出翻译结果，不要额外说明。
"""
            else:
                candidate_prompt = f"""角色: {chosen_role}
风格: {chosen_style}
任务: {task_description}
指令: {chosen_tech}

输入: {{input}}
"""
            
            # 3. 在测试集上跑分
            scores = []
            for case_idx, case in enumerate(test_dataset):
                try:
                    print(f"\n  📝 测试样本 {case_idx+1}/{len(test_dataset)}")
                    print(f"    输入: {case['input'][:50]}..." if len(case['input']) > 50 else f"    输入: {case['input']}")
                    print(f"    标准答案: {case['ground_truth']}")
                    
                    # 替换占位符
                    if task_type == "classification":
                        prompt_filled = candidate_prompt.replace("[待分类文本]", case['input'])
                    elif task_type == "summarization":
                        prompt_filled = candidate_prompt.replace("[待摘要文本]", case['input'])
                    elif task_type == "translation":
                        prompt_filled = candidate_prompt.replace("[待翻译文本]", case['input'])
                    else:
                        prompt_filled = candidate_prompt.replace("{{input}}", case['input'])
                    
                    # 调用 LLM
                    print(f"    🤖 调用 LLM...")
                    response = self.llm.invoke(prompt_filled)
                    time.sleep(0.3)  # API 调用延迟，避免频率过快（随机搜索批量调用）
                    prediction = response.content.strip()
                    print(f"    💬 LLM 输出: {prediction[:80]}..." if len(prediction) > 80 else f"    💬 LLM 输出: {prediction}")
                    
                    # 计算分数
                    if task_type == "classification":
                        # 分类任务：简单匹配
                        score = 100.0 if prediction == case['ground_truth'] else 0.0
                        print(f"    📊 匹配结果: {'✅ 正确' if score == 100.0 else '❌ 错误'}")
                    elif task_type == "summarization":
                        # 摘要任务：ROUGE
                        print(f"    📊 计算 ROUGE 分数...")
                        rouge_scores = calc.calculate_rouge(prediction, case['ground_truth'])
                        score = rouge_scores['rouge1']  # 使用 ROUGE-1 作为评分
                        print(f"    📊 ROUGE-1: {score:.2f}")
                    elif task_type == "translation":
                        # 翻译任务：BLEU
                        print(f"    📊 计算 BLEU 分数...")
                        score = calc.calculate_bleu(prediction, case['ground_truth'])
                        print(f"    📊 BLEU: {score:.2f}")
                    else:
                        score = 50.0  # 默认分数
                    
                    scores.append(score)
                    print(f"    ✅ 得分: {score:.1f}")
                    
                except Exception as e:
                    print(f"    ❌ 评估失败！")
                    print(f"    错误类型: {type(e).__name__}")
                    print(f"    错误信息: {e}")
                    scores.append(0.0)
            
            # 计算平均分
            avg_score = sum(scores) / len(scores) if scores else 0.0
            print(f"  平均得分: {avg_score:.2f}\n")
            
            # 4. 记录结果
            result = SearchResult(
                iteration_id=i+1,
                role=chosen_role,
                style=chosen_style,
                technique=chosen_tech,
                full_prompt=candidate_prompt,
                avg_score=avg_score,
                task_type=task_type
            )
            results_log.append(result)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i+1, iterations, f"完成迭代 {i+1}/{iterations}，得分: {avg_score:.2f}")
        
        # 找出最佳结果
        best_result = max(results_log, key=lambda x: x.avg_score)
        
        print(f"{'='*60}")
        print(f"搜索完成！最佳得分: {best_result.avg_score:.2f}")
        print(f"最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"{'='*60}\n")
        
        return results_log, best_result
    
    def run_genetic_algorithm(
        self,
        task_description: str,
        task_type: str,
        test_dataset: list,
        search_space: 'SearchSpace',
        generations: int = 5,
        population_size: int = 8,
        elite_ratio: float = 0.2,
        mutation_rate: float = 0.2,
        progress_callback: Optional[callable] = None
    ) -> tuple[list, 'SearchResult', list]:
        """
        遗传算法优化 Prompt
        
        核心思想：通过多代进化，让优秀的 Prompt 组合"繁衍"出更好的后代
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{"input": "...", "ground_truth": "..."}, ...]
            search_space: 搜索空间
            generations: 进化代数（越多越好，但消耗更大）
            population_size: 种群规模（每代有多少个个体）
            elite_ratio: 精英保留比例（保留多少优秀个体到下一代）
            mutation_rate: 变异概率（引入随机性避免局部最优）
            progress_callback: 进度回调函数 callback(gen, total_gen, best_score, avg_score)
        
        Returns:
            (all_results, best_result, evolution_history)
            - all_results: 所有迭代的结果
            - best_result: 最佳结果
            - evolution_history: 进化历史 [{"generation": 1, "best_score": 85.0, "avg_score": 78.5}, ...]
        """
        print(f"\n{'='*60}")
        print(f"🧬 遗传算法优化开始")
        print(f"{'='*60}")
        print(f"📋 任务类型: {task_type}")
        print(f"📊 代数: {generations}, 种群规模: {population_size}")
        print(f"🔬 精英比例: {elite_ratio * 100}%, 变异率: {mutation_rate * 100}%")
        print(f"📏 测试集样本数: {len(test_dataset)}")
        print(f"💰 预计 API 调用: {generations * population_size * len(test_dataset)} 次")
        print(f"{'='*60}\n")
        
        def create_individual():
            """创建一个随机个体（Prompt 组合）"""
            return {
                "role": random.choice(search_space.roles),
                "style": random.choice(search_space.styles),
                "technique": random.choice(search_space.techniques),
                "score": 0.0,
                "full_prompt": ""
            }
        
        def evaluate_individual(individual, generation: int, index: int):
            """评估个体的适应度（在测试集上的得分）"""
            role = individual["role"]
            style = individual["style"]
            technique = individual["technique"]
            
            # 构建 Prompt（根据任务类型优化输出格式）
            if task_type == "classification":
                # 分类任务：强制要求只输出标签
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出分类标签（如：积极、消极、中立），不要输出任何解释、分析或其他内容。**

输入：{{text}}
输出（只输出标签）："""
            else:
                # 其他任务：常规格式
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

输入：{{text}}
"""
            
            individual["full_prompt"] = prompt_template
            
            # 在测试集上评估
            predictions = []
            ground_truths = []
            
            print(f"  第 {generation} 代个体 {index}: {role} + {style} + {technique}")
            
            for idx, sample in enumerate(test_dataset, 1):
                test_input = sample.get("input", "")
                ground_truth = sample.get("ground_truth", "")
                
                # 替换占位符
                final_prompt = prompt_template.replace("{{text}}", test_input)
                
                # 调用 LLM（带重试机制）
                prediction = ""
                max_retries = 3
                retry_delay = 2.0
                
                for retry in range(max_retries):
                    try:
                        response = self.llm.invoke(final_prompt)
                        time.sleep(1.0)  # API 调用延迟，遗传算法密集调用需要更长延迟
                        prediction = response.content.strip()
                        break  # 成功则跳出重试循环
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "Too Many Requests" in error_msg:
                            if retry < max_retries - 1:
                                wait_time = retry_delay * (2 ** retry)  # 指数退避: 2s, 4s, 8s
                                print(f"    ⚠️ 样本 {idx} 请求过快，等待 {wait_time:.0f}s 后重试（第{retry+1}次）...")
                                time.sleep(wait_time)
                                continue
                            else:
                                print(f"    ❌ 样本 {idx} 达到最大重试次数，跳过")
                                prediction = ""
                                break
                        else:
                            print(f"    ❌ 样本 {idx} 评估失败: {error_msg[:50]}")
                            prediction = ""
                            break
                
                # 清理预测结果
                if prediction and task_type == "classification":
                    # 取第一行
                    prediction = prediction.split('\n')[0].strip()
                    # 移除常见的前缀词
                    for prefix in ["输出：", "输出:", "结果：", "结果:", "分类：", "分类:", "标签：", "标签:"]:
                        if prediction.startswith(prefix):
                            prediction = prediction[len(prefix):].strip()
                    # 如果包含多个词，尝试提取关键标签
                    if len(prediction) > 10:  # 太长了，可能是句子
                        # 尝试在句子中查找标签关键词
                        for label in ["积极", "消极", "中立", "正面", "负面", "中性"]:
                            if label in prediction:
                                prediction = label
                                break
                
                predictions.append(prediction)
                ground_truths.append(ground_truth)
                
                # 调试输出：显示预测和真实值
                if generation == 1 and index == 1 and idx <= 2:  # 只显示第一代第一个体的前2个样本
                    print(f"      [调试] 样本{idx} 预测='{prediction}' vs 真实='{ground_truth}'")
            
            # 计算分数
            calc = MetricsCalculator()
            
            # 过滤掉空预测（评估失败的样本）
            valid_pairs = [(p, g) for p, g in zip(predictions, ground_truths) if p]
            
            if not valid_pairs:
                # 所有样本都失败了
                score = 0.0
                print(f"    → 得分: 0.00 (所有样本评估失败)")
            else:
                valid_predictions = [p for p, g in valid_pairs]
                valid_ground_truths = [g for p, g in valid_pairs]
                
                if task_type == "classification":
                    score = calc.calculate_accuracy(valid_predictions, valid_ground_truths)
                elif task_type == "summarization":
                    scores = [calc.calculate_rouge(p, g)['rougeL'] for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                elif task_type == "translation":
                    scores = [calc.calculate_bleu(p, g) for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                else:
                    score = 0.0
                
                # 如果部分样本失败，显示成功率
                failed_count = len(predictions) - len(valid_pairs)
                if failed_count > 0:
                    print(f"    → 得分: {score:.2f} ({len(valid_pairs)}/{len(predictions)} 样本成功)")
                else:
                    print(f"    → 得分: {score:.2f}")
            
            individual["score"] = score
            
            # 如果得分为0且有成功的样本，显示调试信息
            if score == 0.0 and valid_pairs:
                print(f"      [0分调试] 预测='{valid_predictions[0][:50]}' vs 真实='{valid_ground_truths[0]}'")
            
            return individual
        
        def crossover(parent1, parent2):
            """交叉：孩子继承父母的优良基因"""
            child = {
                "role": random.choice([parent1["role"], parent2["role"]]),
                "style": random.choice([parent1["style"], parent2["style"]]),
                "technique": random.choice([parent1["technique"], parent2["technique"]]),
                "score": 0.0,
                "full_prompt": ""
            }
            return child
        
        def mutate(individual):
            """变异：随机改变某些基因，引入新可能性"""
            if random.random() < mutation_rate:
                individual["role"] = random.choice(search_space.roles)
                print(f"    🔀 变异: 更换角色 → {individual['role']}")
            if random.random() < mutation_rate:
                individual["style"] = random.choice(search_space.styles)
                print(f"    🔀 变异: 更换风格 → {individual['style']}")
            if random.random() < mutation_rate:
                individual["technique"] = random.choice(search_space.techniques)
                print(f"    🔀 变异: 更换技巧 → {individual['technique']}")
            return individual
        
        # === 遗传算法主循环 ===
        
        # 初始化第一代种群
        print(f"🧬 第 1 代：初始化种群（{population_size} 个个体）")
        population = [create_individual() for _ in range(population_size)]
        
        evolution_history = []
        all_results = []
        
        for gen in range(generations):
            print(f"\n{'='*60}")
            print(f"🧬 第 {gen + 1}/{generations} 代进化")
            print(f"{'='*60}")
            
            # 评估当前种群
            for i, individual in enumerate(population, 1):
                evaluate_individual(individual, gen + 1, i)
            
            # 按适应度排序
            population.sort(key=lambda x: x["score"], reverse=True)
            
            # 记录历史
            best_score = population[0]["score"]
            avg_score = sum(ind["score"] for ind in population) / len(population)
            
            evolution_history.append({
                "generation": gen + 1,
                "best_score": best_score,
                "avg_score": avg_score,
                "worst_score": population[-1]["score"]
            })
            
            print(f"\n📊 第 {gen + 1} 代统计:")
            print(f"  🥇 最高分: {best_score:.2f}")
            print(f"  📊 平均分: {avg_score:.2f}")
            print(f"  📉 最低分: {population[-1]['score']:.2f}")
            print(f"  🏆 冠军: {population[0]['role']} + {population[0]['style']} + {population[0]['technique']}")
            
            # 保存所有结果
            for i, ind in enumerate(population):
                result = SearchResult(
                    iteration_id=gen * population_size + i + 1,
                    role=ind["role"],
                    style=ind["style"],
                    technique=ind["technique"],
                    full_prompt=ind["full_prompt"],
                    avg_score=ind["score"],
                    task_type=task_type
                )
                all_results.append(result)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(gen + 1, generations, best_score, avg_score)
            
            # 如果是最后一代，跳过繁衍
            if gen == generations - 1:
                break
            
            # 选择（精英策略）
            elite_count = max(1, int(population_size * elite_ratio))
            print(f"\n🧬 选择: 保留 {elite_count} 个精英到下一代")
            new_population = population[:elite_count].copy()
            
            # 繁衍（交叉 + 变异）
            print(f"🧬 繁衍: 生成 {population_size - elite_count} 个新个体")
            while len(new_population) < population_size:
                # 轮盘赌选择父母（更倾向于选择高分个体）
                # 简化版：从前50%中随机选
                parent_pool_size = max(2, population_size // 2)
                parent1 = random.choice(population[:parent_pool_size])
                parent2 = random.choice(population[:parent_pool_size])
                
                # 交叉
                child = crossover(parent1, parent2)
                
                # 变异
                child = mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        # 最终结果
        best_result = max(all_results, key=lambda x: x.avg_score)
        
        print(f"\n{'='*60}")
        print(f"🏆 遗传算法完成！")
        print(f"{'='*60}")
        print(f"🥇 最终冠军得分: {best_result.avg_score:.2f}")
        print(f"🧬 最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"📈 进化增益: {evolution_history[-1]['best_score'] - evolution_history[0]['best_score']:.2f} 分")
        print(f"{'='*60}\n")
        
        return all_results, best_result, evolution_history

    def run_bayesian_optimization(
        self,
        task_description: str,
        task_type: str,
        test_dataset: list,
        search_space: 'SearchSpace',
        n_trials: int = 20,
        progress_callback: Optional[callable] = None
    ) -> tuple[list, 'SearchResult', list]:
        """
        贝叶斯优化 Prompt
        
        核心思想：利用概率模型（TPE）智能选择下一个尝试的参数组合，
        用最少的尝试次数找到最优解，比随机搜索效率高得多。
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{"input": "...", "ground_truth": "..."}, ...]
            search_space: 搜索空间
            n_trials: 尝试次数（贝叶斯优化通常20-50次就能找到好结果）
            progress_callback: 进度回调函数 callback(trial, total_trials, best_score)
        
        Returns:
            (all_results, best_result, trial_history)
            - all_results: 所有试验的结果
            - best_result: 最佳结果
            - trial_history: 试验历史 [{"trial": 1, "score": 85.0, "params": {...}}, ...]
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError("贝叶斯优化需要 optuna 库。请运行: pip install optuna")
        
        print(f"\n{'='*60}")
        print(f"🧐 贝叶斯优化开始")
        print(f"{'='*60}")
        print(f"📋 任务类型: {task_type}")
        print(f"🔬 使用算法: TPE (Tree-structured Parzen Estimator)")
        print(f"🎯 尝试次数: {n_trials}")
        print(f"📏 测试集样本数: {len(test_dataset)}")
        print(f"💰 预计 API 调用: {n_trials * len(test_dataset)} 次")
        print(f"💡 贝叶斯优化会根据历史结果智能选择下一个参数组合")
        print(f"{'='*60}\n")
        
        all_results = []
        trial_history = []
        best_score_so_far = 0.0
        
        def objective(trial):
            """Optuna 的目标函数"""
            nonlocal best_score_so_far
            
            # 让 Optuna 建议参数
            role = trial.suggest_categorical('role', search_space.roles)
            style = trial.suggest_categorical('style', search_space.styles)
            technique = trial.suggest_categorical('technique', search_space.techniques)
            
            print(f"\n{'='*60}")
            print(f"🔍 试验 {trial.number + 1}/{n_trials}")
            print(f"{'='*60}")
            
            # 显示策略提示
            if trial.number < 5:
                print(f"  📍 策略: 随机探索（建立初始模型）")
            else:
                # 计算与最佳结果的相似度（简单启发式）
                best_trials = sorted(trial_history, key=lambda x: x['score'], reverse=True)[:3]
                if best_trials and any(
                    (role == t['role'] or style == t['style'] or technique == t['technique'])
                    for t in best_trials
                ):
                    print(f"  📍 策略: 开发高分区域（基于历史最佳）")
                else:
                    print(f"  📍 策略: 探索新区域（避免局部最优）")
            
            print(f"  参数组合: {role} + {style} + {technique}")
            
            # 构建 Prompt
            if task_type == "classification":
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出分类标签（如：积极、消极、中立），不要输出任何解释、分析或其他内容。**

输入：{{text}}
输出（只输出标签）："""
            else:
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

输入：{{text}}
"""
            
            # 在测试集上评估
            predictions = []
            ground_truths = []
            
            for idx, sample in enumerate(test_dataset, 1):
                test_input = sample.get("input", "")
                ground_truth = sample.get("ground_truth", "")
                
                final_prompt = prompt_template.replace("{{text}}", test_input)
                
                # 显示当前进度
                print(f"    📝 评估样本 {idx}/{len(test_dataset)}...", end="", flush=True)
                
                # 调用 LLM（带重试机制）
                prediction = ""
                max_retries = 3
                retry_delay = 2.0
                
                for retry in range(max_retries):
                    try:
                        response = self.llm.invoke(final_prompt)
                        time.sleep(1.2)  # 增加延迟到 1.2s
                        prediction = response.content.strip()
                        print(" ✓")  # 成功标记
                        break
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "Too Many Requests" in error_msg:
                            if retry < max_retries - 1:
                                wait_time = retry_delay * (2 ** retry)
                                print(f" ⚠️ 限流，等待 {wait_time:.0f}s...")
                                time.sleep(wait_time)
                                continue
                            else:
                                print(" ✗ (达到重试上限)")
                                prediction = ""
                                break
                        else:
                            print(f" ✗ ({str(e)[:30]})")
                            prediction = ""
                            break
                
                # 清理预测结果
                if prediction and task_type == "classification":
                    prediction = prediction.split('\n')[0].strip()
                    for prefix in ["输出：", "输出:", "结果：", "结果:", "分类：", "分类:", "标签：", "标签:"]:
                        if prediction.startswith(prefix):
                            prediction = prediction[len(prefix):].strip()
                    if len(prediction) > 10:
                        for label in ["积极", "消极", "中立", "正面", "负面", "中性"]:
                            if label in prediction:
                                prediction = label
                                break
                
                predictions.append(prediction)
                ground_truths.append(ground_truth)
            
            # 计算分数
            calc = MetricsCalculator()
            valid_pairs = [(p, g) for p, g in zip(predictions, ground_truths) if p]
            
            if not valid_pairs:
                score = 0.0
            else:
                valid_predictions = [p for p, g in valid_pairs]
                valid_ground_truths = [g for p, g in valid_pairs]
                
                if task_type == "classification":
                    score = calc.calculate_accuracy(valid_predictions, valid_ground_truths)
                elif task_type == "summarization":
                    scores = [calc.calculate_rouge(p, g)['rougeL'] for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                elif task_type == "translation":
                    scores = [calc.calculate_bleu(p, g) for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                else:
                    score = 0.0
            
            # 记录结果
            result = SearchResult(
                iteration_id=trial.number + 1,
                role=role,
                style=style,
                technique=technique,
                full_prompt=prompt_template,
                avg_score=score,
                task_type=task_type
            )
            all_results.append(result)
            
            # 更新最佳分数
            if score > best_score_so_far:
                best_score_so_far = score
                print(f"  → 得分: {score:.2f} 🎉 新纪录！")
            else:
                print(f"  → 得分: {score:.2f}")
            
            # 记录试验历史
            trial_history.append({
                "trial": trial.number + 1,
                "score": score,
                "best_score": best_score_so_far,
                "role": role,
                "style": style,
                "technique": technique
            })
            
            # 进度回调
            if progress_callback:
                progress_callback(trial.number + 1, n_trials, best_score_so_far)
            
            # 试验间增加延迟，避免连续调用触发限流
            if trial.number < n_trials - 1:  # 不是最后一次
                print(f"  ⏸️  试验间冷却 2秒...")
                time.sleep(2.0)
            
            return score
        
        # 创建 Optuna Study（优化 TPE 参数）
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(
            direction="maximize",
            sampler=optuna.samplers.TPESampler(
                n_startup_trials=min(5, n_trials // 3),  # 前5次随机探索
                n_ei_candidates=24,  # 默认24，增加候选数量
                multivariate=True,  # 考虑参数间的相关性
                warn_independent_sampling=False,
                seed=None  # 移除固定种子，增加随机性
            )
        )
        
        # 执行优化
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        # 获取最佳结果
        best_trial = study.best_trial
        best_result = next(r for r in all_results if 
                          r.role == best_trial.params['role'] and
                          r.style == best_trial.params['style'] and
                          r.technique == best_trial.params['technique'])
        
        print(f"\n{'='*60}")
        print(f"🏆 贝叶斯优化完成！")
        print(f"{'='*60}")
        print(f"🥇 最佳得分: {best_result.avg_score:.2f}")
        print(f"🧬 最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"📊 收敛速度: 在第 {best_trial.number + 1} 次试验中找到最佳结果")
        
        # 分析优化效果
        scores = [h['score'] for h in trial_history]
        first_5_avg = sum(scores[:5]) / 5 if len(scores) >= 5 else sum(scores) / len(scores)
        last_5_avg = sum(scores[-5:]) / 5 if len(scores) >= 5 else sum(scores) / len(scores)
        
        print(f"\n📈 优化分析:")
        print(f"  前5次平均: {first_5_avg:.2f}")
        print(f"  后5次平均: {last_5_avg:.2f}")
        if last_5_avg >= first_5_avg:
            print(f"  ✅ 后期表现提升 {last_5_avg - first_5_avg:.2f} 分（智能优化生效）")
        else:
            print(f"  ⚠️ 后期探索其他区域（防止陷入局部最优）")
        
        print(f"{'='*60}\n")
        
        return all_results, best_result, trial_history


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
