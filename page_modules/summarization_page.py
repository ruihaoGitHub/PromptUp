"""
摘要任务页面模块
提供摘要器 Prompt 生成和优化功能
"""
import streamlit as st
import pandas as pd
from .base_page import BasePage
from config.defaults import get_default_value, get_placeholder, get_default_lab_dataset


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
                placeholder=get_placeholder("summarization", "task_description"),
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
                index=max(
                    0,
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
                    ].index(get_default_value("summarization", "source_type"))
                    if get_default_value("summarization", "source_type") in [
                        "新闻报道",
                        "学术论文",
                        "会议记录",
                        "技术文档",
                        "客户反馈",
                        "产品评论",
                        "研究报告",
                        "邮件内容",
                        "其他"
                    ] else 0
                )
            )
            
            # 目标受众
            target_audience = st.text_input(
                "👥 目标受众",
                placeholder=get_placeholder("summarization", "target_audience"),
                help="摘要将呈现给谁看？这会影响语言风格和详细程度"
            )
            
            # 核心关注点
            focus_points = st.text_area(
                "🎯 核心关注点",
                height=100,
                placeholder=get_placeholder("summarization", "focus_points"),
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
                task_description = get_default_value("summarization", "task_description")
                st.info("💡 未输入任务描述，使用默认示例")
            
            if not target_audience or target_audience.strip() == "":
                target_audience = get_default_value("summarization", "target_audience")
            
            if not focus_points or focus_points.strip() == "":
                focus_points = get_default_value("summarization", "focus_points")
            
            # 保存用户输入的任务描述到 session_state，供随机搜索使用
            st.session_state.user_task_description_summarization = task_description
            st.session_state.summarization_source_type = source_type
            st.session_state.summarization_target_audience = target_audience
            st.session_state.summarization_focus_points = focus_points
            
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
        st.markdown("*使用测试样本验证摘要质量*")

        # 测试数据来源选择
        st.markdown("**📊 测试数据来源**")
        data_source = st.radio(
            "选择数据来源",
            ["使用默认数据", "上传CSV文件", "手动输入"],
            key="sum_data_source",
            help="选择测试数据的来源方式",
            horizontal=True
        )

        # 根据选择显示相应的输入界面
        if data_source == "上传CSV文件":
            self._render_csv_upload()
        elif data_source == "手动输入":
            self._render_manual_input()

        # 获取测试数据
        test_cases = self._get_test_cases()
        
        col_test1, col_test2 = st.columns([1, 1])
        
        with col_test1:
            st.markdown("**📄 测试样本（原文 / 参考摘要）**")
            st.caption("修改下方的测试文本和参考摘要：")

            for i, case in enumerate(test_cases):
                with st.container():
                    st.markdown(f"**测试 {i+1}:**")
                    text = st.text_area(
                        f"原文 {i+1}",
                        value=case["text"],
                        height=120,
                        key=f"sum_test_text_{i}"
                    )
                    expected = st.text_area(
                        f"参考摘要 {i+1}",
                        value=case["expected"],
                        height=100,
                        key=f"sum_test_expected_{i}"
                    )
                    test_cases[i] = {"text": text, "expected": expected}
        
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
            valid_cases = [c for c in test_cases if c["text"].strip() and c["expected"].strip()]
            if not valid_cases:
                st.error("❌ 请至少提供一条完整的测试样本（原文与参考摘要）")
            else:
                with st.spinner("⏳ 正在生成摘要..."):
                    try:
                        from metrics import MetricsCalculator
                        calc = MetricsCalculator()

                        results = []
                        for case in valid_cases:
                            prompt_with_text = result.final_prompt.replace("{{text}}", case["text"])
                            prompt_with_text = prompt_with_text.replace("{text}", case["text"])
                            prompt_with_text = prompt_with_text.replace("[待摘要文本]", case["text"])

                            response = self.optimizer.llm.invoke(prompt_with_text)
                            summary = response.content.strip()

                            rouge_scores = calc.calculate_rouge(summary, case["expected"], lang="zh")

                            results.append({
                                "original": case["text"],
                                "summary": summary,
                                "reference": case["expected"],
                                "rouge_scores": rouge_scores,
                                "compression_ratio": len(summary) / len(case["text"]) * 100
                            })

                        st.session_state.sum_validation_results = results

                        avg_rouge1 = sum(r["rouge_scores"]["rouge1"] for r in results) / len(results)
                        avg_rouge2 = sum(r["rouge_scores"]["rouge2"] for r in results) / len(results)
                        avg_rougeL = sum(r["rouge_scores"]["rougeL"] for r in results) / len(results)
                        st.session_state.sum_avg_rouge = {
                            "rouge1": avg_rouge1,
                            "rouge2": avg_rouge2,
                            "rougeL": avg_rougeL
                        }

                    except Exception as e:
                        st.error(f"❌ 生成摘要失败：{str(e)}")
        
        # 显示验证结果
        if 'sum_validation_results' in st.session_state and st.session_state.sum_validation_results:
            results = st.session_state.sum_validation_results
            avg_scores = st.session_state.get('sum_avg_rouge', {"rouge1": 0, "rouge2": 0, "rougeL": 0})

            st.divider()
            st.markdown("### 📊 摘要结果")

            avg_rouge = (avg_scores['rouge1'] + avg_scores['rouge2'] + avg_scores['rougeL']) / 3

            if avg_rouge >= 50:
                st.success(f"🎉 平均 ROUGE 分数：{avg_rouge:.2f}% - 🟢 优秀！")
            elif avg_rouge >= 30:
                st.info(f"👍 平均 ROUGE 分数：{avg_rouge:.2f}% - 🟡 良好")
            else:
                st.warning(f"⚠️ 平均 ROUGE 分数：{avg_rouge:.2f}% - 🔴 需改进")

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("ROUGE-1", f"{avg_scores['rouge1']:.2f}%", help="单词重叠率")
            with col_r2:
                st.metric("ROUGE-2", f"{avg_scores['rouge2']:.2f}%", help="双词组重叠率")
            with col_r3:
                st.metric("ROUGE-L", f"{avg_scores['rougeL']:.2f}%", help="最长公共子序列")

            for i, r in enumerate(results, 1):
                with st.expander(f"测试 {i} 结果", expanded=(i == 1)):
                    col_result1, col_result2, col_result3 = st.columns([1, 1, 1])

                    with col_result1:
                        st.markdown("**📄 原文**")
                        st.text_area(
                            f"原文_{i}",
                            value=r["original"],
                            height=150,
                            label_visibility="collapsed",
                            disabled=True
                        )

                    with col_result2:
                        st.markdown("**✨ AI生成的摘要**")
                        st.text_area(
                            f"AI摘要_{i}",
                            value=r["summary"],
                            height=150,
                            label_visibility="collapsed"
                        )

                    with col_result3:
                        st.markdown("**📌 参考摘要**")
                        st.text_area(
                            f"参考摘要_{i}",
                            value=r["reference"],
                            height=150,
                            label_visibility="collapsed",
                            disabled=True
                        )

                    st.markdown("**📈 统计信息**")
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    with stat_col1:
                        st.metric("原文字数", len(r["original"]))
                    with stat_col2:
                        st.metric("摘要字数", len(r["summary"]))
                    with stat_col3:
                        st.metric("压缩率", f"{r['compression_ratio']:.1f}%")
                    with stat_col4:
                        r_avg = (r["rouge_scores"]["rouge1"] + r["rouge_scores"]["rouge2"] + r["rouge_scores"]["rougeL"]) / 3
                        st.metric("该样本ROUGE均值", f"{r_avg:.2f}%")

            st.markdown("**💡 人工评估建议**")
            st.caption("ROUGE 分数是自动化指标，建议结合人工评估判断摘要质量（完整性、准确性、简洁性、可读性）")

    def _render_csv_upload(self):
        """渲染CSV文件上传界面"""
        st.markdown("**📁 CSV文件上传**")
        st.info("CSV文件应包含两列：'text'（原文）和 'expected'（参考摘要）")

        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=["csv"],
            key="sum_csv_upload",
            help="上传包含摘要测试数据的CSV文件"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                required_columns = ["text", "expected"]
                if not all(col in df.columns for col in required_columns):
                    st.error(f"❌ CSV文件必须包含以下列：{', '.join(required_columns)}")
                    return

                st.success(f"✅ 成功加载 {len(df)} 条测试数据")
                st.markdown("**数据预览：**")
                st.dataframe(df.head(), use_container_width=True)

                st.session_state.sum_custom_test_data = df.to_dict('records')

            except Exception as e:
                st.error(f"❌ 文件读取失败：{str(e)}")

    def _render_manual_input(self):
        """渲染手动输入界面"""
        st.markdown("**✏️ 手动输入测试数据**")

        manual_data = st.session_state.get('sum_manual_test_data', [
            {"text": "", "expected": ""},
            {"text": "", "expected": ""},
            {"text": "", "expected": ""}
        ])

        st.markdown("添加测试样本：")

        updated_data = []
        for i, item in enumerate(manual_data):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                text = st.text_area(
                    f"原文 {i+1}",
                    value=item["text"],
                    key=f"sum_manual_text_{i}",
                    height=100,
                    placeholder="输入待摘要原文"
                )
            with col2:
                expected = st.text_area(
                    f"参考摘要 {i+1}",
                    value=item["expected"],
                    key=f"sum_manual_expected_{i}",
                    height=100,
                    placeholder="输入参考摘要"
                )
            with col3:
                if st.button("🗑️", key=f"sum_delete_{i}", help=f"删除第{i+1}行"):
                    continue

            if text.strip() or expected.strip():
                updated_data.append({"text": text, "expected": expected})

        if st.button("➕ 添加一行", key="sum_add_manual_row"):
            updated_data.append({"text": "", "expected": ""})

        st.session_state.sum_manual_test_data = updated_data

        valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
        st.info(f"当前有 {valid_count} 条有效测试数据")

    def _get_test_cases(self):
        """获取测试数据，根据用户选择返回相应数据"""
        data_source = st.session_state.get('sum_data_source', '使用默认数据')

        if data_source == "使用默认数据":
            if 'sum_custom_test_data' in st.session_state:
                del st.session_state.sum_custom_test_data
            if 'sum_manual_test_data' in st.session_state:
                del st.session_state.sum_manual_test_data
            return get_default_lab_dataset("summarization")

        elif data_source == "上传CSV文件":
            if 'sum_custom_test_data' in st.session_state and st.session_state.sum_custom_test_data:
                return st.session_state.sum_custom_test_data
            else:
                return get_default_lab_dataset("summarization")

        elif data_source == "手动输入":
            if 'sum_manual_test_data' in st.session_state:
                manual_data = [item for item in st.session_state.sum_manual_test_data
                              if item["text"].strip() and item["expected"].strip()]
                if manual_data:
                    return manual_data
            return get_default_lab_dataset("summarization")

        return get_default_lab_dataset("summarization")
    
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
