"""
摘要任务页面模块
提供摘要器 Prompt 生成和优化功能
"""
import streamlit as st
from pages.base_page import BasePage


class SummarizationPage(BasePage):
    """摘要任务页面"""
    
    def render(self):
        """渲染摘要任务页面"""
        col1, col2 = self.create_two_columns()
        
        with col1:
            st.subheader("📄 摘要任务配置")
            st.info("📌 摘要任务需要明确信息提取规则，系统将设计最优的提取策略。")
            
            # 任务描述
            task_description = st.text_area(
                "任务描述",
                height=100,
                placeholder="例如：对新闻进行摘要",
                help="清晰描述摘要的目的",
                key="sum_task_desc"
            )
            
            # 源文本类型
            source_type = st.selectbox(
                "📝 源文本类型",
                [
                    "新闻报道",
                    "学术论文",
                    "会议记录",
                    "技术文档",
                    "客户反馈",
                    "产品评论",
                    "研究报告",
                    "邮件内容",
                    "其他"
                ],
                help="选择需要摘要的文本类型"
            )
            
            # 目标受众
            target_audience = st.text_input(
                "👥 目标受众",
                placeholder="例如：大学生",
                help="摘要将呈现给谁看？这会影响语言风格和详细程度"
            )
            
            # 核心关注点
            focus_points = st.text_area(
                "🎯 核心关注点",
                height=100,
                placeholder="无",
                help="摘要中必须保留哪些信息？"
            )
            
            # 篇幅限制（可选）
            with st.expander("📏 篇幅限制（可选）", expanded=False):
                length_constraint = st.selectbox(
                    "摘要长度",
                    ["不限制", "100字以内", "200字以内", "3-5个要点", "每个关注点不超过50字"],
                    help="控制摘要的篇幅"
                )
                if length_constraint == "不限制":
                    length_constraint = None
            
            # 构建摘要器按钮
            build_summarization_btn = st.button("🔨 构建摘要器 Prompt", type="primary", use_container_width=True)
        
        # 摘要任务优化逻辑
        if build_summarization_btn:
            if not self._validate_api_key():
                return
            
            # 如果用户没有输入，使用默认值
            if not task_description or task_description.strip() == "":
                task_description = "对新闻进行摘要"
                st.info("💡 未输入任务描述，使用默认示例")
            
            if not target_audience or target_audience.strip() == "":
                target_audience = "大学生"
            
            if not focus_points or focus_points.strip() == "":
                focus_points = "无"
            
            with st.spinner("🔮 正在生成提取规则、设计输出格式、构建摘要器..."):
                try:
                    # 执行摘要任务优化
                    result = self.optimizer.optimize_summarization(
                        task_description=task_description,
                        source_type=source_type,
                        target_audience=target_audience,
                        focus_points=focus_points,
                        length_constraint=length_constraint
                    )
                    
                    # 保存结果
                    st.session_state.summarization_result = result
                    
                    st.success("✅ 摘要器 Prompt 构建完成！")
                    
                except Exception as e:
                    self._handle_optimization_error(e)
        
        # 显示摘要任务优化结果
        if st.session_state.summarization_result:
            result = st.session_state.summarization_result
            
            with col2:
                st.subheader("📝 摘要器 Prompt")
                
                # 1. 优化思路
                with st.expander("🧠 查看优化思路", expanded=True):
                    st.write(result.thinking_process)
                
                # 2. 角色设定
                with st.expander("👤 角色设定", expanded=False):
                    st.info(result.role_setting)
                
                # 3. 提取规则
                with st.expander("📋 信息提取规则", expanded=True):
                    for idx, rule in enumerate(result.extraction_rules, 1):
                        st.markdown(f"**规则 {idx}:** {rule}")
                    st.caption("💡 明确的提取规则帮助模型识别关键信息")
                
                # 4. 负面约束
                with st.expander("🚫 负面约束（防止模型幻觉）", expanded=True):
                    for idx, constraint in enumerate(result.negative_constraints, 1):
                        st.markdown(f"**约束 {idx}:** {constraint}")
                    st.caption("💡 告诉模型「不要做什么」，防止添加原文没有的内容")
                
                # 5. 处理步骤
                with st.expander("🔄 思考步骤引导", expanded=False):
                    st.write(result.step_by_step_guide)
                
                # 6. 关注点
                with st.expander("🎯 核心关注领域", expanded=False):
                    for idx, area in enumerate(result.focus_areas, 1):
                        st.markdown(f"**关注点 {idx}:** {area}")
                
                # 7. 最终 Prompt
                st.markdown("**✨ 最终完整的摘要 Prompt（可直接复制）：**")
                st.caption("💡 用 {{text}} 占位符表示待摘要的文本")
                st.text_area(
                    "摘要器 Prompt",
                    value=result.final_prompt,
                    height=400,
                    label_visibility="collapsed"
                )
                
                # 直接显示代码框，带有复制按钮
                st.code(result.final_prompt, language=None)
                st.caption("📌 点击代码框右上角的复制按钮即可复制")
    
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
        st.error(f"❌ 构建失败：{error_msg}")
        
        api_provider = st.session_state.get('api_provider', 'NVIDIA')
        
        # 提供解决方案
        if "404" in error_msg or "401" in error_msg:
            st.warning("""**可能的原因和解决方案：**""")
            if api_provider == "NVIDIA":
                st.markdown("""
                1. **API Key 无效或未配置**
                   - 请访问 [NVIDIA Build](https://build.nvidia.com/) 获取 API Key
                2. **模型不支持**
                   - 推荐使用 meta/llama-3.1-405b-instruct
                """)
        
        st.info("🔧 建议：运行 `python test_nvidia.py` 测试 API 连接")
