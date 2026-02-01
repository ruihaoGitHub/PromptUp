"""
页面管理器
负责页面路由和渲染
"""
import streamlit as st
from typing import Dict, Type
from .base_page import BasePage


class PageManager:
    """页面管理器"""
    
    def __init__(self):
        """初始化页面管理器"""
        self.pages: Dict[str, Type[BasePage]] = {}
        self.current_page: str = ""
    
    def register_page(self, name: str, page_class: Type[BasePage]):
        """
        注册页面
        
        Args:
            name: 页面名称
            page_class: 页面类
        """
        self.pages[name] = page_class
    
    def render_page(self, name: str, optimizer):
        """
        渲染指定页面
        
        Args:
            name: 页面名称
            optimizer: PromptOptimizer 实例
        """
        if name not in self.pages:
            st.error(f"页面 '{name}' 不存在")
            return
        
        self.current_page = name
        page_instance = self.pages[name](optimizer)
        page_instance.render()
    
    def get_page_names(self) -> list[str]:
        """获取所有已注册的页面名称"""
        return list(self.pages.keys())


# 全局页面管理器实例
page_manager = PageManager()
