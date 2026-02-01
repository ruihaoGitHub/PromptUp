"""
配置模块
包含数据模型定义和Meta-Prompt模板加载
"""
from .models import (
    OptimizedPrompt,
    ClassificationPrompt,
    SummarizationPrompt,
    TranslationPrompt,
    SearchSpace,
    SearchResult
)

from .template_loader import (
    load_meta_prompt,
    get_generation_meta_prompt,
    get_classification_meta_prompt,
    get_summarization_meta_prompt,
    get_translation_meta_prompt,
    get_search_space_meta_prompt
)

__all__ = [
    'OptimizedPrompt',
    'ClassificationPrompt',
    'SummarizationPrompt',
    'TranslationPrompt',
    'SearchSpace',
    'SearchResult',
    'load_meta_prompt',
    'get_generation_meta_prompt',
    'get_classification_meta_prompt',
    'get_summarization_meta_prompt',
    'get_translation_meta_prompt',
    'get_search_space_meta_prompt'
]
