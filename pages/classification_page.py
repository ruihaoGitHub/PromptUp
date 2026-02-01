"""
分类任务页面模块
提供分类器 Prompt 生成和优化功能
"""
import streamlit as st
from pages.base_page import BasePage


class ClassificationPage(BasePage):
    """分类任务页面"""
    
    def render(self):
        """渲染分类任务页面"""
        col1, col2 = self.create_two_columns()
        
        with col1:
            st.subheader("🏷️ 分类任务配置")
            st.info("📌 分类任务需要明确的标签定义和示例，系统将自动生成这些要素。")
            
            # 任务描述
            task_description = st.text_area(
                "任务描述",
                height=100,
                placeholder="例如：判断用户评论的情感倾向",
                help="清晰描述这是一个什么样的分类任务。",
                key="cls_task_desc"
            )
            
            # 标签输入
            labels_input = st.text_input(
                "目标标签（用逗号分隔）",
                placeholder="例如：积极, 消极, 中立",
                help="输入所有可能的分类标签，用逗号分隔（中文逗号、英文逗号均可）。",
                key="cls_labels"
            )
            
            # 构建分类器按钮
            build_btn = st.button("🔨 构建分类器 Prompt", type="primary", use_container_width=True)
        
        # 分类任务优化逻辑
        if build_btn:
            if not self._validate_api_key():
                return
            
            # 如果用户没有输入，使用默认值
            if not task_description or task_description.strip() == "":
                task_description = "对电商产品评论进行情感分类，识别用户的满意度和态度"
                st.info("💡 未输入任务描述，使用默认示例")
            
            if not labels_input or labels_input.strip() == "":
                labels_input = "积极, 消极, 中立"
                st.info("💡 未输入标签，使用默认标签：" + labels_input)
            
            # 解析标签（支持中文逗号和英文逗号）
            labels_input_normalized = labels_input.replace("，", ",")
            labels_list = [label.strip() for label in labels_input_normalized.split(",") if label.strip()]
            
            if len(labels_list) < 2:
                st.error("❌ 至少需要 2 个标签")
            else:
                with st.spinner("🔮 正在构建分类器..."):
                    try:
                        # 执行分类任务优化
                        result = self.optimizer.optimize_classification(
                            task_description=task_description,
                            labels=labels_list
                        )
                        
                        # 保存结果
                        st.session_state.classification_result = result
                        
                        st.success("✅ 分类器 Prompt 构建完成！")
                        
                    except Exception as e:
                        self._handle_optimization_error(e)
        
        # 显示分类任务优化结果
        if st.session_state.classification_result:
            result = st.session_state.classification_result
            
            with col2:
                st.subheader("🎯 分类器 Prompt")
                
                # 1. 优化思路
                with st.expander("🧠 查看优化思路", expanded=True):
                    st.write(result.thinking_process)
                
                # 2. 角色定义
                with st.expander("👤 角色设定", expanded=False):
                    st.info(result.role_definition)
                
                # 3. 最终 Prompt
                st.markdown("**✨ 最终完整的分类 Prompt（可直接复制）：**")
                st.text_area(
                    "分类器 Prompt",
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
