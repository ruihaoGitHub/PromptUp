"""
数据模型定义模块
包含所有 Pydantic 数据模型
"""
from pydantic import BaseModel, Field


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
