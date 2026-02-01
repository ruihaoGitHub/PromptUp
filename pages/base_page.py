"""
页面基类
定义所有页面的通用接口和辅助方法
"""
import streamlit as st
from typing import Optional
from optimizer import PromptOptimizer


class BasePage:
    """页面基类"""
    
    def __init__(self, optimizer: PromptOptimizer):
        """
        初始化页面
        
        Args:
            optimizer: PromptOptimizer 实例
        """
        self.optimizer = optimizer
    
    def render(self):
        """
        渲染页面内容（由子类实现）
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    @staticmethod
    def show_thinking_process(thinking: str):
        """显示思考过程"""
        with st.expander("💭 AI 思考过程", expanded=False):
            st.markdown(thinking)
    
    @staticmethod
    def show_techniques(techniques: list[str]):
        """显示使用的技术"""
        st.markdown("**🔧 使用的优化技术：**")
        for tech in techniques:
            st.markdown(
                f'<span class="technique-badge">{tech}</span>',
                unsafe_allow_html=True
            )
    
    @staticmethod
    def show_keywords(keywords: list[str]):
        """显示新增关键词"""
        if keywords:
            st.markdown("**🔑 新增关键词：**")
            for kw in keywords:
                st.markdown(
                    f'<span class="keyword-badge">{kw}</span>',
                    unsafe_allow_html=True
                )
    
    @staticmethod
    def show_error(error: str):
        """显示错误信息"""
        st.error(f"❌ {error}")
    
    @staticmethod
    def show_success(message: str):
        """显示成功信息"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def show_warning(message: str):
        """显示警告信息"""
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def create_two_columns():
        """创建两列布局"""
        return st.columns(2)
    
    @staticmethod
    def create_tabs(labels: list[str]):
        """创建标签页"""
        return st.tabs(labels)
