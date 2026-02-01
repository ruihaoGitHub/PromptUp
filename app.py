"""
AI Prompt 自动优化系统 - Streamlit 主界面
重构后的精简版本，使用页面模块和 UI 组件系统
"""
import streamlit as st
from dotenv import load_dotenv
from optimizer import PromptOptimizer
from pages import (
    GenerationPage,
    ClassificationPage, 
    SummarizationPage,
    TranslationPage
)
from ui import apply_custom_styles, render_sidebar

# 加载环境变量
load_dotenv()

# 应用自定义样式（包含页面配置）
apply_custom_styles()

# 标题区域
st.markdown('<p class="main-header">🚀 AI Prompt 自动优化大师</p>', unsafe_allow_html=True)

# 渲染侧边栏并获取配置
config = render_sidebar()
task_type = config['task_type']
api_provider = config['api_provider']
api_key_input = config['api_key']
base_url = config['base_url']
model_choice = config['model']

# 根据任务类型显示不同的副标题
if task_type == "生成任务":
    st.markdown('<p class="sub-header">输入简单的想法，系统将自动利用 <b>结构化模板、语义扩展、关键词增强</b> 技术为您生成专家级 Prompt</p>', unsafe_allow_html=True)
elif task_type == "分类任务":
    st.markdown('<p class="sub-header">系统将为您设计专业的分类器 Prompt，自动生成 <b>标签定义、Few-shot 示例</b> 和最佳分类策略</p>', unsafe_allow_html=True)
elif task_type == "摘要任务":
    st.markdown('<p class="sub-header">系统将为您设计智能的摘要器 Prompt，自动优化 <b>信息提取规则、压缩策略</b> 和输出格式</p>', unsafe_allow_html=True)
elif task_type == "翻译任务":
    st.markdown('<p class="sub-header">系统将为您构建专业的翻译器 Prompt，整合 <b>术语表、风格指南</b> 和领域知识库</p>', unsafe_allow_html=True)

# 创建优化器实例（所有页面共享）
if api_key_input and api_key_input.strip():
    optimizer = PromptOptimizer(
        api_key=api_key_input,
        model=model_choice,
        base_url=base_url if base_url else None,
        provider=api_provider.lower()
    )
    
    # 将配置保存到 session_state，供页面模块使用
    st.session_state.api_key_input = api_key_input
    st.session_state.api_provider = api_provider
    st.session_state.model_choice = model_choice
    st.session_state.base_url = base_url
else:
    optimizer = None

# 根据任务类型渲染对应的页面
if not optimizer:
    # 如果没有配置 API Key，显示提示
    st.warning("⚠️ 请先在左侧边栏配置 API Key")
elif task_type == "生成任务":
    generation_page = GenerationPage(optimizer)
    generation_page.render()
elif task_type == "分类任务":
    classification_page = ClassificationPage(optimizer)
    classification_page.render()
elif task_type == "摘要任务":
    summarization_page = SummarizationPage(optimizer)
    summarization_page.render()
elif task_type == "翻译任务":
    translation_page = TranslationPage(optimizer)
    translation_page.render()
