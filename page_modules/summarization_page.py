"""
摘要任务页面模块
提供摘要器 Prompt 生成和优化功能
"""
import streamlit as st
from .base_page import BasePage


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
                placeholder="例如：对产品发布新闻进行摘要",
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
                help="选择需要摘要的文本类型",
                index=0
            )
            
            # 目标受众
            target_audience = st.text_input(
                "👥 目标受众",
                placeholder="例如：高校师生与媒体读者",
                help="摘要将呈现给谁看？这会影响语言风格和详细程度"
            )
            
            # 核心关注点
            focus_points = st.text_area(
                "🎯 核心关注点",
                height=100,
                placeholder="产品功能、关键数据、发布节奏、行业影响",
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
        if 'summarization_result' in st.session_state and st.session_state.summarization_result:
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
        
        # 验证实验室区域
        if 'summarization_result' in st.session_state and st.session_state.summarization_result:
            self._render_validation_lab(st.session_state.summarization_result)
    
    def _render_validation_lab(self, result):
        """渲染摘要验证实验室"""
        st.divider()
        st.subheader("🔬 效果验证实验室")
        st.markdown("*使用示例文本测试摘要质量*")
        
        # 默认测试文本
        default_text = """近日，某科技公司发布了其最新研发的人工智能助手产品。该产品基于大语言模型技术，能够进行自然语言对话、文本生成、代码编写等多种任务。
        
公司CEO在发布会上表示，这款产品经过了18个月的研发，训练数据量达到了10TB，参数规模超过千亿。产品的主要特点包括：更强的上下文理解能力、更准确的多轮对话、以及更好的专业领域知识。

该产品将首先面向企业客户开放API接口，个人用户版本预计在三个月后推出。定价策略采用按使用量计费的模式，预计每1000次调用收费0.5美元。

业内专家认为，这款产品的发布标志着人工智能技术在商业应用领域的又一次重要突破，预计将对内容创作、客户服务、教育培训等多个行业产生深远影响。"""
        # 默认测试文本
        default_text = """【产品发布快讯】某公司今日发布“NovaWrite AI 写作助手”，面向教育与内容创作场景。产品支持中文长文写作、资料改写与多轮对话。

    官方披露：本次模型训练数据规模约 8TB，推理延迟平均降低 35%，支持 8k 上下文。首批功能包含：大纲生成、风格迁移、数据要点提炼。

    商业化策略：企业版 4 月上线，按调用计费，起步价 0.4 美元/千次；个人版预计 6 月开放。公司将与 20 所高校合作试点。

    行业观点认为，该产品有望提升内容生产效率，并推动教育与媒体行业的 AI 落地。"""
        
        col_test1, col_test2 = st.columns([1, 1])
        
        with col_test1:
            st.markdown("**📄 测试文本（原文）**")
            test_text = st.text_area(
                "输入要摘要的文本",
                value=default_text,
                height=200,
                key="sum_test_text"
            )
            
            st.markdown("**📌 参考摘要（用于计算ROUGE分数）**")
            reference_summary = st.text_area(
                "输入人工撰写的参考摘要",
                value="某公司发布 NovaWrite AI 写作助手，面向教育与内容创作，支持长文写作、改写与多轮对话。模型训练数据约 8TB，推理延迟降低 35%，支持 8k 上下文，提供大纲生成、风格迁移、要点提炼等功能。企业版 4 月上线按调用计费（0.4 美元/千次），个人版预计 6 月开放，并与 20 所高校试点。业内认为将提升内容效率并推动教育、媒体落地。",
                height=100,
                key="sum_reference"
            )
        
        with col_test2:
            st.markdown("**🎯 评分标准**")
            st.info("""
**ROUGE Score（摘要任务）**

**ROUGE 指标说明**：
- **ROUGE-1**：单词重叠率
- **ROUGE-2**：双词组重叠率
- **ROUGE-L**：最长公共子序列

**评分标准**：
- 🟢 **优秀** ≥ 50%
- 🟡 **良好** 30% - 50%
- 🔴 **需改进** < 30%
            """)
        
        # 运行验证按钮
        if st.button("🚀 生成摘要", type="primary", use_container_width=True, key="sum_validation_btn"):
            if not test_text or test_text.strip() == "":
                st.error("❌ 请输入要摘要的文本")
            elif not reference_summary or reference_summary.strip() == "":
                st.error("❌ 请输入参考摘要，用于计算ROUGE分数")
            else:
                with st.spinner("⏳ 正在生成摘要..."):
                    try:
                        # 替换占位符
                        prompt_with_text = result.final_prompt.replace("{{text}}", test_text)
                        prompt_with_text = prompt_with_text.replace("{text}", test_text)
                        prompt_with_text = prompt_with_text.replace("[待摘要文本]", test_text)
                        
                        # 调用 LLM
                        response = self.optimizer.llm.invoke(prompt_with_text)
                        summary = response.content.strip()
                        
                        # 计算 ROUGE 分数
                        from metrics import MetricsCalculator
                        calc = MetricsCalculator()
                        rouge_scores = calc.calculate_rouge(summary, reference_summary, lang="zh")
                        
                        # 保存结果
                        st.session_state.sum_validation_result = {
                            "original": test_text,
                            "summary": summary,
                            "reference": reference_summary,
                            "rouge_scores": rouge_scores,
                            "compression_ratio": len(summary) / len(test_text) * 100
                        }
                        
                    except Exception as e:
                        st.error(f"❌ 生成摘要失败：{str(e)}")
        
        # 显示验证结果
        if 'sum_validation_result' in st.session_state and st.session_state.sum_validation_result:
            result_data = st.session_state.sum_validation_result
            
            st.divider()
            st.markdown("### 📊 摘要结果")
            
            # 显示ROUGE分数和评级
            rouge_scores = result_data["rouge_scores"]
            avg_rouge = (rouge_scores['rouge1'] + rouge_scores['rouge2'] + rouge_scores['rougeL']) / 3
            
            # 根据平均ROUGE分数显示评级
            if avg_rouge >= 50:
                st.success(f"🎉 平均 ROUGE 分数：{avg_rouge:.2f}% - 🟢 优秀！")
            elif avg_rouge >= 30:
                st.info(f"👍 平均 ROUGE 分数：{avg_rouge:.2f}% - 🟡 良好")
            else:
                st.warning(f"⚠️ 平均 ROUGE 分数：{avg_rouge:.2f}% - 🔴 需改进")
            
            # 详细ROUGE分数
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("ROUGE-1", f"{rouge_scores['rouge1']:.2f}%", help="单词重叠率")
            with col_r2:
                st.metric("ROUGE-2", f"{rouge_scores['rouge2']:.2f}%", help="双词组重叠率")
            with col_r3:
                st.metric("ROUGE-L", f"{rouge_scores['rougeL']:.2f}%", help="最长公共子序列")
            
            st.divider()
            
            col_result1, col_result2, col_result3 = st.columns([1, 1, 1])
            
            with col_result1:
                st.markdown("**📄 原文**")
                st.text_area(
                    "原文",
                    value=result_data["original"],
                    height=150,
                    label_visibility="collapsed",
                    disabled=True
                )
            
            with col_result2:
                st.markdown("**✨ AI生成的摘要**")
                st.text_area(
                    "AI摘要",
                    value=result_data["summary"],
                    height=150,
                    label_visibility="collapsed"
                )
            
            with col_result3:
                st.markdown("**📌 参考摘要**")
                st.text_area(
                    "参考摘要",
                    value=result_data["reference"],
                    height=150,
                    label_visibility="collapsed",
                    disabled=True
                )
            
            # 统计信息
            st.markdown("**📈 统计信息**")
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("原文字数", len(result_data["original"]))
            with stat_col2:
                st.metric("摘要字数", len(result_data["summary"]))
            with stat_col3:
                st.metric("压缩率", f"{result_data['compression_ratio']:.1f}%")
            
            st.markdown("**💡 人工评估建议**")
            st.caption("ROUGE 分数是自动化指标，建议结合人工评估判断摘要质量（完整性、准确性、简洁性、可读性）")
    
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
