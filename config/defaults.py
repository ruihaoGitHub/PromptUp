"""
默认参数配置文件
统一管理所有任务的默认参数，避免在多个地方写死
"""

# 分类任务默认参数
CLASSIFICATION_DEFAULTS = {
    "task_description": {
        "placeholder": "例如：判断用户评论的情感倾向",
        "default_value": "对电商产品评论进行情感分类，识别用户的满意度和态度"
    },
    "labels": {
        "placeholder": "例如：积极, 消极, 中立",
        "default_value": "积极, 消极, 中立"
    }
}

# 摘要任务默认参数
SUMMARIZATION_DEFAULTS = {
    "task_description": {
        "placeholder": "例如：对产品发布新闻进行摘要",
        "default_value": "对新闻/会议纪要进行摘要（保留关键数字与结论）"
    },
    "source_type": {
        "placeholder": "例如：新闻报道",
        "default_value": "新闻报道"
    },
    "target_audience": {
        "placeholder": "例如：高校师生与媒体读者",
        "default_value": "高校师生与媒体读者"
    },
    "focus_points": {
        "placeholder": "产品功能、关键数据、发布节奏、行业影响",
        "default_value": "无"
    }
}

# 翻译任务默认参数
TRANSLATION_DEFAULTS = {
    "task_description": {
        "placeholder": "例如：将英文新闻与法律条款翻译为中文，保持正式、准确、结构对齐",
        "default_value": "将英文新闻与法律条款翻译为中文，保持正式、准确、结构对齐"
    },
    "domain": {
        "default_value": "法律合同"
    },
    "tone": {
        "default_value": "正式/商务"
    }
}

# 生成任务默认参数
GENERATION_DEFAULTS = {
    "user_input": {
        "placeholder": "例如：推荐一下索尼降噪耳机",
        "default_value": "推荐一下索尼降噪耳机"
    },
    "scene_input": {
        "placeholder": "例如：发在小红书上，目标是学生党，突出性价比和降噪，语气要活泼",
        "default_value": "发在小红书上，目标是学生党，突出性价比和降噪，语气要活泼"
    },
    "optimization_mode": {
        "default_value": "通用增强 (General)"
    }
}

# 分类任务默认测试数据集
CLASSIFICATION_DEFAULT_DATASET = [
    {"input": "这家餐厅服务很好，口味也棒！", "ground_truth": "积极"},
    {"input": "物流太慢了，包装也破了。", "ground_truth": "消极"},
    {"input": "体验一般，没有特别惊喜。", "ground_truth": "中立"},
    {"input": "客服很耐心，问题解决得很快。", "ground_truth": "积极"},
    {"input": "产品质量很差，用了几天就坏了。", "ground_truth": "消极"},
    {"input": "功能基本能用，但界面设计一般。", "ground_truth": "中立"},
    {"input": "价格合理，性价比很高。", "ground_truth": "积极"},
    {"input": "售后态度冷淡，问题迟迟不解决。", "ground_truth": "消极"},
    {"input": "外观不错但使用体验一般。", "ground_truth": "中立"},
    {"input": "包装精美，送货及时，购物体验很好。", "ground_truth": "积极"}
]

# 摘要任务默认测试数据集
SUMMARIZATION_DEFAULT_DATASET = [
    {
        "input": """【产品发布快讯】某公司发布“NovaWrite AI 写作助手”，面向教育与内容创作场景，支持中文长文写作与多轮对话。
官方披露：训练数据约 8TB，推理延迟降低 35%，支持 8k 上下文。功能包含大纲生成与要点提炼。
商业化策略：企业版 4 月上线按调用计费（0.4 美元/千次），个人版 6 月开放并与高校试点。""",
        "ground_truth": "某公司发布 NovaWrite AI 写作助手，训练数据约 8TB、推理延迟降 35%、支持 8k 上下文。企业版 4 月上线按调用计费（0.4 美元/千次），个人版 6 月开放并与高校试点。"
    },
    {
        "input": """产品评审会上确定三项重点：搜索性能优化（响应时间降低30%）、上线新的A/B测试平台、完善日志链路以便事故复盘。
行动计划：张明负责搜索优化方案设计（2周内提交）；李华负责A/B平台需求梳理（下周完成PRD）；王琳负责日志权限与归档策略（本周五前）。""",
        "ground_truth": "会议确定三项重点：搜索性能优化、上线A/B测试平台、完善日志链路。行动计划：张明2周内提交方案，李华下周完成PRD，王琳本周五前出日志权限与归档方案。"
    },
    {
        "input": """央行宣布降准0.25个百分点，释放约5000亿元资金以支持实体经济。央行表示经济面临下行压力，需要加大支持力度。
分析人士认为此举可降低融资成本、刺激投资消费，但需警惕通胀风险。""",
        "ground_truth": "央行降准0.25个百分点释放约5000亿元资金支持实体经济，旨在降低融资成本并刺激需求，但需警惕通胀风险。"
    },
    {
        "input": """2026年2月某省发布新能源汽车推广方案：计划年内新增公共充电桩2万个，覆盖80%地级市核心区域。
同时提出对购置新能源物流车的企业给予最高10万元补贴。专家认为该政策将提升绿色物流渗透率。""",
        "ground_truth": "某省发布新能源汽车推广方案，年内新增公共充电桩2万个覆盖80%地级市核心区域，并对购置新能源物流车企业最高补贴10万元，预计提升绿色物流渗透率。"
    },
    {
        "input": """公司季度经营会上通报：Q1营收同比增长18%，毛利率提升2.1个百分点。下一步目标：优化供应链成本、上线自助工单系统、将客户响应时长缩短至2小时内。""",
        "ground_truth": "公司Q1营收同比增长18%、毛利率提升2.1个百分点；下一步将优化供应链成本、上线自助工单系统并将响应时长缩短至2小时内。"
    }
]

# 翻译任务默认测试数据集
TRANSLATION_DEFAULT_DATASET = [
    {
        "input": """Notwithstanding any provision to the contrary, neither party shall be liable for any delay in performance or failure to perform this Agreement where such delay or failure is due to a Force Majeure event; provided that the affected party shall notify the other party in writing within five (5) business days and use reasonable efforts to mitigate losses.""",
        "ground_truth": "尽管有任何相反约定，若因不可抗力事件导致履行延迟或未能履行本协议，任何一方均不承担责任；但受影响方应在五（5）个工作日内以书面形式通知对方，并尽合理努力减轻损失。"
    },
    {
        "input": """Any dispute arising out of or in connection with this Agreement shall be submitted to arbitration in Shanghai, and the arbitral award shall be final and binding upon both parties.""",
        "ground_truth": "凡因本协议产生或与本协议有关的任何争议，均应提交上海仲裁，仲裁裁决为终局并对双方具有约束力。"
    },
    {
        "input": """The company announced a $120 million funding round led by Horizon Capital, valuing the startup at $1.8 billion. The funds will be used to expand its data centers in Asia.""",
        "ground_truth": "该公司宣布由 Horizon Capital 领投的 1.2 亿美元融资轮，使这家初创公司估值达到 18 亿美元。资金将用于扩大其在亚洲的数据中心。"
    },
    {
        "input": """The quarterly earnings report exceeded analyst expectations, with revenue growing 15% year-over-year. The company's stock price surged 8% following the announcement.""",
        "ground_truth": "季度财报超出分析师预期，营收同比增长15%。公司股价在公告后上涨8%。"
    },
    {
        "input": """The new software update includes enhanced security features and improved user interface. Users will notice faster loading times and more intuitive navigation, making the application more efficient and user-friendly.""",
        "ground_truth": "新软件更新包括增强的安全功能和改进的用户界面。用户将注意到更快的加载时间和更直观的导航，使应用程序更加高效和用户友好。"
    }
]

# 分类任务效果实验室默认测试样本
CLASSIFICATION_LAB_DEFAULT_DATASET = [
    {"text": "这个产品真的很棒，质量超出预期！", "expected": "积极"},
    {"text": "太失望了，完全不值这个价格", "expected": "消极"},
    {"text": "还可以吧，没有特别的感觉", "expected": "中立"},
    {"text": "客服回复很及时，体验不错", "expected": "积极"},
    {"text": "包装破损，体验很差", "expected": "消极"}
]

# 摘要任务效果实验室默认测试样本
SUMMARIZATION_LAB_DEFAULT_DATASET = [
    {
        "text": "【产品发布快讯】某公司今日发布“NovaWrite AI 写作助手”，面向教育与内容创作场景。产品支持中文长文写作、资料改写与多轮对话。\n官方披露：本次模型训练数据规模约 8TB，推理延迟平均降低 35%，支持 8k 上下文。首批功能包含：大纲生成、风格迁移、数据要点提炼。\n商业化策略：企业版 4 月上线，按调用计费，起步价 0.4 美元/千次；个人版预计 6 月开放。公司将与 20 所高校合作试点。\n行业观点认为，该产品有望提升内容生产效率，并推动教育与媒体行业的 AI 落地。",
        "expected": "某公司发布 NovaWrite AI 写作助手，面向教育与内容创作，支持长文写作与多轮对话。模型训练数据约 8TB、推理延迟降低 35%、支持 8k 上下文，提供大纲生成与要点提炼。企业版 4 月上线按调用计费（0.4 美元/千次），个人版 6 月开放并与高校试点。"
    },
    {
        "text": "产品评审会上，团队确认了下季度三项重点：1）完成搜索性能优化，目标是将平均响应时间降低30%；2）上线新的A/B测试平台，优先支持推荐系统实验；3）完善日志链路，确保事故复盘可追溯。\n行动计划：张明负责搜索优化方案设计，2周内提交；李华负责A/B平台需求梳理，下周完成PRD；王琳负责日志系统权限与归档策略，本周五前出方案。",
        "expected": "会议确定三项重点：搜索性能优化（响应时间降30%）、上线A/B测试平台、完善日志链路。行动计划：张明2周内提交方案，李华下周完成PRD，王琳本周五前出日志权限与归档方案。"
    },
    {
        "text": "央行今日宣布降准0.25个百分点，将释放约5000亿元资金支持实体经济。央行表示，当前经济面临一定下行压力，需要通过货币政策工具加大支持力度。分析人士认为，此举有助于降低企业融资成本，刺激投资和消费需求，但也需警惕通胀风险。",
        "expected": "央行降准0.25个百分点释放约5000亿元资金以支持实体经济、降低融资成本并刺激需求，但需警惕通胀风险。"
    },
    {
        "text": "2026年2月，某市发布教育数字化行动计划：年内新建智慧教室200间，覆盖60%公立中学。计划同步上线在线作业平台，并开展教师数字化能力培训。",
        "expected": "某市发布教育数字化行动计划：年内新建200间智慧教室覆盖60%公立中学，并上线在线作业平台和教师数字化能力培训。"
    },
    {
        "text": "公司季度总结会上通报：Q1营收同比增长18%，毛利率提升2.1个百分点。下一步目标是优化供应链成本、上线自助工单系统、将客户响应时长缩短至2小时内。",
        "expected": "公司Q1营收同比增长18%、毛利率提升2.1个百分点；将优化供应链成本、上线自助工单系统并把响应时长缩短至2小时内。"
    }
]

# 翻译任务效果实验室默认测试样本
TRANSLATION_LAB_DEFAULT_DATASET = [
    {
        "text": "Notwithstanding any provision to the contrary, neither party shall be liable for any delay in performance or failure to perform this Agreement where such delay or failure is due to a Force Majeure event; provided that the affected party shall notify the other party in writing within five (5) business days and use reasonable efforts to mitigate losses.",
        "expected": "尽管有任何相反约定，若因不可抗力事件导致履行延迟或未能履行本协议，任何一方均不承担责任；但受影响方应在五（5）个工作日内以书面形式通知对方，并尽合理努力减轻损失。",
        "source_lang": "英文",
        "target_lang": "中文"
    },
    {
        "text": "Any dispute arising out of or in connection with this Agreement shall be submitted to arbitration in Shanghai, and the arbitral award shall be final and binding upon both parties.",
        "expected": "凡因本协议产生或与本协议有关的任何争议，均应提交上海仲裁，仲裁裁决为终局并对双方具有约束力。",
        "source_lang": "英文",
        "target_lang": "中文"
    },
    {
        "text": "The company announced a $120 million funding round led by Horizon Capital, valuing the startup at $1.8 billion. The funds will be used to expand its data centers in Asia.",
        "expected": "该公司宣布由 Horizon Capital 领投的 1.2 亿美元融资轮，使这家初创公司估值达到 18 亿美元。资金将用于扩大其在亚洲的数据中心。",
        "source_lang": "英文",
        "target_lang": "中文"
    },
    {
        "text": "The quarterly earnings report exceeded analyst expectations, with revenue growing 15% year-over-year. The company's stock price surged 8% following the announcement.",
        "expected": "季度财报超出分析师预期，营收同比增长15%。公司股价在公告后上涨8%。",
        "source_lang": "英文",
        "target_lang": "中文"
    },
    {
        "text": "The new software update includes enhanced security features and improved user interface. Users will notice faster loading times and more intuitive navigation, making the application more efficient and user-friendly.",
        "expected": "新软件更新包括增强的安全功能和改进的用户界面。用户将注意到更快的加载时间和更直观的导航，使应用程序更加高效和用户友好。",
        "source_lang": "英文",
        "target_lang": "中文"
    }
]

# 所有任务的默认参数映射
TASK_DEFAULTS = {
    "generation": GENERATION_DEFAULTS,
    "classification": CLASSIFICATION_DEFAULTS,
    "summarization": SUMMARIZATION_DEFAULTS,
    "translation": TRANSLATION_DEFAULTS
}

def get_task_defaults(task_type: str):
    """
    获取指定任务类型的默认参数

    Args:
        task_type: 任务类型 ('classification', 'summarization', 'translation')

    Returns:
        dict: 该任务类型的默认参数字典
    """
    return TASK_DEFAULTS.get(task_type, {})

def get_default_value(task_type: str, param_name: str):
    """
    获取指定任务类型和参数名称的默认值

    Args:
        task_type: 任务类型 ('classification', 'summarization', 'translation')
        param_name: 参数名称

    Returns:
        str: 默认值，如果不存在返回空字符串
    """
    task_defaults = get_task_defaults(task_type)
    param_config = task_defaults.get(param_name, {})
    return param_config.get("default_value", "")

def get_default_dataset(task_type: str):
    """
    获取指定任务类型的默认测试数据集

    Args:
        task_type: 任务类型 ('classification', 'summarization', 'translation')

    Returns:
        list: 默认测试数据集，格式为 [{'input': '...', 'ground_truth': '...'}]
    """
    if task_type == "classification":
        return CLASSIFICATION_DEFAULT_DATASET.copy()
    elif task_type == "summarization":
        return SUMMARIZATION_DEFAULT_DATASET.copy()
    elif task_type == "translation":
        return TRANSLATION_DEFAULT_DATASET.copy()
    else:
        return []

def get_placeholder(task_type: str, param_name: str):
    """
    获取指定任务类型和参数名称的占位符文本

    Args:
        task_type: 任务类型 ('classification', 'summarization', 'translation')
        param_name: 参数名称

    Returns:
        str: 占位符文本，如果不存在返回空字符串
    """
    task_defaults = get_task_defaults(task_type)
    param_config = task_defaults.get(param_name, {})
    return param_config.get("placeholder", "")

def get_default_lab_dataset(task_type: str):
    """
    获取指定任务类型的效果实验室默认测试数据集

    Args:
        task_type: 任务类型 ('classification', 'summarization', 'translation')

    Returns:
        list: 默认实验室测试数据集，格式为 [{'text': '...', 'expected': '...'}]
    """
    if task_type == "classification":
        return CLASSIFICATION_LAB_DEFAULT_DATASET.copy()
    if task_type == "summarization":
        return SUMMARIZATION_LAB_DEFAULT_DATASET.copy()
    if task_type == "translation":
        return TRANSLATION_LAB_DEFAULT_DATASET.copy()
    return []