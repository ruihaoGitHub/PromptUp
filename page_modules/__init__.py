"""
页面模块
导出所有页面组件
"""
from .base_page import BasePage
from .page_manager import PageManager, page_manager
from .generation_page import GenerationPage
from .classification_page import ClassificationPage
from .summarization_page import SummarizationPage
from .translation_page import TranslationPage

__all__ = [
    'BasePage',
    'PageManager',
    'page_manager',
    'GenerationPage',
    'ClassificationPage',
    'SummarizationPage',
    'TranslationPage'
]

