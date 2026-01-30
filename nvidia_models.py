"""
NVIDIA AI Endpoints 支持的模型列表
"""

# NVIDIA 全部可用模型（按类别分组）
NVIDIA_MODELS = {
    "推荐模型": [
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct",
        "mistral/mistral-large-2-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "deepseek/deepseek-r1",
        "qwen/qwen2.5-72b-instruct",
    ],
    
    "Llama 系列": [
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct", 
        "meta/llama-3.1-8b-instruct",
        "meta/llama-3.3-70b-instruct",
        "meta/llama-3.2-90b-vision-instruct",
        "meta/llama-3.2-11b-vision-instruct",
        "meta/llama-3.2-3b-instruct",
        "meta/llama-3.2-1b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
    ],
    
    "DeepSeek 系列": [
        "deepseek/deepseek-r1",
        "deepseek/deepseek-r1-distill-llama-70b",
        "deepseek/deepseek-r1-distill-qwen-32b",
        "deepseek/deepseek-r1-distill-qwen-14b",
        "deepseek/deepseek-r1-distill-qwen-7b",
        "deepseek/deepseek-v3",
    ],
    
    "Qwen 系列": [
        "qwen/qwen2.5-72b-instruct",
        "qwen/qwen2.5-7b-instruct",
        "qwen/qwen2.5-coder-32b-instruct",
        "qwen/qwen3-next-80b-a3b-instruct",
        "qwen/qwen3-next-80b-a3b-thinking",
        "qwen/qwen3-coder-480b-a35b-instruct",
        "qwen/qwen3-235b-a22b",
    ],
    
    "Mistral 系列": [
        "mistral/mistral-large-2-instruct",
        "mistral/mistral-small-2-instruct",
        "mistralai/mixtral-8x7b-instruct-v0.1",
        "mistralai/mixtral-8x22b-instruct-v0.1",
        "mistral/mistral-7b-instruct-v0.3",
        "mistral/mistral-7b-instruct-v0.2",
        "mistral/codestral-mamba-7b-v0.1",
    ],
    
    "Google Gemma 系列": [
        "google/gemma-2-27b-it",
        "google/gemma-2-9b-it",
        "google/gemma-2-2b-it",
        "google/gemma-7b",
    ],
    
    "Microsoft Phi 系列": [
        "microsoft/phi-4-multimodal-instruct",
        "microsoft/phi-4-mini-instruct",
        "microsoft/phi-3.5-mini-instruct",
        "microsoft/phi-3-mini-128k-instruct",
        "microsoft/phi-3-mini-4k-instruct",
        "microsoft/phi-3-small-128k-instruct",
        "microsoft/phi-3-small-8k-instruct",
        "microsoft/phi-3-medium-4k-instruct",
    ],
    
    "其他优秀模型": [
        "nvidia/nemotron-4-mini-hindi-4b-instruct",
        "01-ai/yi-large",
        "writer/palmyra-fin-70b-32k",
        "snowflake/arctic",
        "baichuan/baichuan2-13b-chat",
        "seallms/seallm-7b-v2.5",
        "upstage/solar-pro-preview-instruct",
    ]
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
