"""
生成任务页面模块
提供通用 Prompt 生成和优化功能
"""
import streamlit as st
import sys
import os
# 将项目根目录（PromptUp）添加到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .base_page import BasePage
from config.defaults import get_default_value, get_placeholder
from contribution_analysis import render_contribution_analysis


class GenerationPage(BasePage):
    """通用 Prompt 生成任务页面"""
    
    def render(self):
        """渲染生成任务页面"""
        col1, col2 = self.create_two_columns()
        
        with col1:
            st.subheader("📝 原始输入")
            
            # 用户输入区域
            user_input = st.text_area(
                "输入您的简单 Prompt",
                height=150,
                placeholder=get_placeholder("generation", "user_input"),
                help="描述您想做什么，可以很简单。",
                key="gen_user_input"
            )
            
            optimization_mode = st.selectbox(
                "🎯 优化模式",
                [
                    "通用增强 (General)",
                    "代码生成 (Coding)",
                    "创意写作 (Creative)",
                    "学术分析 (Academic)"
                ],
                index=max(
                    0,
                    [
                        "通用增强 (General)",
                        "代码生成 (Coding)",
                        "创意写作 (Creative)",
                        "学术分析 (Academic)"
                    ].index(get_default_value("generation", "optimization_mode"))
                    if get_default_value("generation", "optimization_mode") in [
                        "通用增强 (General)",
                        "代码生成 (Coding)",
                        "创意写作 (Creative)",
                        "学术分析 (Academic)"
                    ] else 0
                ),
                help="根据任务类型选择合适的优化策略。代码生成侧重步骤化和示例；创意写作强调个性化；学术分析注重逻辑性。",
                key="gen_optimization_mode"
            )
            
            scene_input = st.text_input(
                "场景/补充描述（可选）",
                placeholder=get_placeholder("generation", "scene_input"),
                help="提供更多背景信息，如编程语言、目标受众等。",
                key="gen_scene_input"
            )
            
            # 优化按钮
            start_btn = st.button("✨ 开始魔法优化", type="primary", use_container_width=True)
        
        # 生成任务优化逻辑
        if start_btn:
            # 验证输入
            if not self._validate_api_key():
                return
            
            # 如果用户没有输入，使用默认值
            if not user_input or user_input.strip() == "":
                user_input = get_default_value("generation", "user_input")
                st.info("💡 未输入内容，使用默认示例：" + user_input)
            
            if not scene_input or scene_input.strip() == "":
                scene_input = get_default_value("generation", "scene_input")
            
            # 保存原始prompt到session_state以便A/B对比测试使用
            st.session_state.original_user_input = user_input
            st.session_state.original_scene_input = scene_input
            
            with st.spinner("🔮 正在分析语义、提取关键词、构建结构化模板..."):
                try:
                    # 执行优化
                    result = self.optimizer.optimize(
                        user_prompt=user_input,
                        scene_desc=scene_input,
                        optimization_mode=optimization_mode
                    )
                    
                    # 保存结果到 session state
                    st.session_state.result = result
                    st.session_state.comparison_done = False
                    st.session_state.comparison_results = None
                    
                    st.success("✅ 优化完成！")
                    
                except Exception as e:
                    self._handle_optimization_error(e)
        
        # 生成任务结果展示区域
        if 'result' in st.session_state and st.session_state.result:
            result = st.session_state.result
            
            with col2:
                st.subheader("🌟 优化结果")

                # 优化思路展示
                self.show_thinking_process(result)

                # 原始 Prompt 和优化后 Prompt 对比展示
                st.markdown("### 📊 Prompt 对比")

                compare_col1, compare_col2 = st.columns(2)

                with compare_col1:
                    st.markdown("**📄 原始 Prompt**")
                    original_prompt = st.session_state.get('original_user_input', '未保存')
                    st.text_area(
                        "原始输入",
                        value=original_prompt,
                        height=150,
                        label_visibility="collapsed",
                        disabled=True
                    )

                with compare_col2:
                    st.markdown("**✨ 优化后的 Prompt**")
                    st.text_area(
                        "优化结果",
                        value=result.improved_prompt,
                        height=150,
                        label_visibility="collapsed"
                    )

                # 新增：关键词贡献度分析（和原功能并列展示）
                st.markdown("---")  # 加分割线，区分两个模块，更美观
                st.markdown("**🔆 关键词贡献度分析**")
                if hasattr(result, 'improved_prompt') and result.improved_prompt:
                    render_contribution_analysis(result.improved_prompt)
                else:
                    st.warning("未找到可分析的 Prompt 数据")

                # 完整的优化后 Prompt 代码框
                st.markdown("**📋 完整优化后的 Prompt（可直接复制）：**")
                st.code(result.improved_prompt, language=None)
                st.caption("📌 点击代码框右上角的复制按钮即可复制")
        
        # A/B 对比测试区域
        if 'result' in st.session_state and st.session_state.result:
            self._render_ab_test(st.session_state.result)
    
    def _validate_api_key(self):
        """验证 API Key"""
        api_key = st.session_state.get('api_key_input', '')
        if not api_key or api_key.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
            return False
        return True
    
    def _handle_optimization_error(self, e):
        """处理优化错误"""
        error_msg = str(e)
        st.error(f"❌ 优化失败：{error_msg}")
        
        # 根据错误类型提供具体的解决方案
        api_provider = st.session_state.get('api_provider', 'NVIDIA')
        
        if "404" in error_msg or "401" in error_msg:
            st.warning("""**可能的原因和解决方案：**""")
            if api_provider == "NVIDIA":
                st.markdown("""
                1. **API Key 无效或未配置**
                   - 请访问 [NVIDIA Build](https://build.nvidia.com/) 获取 API Key
                   - 确保 API Key 格式正确（以 `nvapi-` 开头）
                   - 在侧边栏输入有效的 API Key
                
                2. **模型名称不正确**
                   - 请从下拉列表中选择模型
                   - 不要手动输入模型名称
                
                3. **网络问题**
                   - NVIDIA API 可能需要科学上网
                   - 检查网络连接是否正常
                """)
            else:
                st.markdown("""
                1. **API Key 无效**
                   - 请访问 [OpenAI Platform](https://platform.openai.com/) 检查 API Key
                   - 确保账户有足够余额
                
                2. **Base URL 配置错误**
                   - 如果使用代理，请检查 Base URL 是否正确
                """)
        elif "rate_limit" in error_msg.lower():
            st.info("💡 API 请求频率超限，请等待几秒后重试")
        else:
            st.info("💡 提示：请检查网络连接和 API 配置")
        
        # 提供测试连接的建议
        st.info("🔧 建议：运行 `python test_nvidia.py` 测试 API 连接")
    
    def _render_ab_test(self, result):
        """渲染 A/B 对比测试区域"""
        st.divider()
        st.subheader("🔬 A/B 效果对比测试")
        st.markdown("*让 AI 分别使用原始 Prompt 和优化后的 Prompt 执行任务，直观对比优化效果*")
        
        col_test1, col_test2, col_test3 = st.columns([2, 1, 2])
        
        with col_test2:
            if st.button("🚀 运行对比测试", type="primary", use_container_width=True, key="ab_test_btn"):
                # 检查是否有保存的原始prompt
                if 'original_user_input' not in st.session_state or not st.session_state.original_user_input:
                    st.error("❌ 未找到原始 Prompt，请先运行一次优化。")
                else:
                    with st.spinner("⏳ 正在运行两个版本的 Prompt，请稍候..."):
                        try:
                            # 使用保存的原始prompt
                            res_orig, res_opt = self.optimizer.compare_results(
                                original_prompt=st.session_state.original_user_input,
                                optimized_prompt=result.improved_prompt
                            )
                            
                            st.session_state.comparison_results = (res_orig, res_opt)
                            st.session_state.comparison_done = True
                            
                        except Exception as e:
                            st.error(f"❌ 对比测试失败：{str(e)}")
        
        # 显示对比结果
        if st.session_state.comparison_done and st.session_state.comparison_results:
            res_orig, res_opt = st.session_state.comparison_results
            
            col_result1, col_result2 = st.columns(2)
            
            with col_result1:
                st.markdown("#### 📄 原始 Prompt 产出")
                st.info(res_orig)
                
            with col_result2:
                st.markdown("#### ✨ 优化后 Prompt 产出")
                st.success(res_opt)
