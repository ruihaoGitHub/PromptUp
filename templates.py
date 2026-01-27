"""
Prompt 模板库
定义多种经典的 Prompt Engineering 框架
"""

# CO-STAR 框架 (Context, Objective, Style, Tone, Audience, Response)
COSTAR_TEMPLATE = """
请按照 CO-STAR 框架重写以下 Prompt：

**Context (背景/上下文)**：{context}
- 补充任务的背景信息、前置条件

**Objective (目标)**：{objective}
- 明确具体要达成的目标

**Style (风格)**：{style}
- 指定输出的风格（如：专业、简洁、详细）

**Tone (语气)**：{tone}
- 定义交流的语气（如：正式、友好、教学性）

**Audience (受众)**：{audience}
- 明确内容的目标受众

**Response (输出格式)**：{response_format}
- 明确期望的输出格式和结构
"""

# BROKE 框架 (Background, Role, Objectives, Key Results, Evolve)
BROKE_TEMPLATE = """
请按照 BROKE 框架优化 Prompt：

**Background (背景)**：
{background}

**Role (角色)**：
你是{role}

**Objectives (目标)**：
{objectives}

**Key Results (关键成果)**：
{key_results}

**Evolve (改进方向)**：
{evolve}
"""

# CRISPE 框架 (Capacity and Role, Insight, Statement, Personality, Experiment)
CRISPE_TEMPLATE = """
**Capacity and Role (能力和角色)**：
你是一位{role}，具备{capacity}的专业能力。

**Insight (洞察/背景)**：
{insight}

**Statement (任务陈述)**：
{statement}

**Personality (个性/风格)**：
请以{personality}的风格进行回复。

**Experiment (输出格式)**：
{experiment}
"""

# RASCEF 框架 (Role, Action, Steps, Context, Examples, Format)
RASCEF_TEMPLATE = """
**Role (角色)**：{role}

**Action (行动)**：{action}

**Steps (步骤)**：
{steps}

**Context (上下文)**：{context}

**Examples (示例)**：
{examples}

**Format (格式)**：{format}
"""

# 通用优化指导原则
OPTIMIZATION_PRINCIPLES = {
    "clarity": "明确性 - 使用清晰、具体的语言，避免模糊表达",
    "structure": "结构化 - 使用编号、分点等方式组织内容",
    "context": "上下文 - 提供充分的背景信息",
    "constraints": "约束条件 - 明确限制和要求",
    "examples": "示例 - 提供具体的例子或模板",
    "format": "格式规范 - 明确期望的输出格式",
    "role": "角色设定 - 让 AI 扮演专家角色",
    "thinking": "思维链 - 要求 AI 展示推理过程"
}

# 不同场景的优化策略
SCENE_STRATEGIES = {
    "通用增强": {
        "focus": ["clarity", "structure", "context"],
        "template": "CO-STAR"
    },
    "代码生成": {
        "focus": ["role", "constraints", "format", "examples"],
        "template": "RASCEF",
        "extra_requirements": [
            "代码需包含详细注释",
            "遵循语言最佳实践和代码规范",
            "包含错误处理",
            "提供使用示例"
        ]
    },
    "创意写作": {
        "focus": ["role", "context", "examples", "thinking"],
        "template": "CRISPE",
        "extra_requirements": [
            "体现创意和独特视角",
            "注重情感共鸣",
            "语言生动有趣",
            "结构完整"
        ]
    },
    "学术分析": {
        "focus": ["structure", "thinking", "constraints", "format"],
        "template": "BROKE",
        "extra_requirements": [
            "基于证据和逻辑",
            "引用权威资料",
            "保持客观中立",
            "结论明确"
        ]
    }
}

def get_template_by_name(template_name: str) -> str:
    """根据名称获取模板"""
    templates = {
        "CO-STAR": COSTAR_TEMPLATE,
        "BROKE": BROKE_TEMPLATE,
        "CRISPE": CRISPE_TEMPLATE,
        "RASCEF": RASCEF_TEMPLATE
    }
    return templates.get(template_name, COSTAR_TEMPLATE)

def get_strategy_by_scene(scene: str) -> dict:
    """根据场景获取优化策略"""
    scene_map = {
        "通用增强 (General)": "通用增强",
        "代码生成 (Coding)": "代码生成",
        "创意写作 (Creative)": "创意写作",
        "学术分析 (Academic)": "学术分析"
    }
    scene_key = scene_map.get(scene, "通用增强")
    return SCENE_STRATEGIES.get(scene_key, SCENE_STRATEGIES["通用增强"])
