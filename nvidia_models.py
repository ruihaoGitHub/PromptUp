"""
NVIDIA AI Endpoints 支持的模型列表
"""

# NVIDIA 全部可用模型（按类别分组）
NVIDIA_MODELS = {
    
    "Llama 系列": [
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.3-70b-instruct", 
        "meta/llama-3.1-8b-instruct",
        "meta/llama-3.2-3b-instruct",
        "meta/llama-3.2-1b-instruct",
    ],
    
    "DeepSeek 系列": [
        "deepseek-ai/deepseek-r1-distill-qwen-32b",
        "deepseek-ai/deepseek-r1-distill-qwen-14b",
        "deepseek-ai/deepseek-v3.2",
        "deepseek-ai/deepseek-v3.1",
    ],
    
    "Qwen 系列": [
        "qwen/qwen2.5-7b-instruct",
        "qwen/qwen2.5-coder-32b-instruct",
        "qwen/qwen3-next-80b-a3b-instruct",
        "qwen/qwen3-next-80b-a3b-thinking",
        "qwen/qwen3-coder-480b-a35b-instruct",
        "qwen/qwen3-235b-a22b",
    ],
    
}

# 展平的模型列表（用于简单选择）
ALL_NVIDIA_MODELS = []
for category, models in NVIDIA_MODELS.items():
    ALL_NVIDIA_MODELS.extend(models)

# 去重
ALL_NVIDIA_MODELS = list(dict.fromkeys(ALL_NVIDIA_MODELS))

def get_model_list(category: str = "all") -> list:
    """
    获取模型列表
    
    Args:
        category: 分类名称，如 "推荐模型"、"Llama 系列" 等，或 "all" 获取全部
    
    Returns:
        模型名称列表
    """
    if category == "all":
        return ALL_NVIDIA_MODELS
    return NVIDIA_MODELS.get(category, [])

def get_model_categories() -> list:
    """获取所有分类名称"""
    return list(NVIDIA_MODELS.keys())
