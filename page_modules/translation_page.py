"""
翻译任务页面模块
提供翻译器 Prompt 生成和优化功能
"""
import streamlit as st
import pandas as pd
import re
from .base_page import BasePage
from config.defaults import get_default_value, get_placeholder, get_default_lab_dataset


class TranslationPage(BasePage):
    """翻译任务页面"""
    
    def render(self):
        """渲染翻译任务页面"""
        col1, col2 = self.create_two_columns()
        
        with col1:
            st.subheader("🌍 翻译任务配置")
            st.info("📌 高质量翻译需要：准确的术语 + 符合文化的表达。系统将为您构建'信达雅'的翻译指令。")
            
            # 语言方向配置
            st.markdown("**🔄 翻译方向**")
            lang_col1, lang_col2 = st.columns(2)
            with lang_col1:
                source_lang = st.selectbox(
                    "源语言",
                    ["中文", "英文", "日文", "法文", "德文", "西班牙文", "韩文"],
                    index=1,
                    help="要翻译的原始文本语言"
                )
            with lang_col2:
                target_lang = st.selectbox(
                    "目标语言",
                    ["英文", "中文", "日文", "法文", "德文", "西班牙文", "韩文"],
                    index=1,
                    help="翻译后的目标语言"
                )
            
            # 任务描述
            task_description = st.text_area(
                "任务描述",
                height=80,
                placeholder=get_placeholder("translation", "task_description"),
                help="清晰描述翻译任务的要求和目标。",
                key="trans_task_desc"
            )
            
            # 领域选择
            st.markdown("**📚 应用领域**")
            domain = st.selectbox(
                "选择翻译领域",
                [
                    "通用日常",
                    "IT/技术文档",
                    "法律合同",
                    "学术论文",
                    "商务邮件",
                    "文学/小说",
                    "医学文档",
                    "新闻报道",
                    "营销文案",
                    "游戏本地化"
                ],
                index=max(
                    0,
                    [
                        "通用日常",
                        "IT/技术文档",
                        "法律合同",
                        "学术论文",
                        "商务邮件",
                        "文学/小说",
                        "医学文档",
                        "新闻报道",
                        "营销文案",
                        "游戏本地化"
                    ].index(get_default_value("translation", "domain"))
                    if get_default_value("translation", "domain") in [
                        "通用日常",
                        "IT/技术文档",
                        "法律合同",
                        "学术论文",
                        "商务邮件",
                        "文学/小说",
                        "医学文档",
                        "新闻报道",
                        "营销文案",
                        "游戏本地化"
                    ] else 0
                ),
                help="不同领域需要不同的专业术语和表达风格"
            )
            
            # 风格选择
            st.markdown("**🎨 期望风格**")
            tone = st.selectbox(
                "选择翻译风格",
                [
                    "标准/准确",
                    "地道/口语化",
                    "优美/文学性",
                    "极简/摘要式",
                    "正式/商务",
                    "轻松/活泼"
                ],
                index=max(
                    0,
                    [
                        "标准/准确",
                        "地道/口语化",
                        "优美/文学性",
                        "极简/摘要式",
                        "正式/商务",
                        "轻松/活泼"
                    ].index(get_default_value("translation", "tone"))
                    if get_default_value("translation", "tone") in [
                        "标准/准确",
                        "地道/口语化",
                        "优美/文学性",
                        "极简/摘要式",
                        "正式/商务",
                        "轻松/活泼"
                    ] else 0
                ),
                help="决定译文的表达方式和语言风格"
            )
            
            # 术语表（核心功能）
            st.markdown("**📖 术语库（Glossary）- 可选**")
            st.caption("强制指定某些词的译法，确保术语一致性。每行一个，格式：原文=译文")
            glossary_input = st.text_area(
                "术语映射",
                height=120,
                value="""Notwithstanding=尽管有任何相反约定
Force Majeure=不可抗力
Liability=责任
Indemnify=赔偿
Governing Law=适用法律
""",
                help="专有名词的强制对应关系，模型将严格遵守",
                key="trans_glossary"
            )
            
            # 构建翻译器按钮
            build_translation_btn = st.button("🔨 构建翻译器 Prompt", type="primary", use_container_width=True)
        
        # 翻译任务优化逻辑
        if build_translation_btn:
            if source_lang == target_lang:
                st.error("❌ 源语言和目标语言不能相同！")
            elif not self._validate_api_key():
                return
            else:
                # 如果用户没有输入任务描述，使用默认值
                if not task_description or task_description.strip() == "":
                    task_description = get_default_value("translation", "task_description")
                    st.info("💡 未输入任务描述，使用默认示例")
                
                # 保存用户输入的任务描述到 session_state，供随机搜索使用
                st.session_state.user_task_description_translation = task_description
                st.session_state.translation_source_lang = source_lang
                st.session_state.translation_target_lang = target_lang
                st.session_state.translation_domain = domain
                st.session_state.translation_tone = tone
                
                # 处理术语表输入，使用默认值
                if not glossary_input or glossary_input.strip() == "":
                    # 根据选择的领域提供默认术语
                    if domain == "IT/技术文档":
                        glossary_input = """Prompt Engineering=提示词工程
LLM=大语言模型
Token=令牌
Fine-tuning=微调
API=应用程序接口
Machine Learning=机器学习"""
                    elif domain == "文学/小说":
                        glossary_input = """修炼=Cultivation
筑基=Foundation Establishment
金丹=Golden Core
元婴=Nascent Soul"""
                    else:
                        glossary_input = ""  # 其他领域使用空术语表
                    
                    if glossary_input:
                        st.info(f"💡 未输入术语库，使用 {domain} 领域的默认示例")
                
                with st.spinner("🔮 正在设计领域专家角色、植入术语库、构建三步翻译法..."):
                    try:
                        # 执行翻译任务优化
                        result = self.optimizer.optimize_translation(
                            source_lang=source_lang,
                            target_lang=target_lang,
                            domain=domain,
                            tone=tone,
                            user_glossary=glossary_input
                        )
                        
                        # 保存结果
                        st.session_state.translation_result = result
                        # 保存语言选择供验证实验室使用
                        st.session_state.source_lang = source_lang
                        st.session_state.target_lang = target_lang
                        
                        st.success("✅ 翻译器 Prompt 构建完成！")
                        
                    except Exception as e:
                        self._handle_optimization_error(e)
        
        # 显示翻译任务优化结果
        if 'translation_result' in st.session_state and st.session_state.translation_result:
            result = st.session_state.translation_result
            
            with col2:
                st.subheader("🌏 翻译器 Prompt")
                
                # 1. 优化思路
                with st.expander("🧠 查看优化思路", expanded=True):
                    st.write(result.thinking_process)
                
                # 2. 角色设定
                with st.expander("👤 领域专家角色", expanded=True):
                    st.info(result.role_definition)
                    st.caption("💡 根据翻译领域设定的专业角色，确保译文专业性")
                
                # 3. 风格指南
                with st.expander("🎨 风格指南", expanded=True):
                    for idx, guideline in enumerate(result.style_guidelines, 1):
                        st.markdown(f"**指南 {idx}:** {guideline}")
                    st.caption("💡 具体的风格要求，使译文符合目标语言的表达习惯")
                
                # 4. 术语表（如果有）
                if result.glossary_section and result.glossary_section.strip():
                    with st.expander("📖 术语对照表（强制遵守）", expanded=True):
                        st.markdown(result.glossary_section)
                        st.caption("💡 专有名词的锁定翻译，确保术语一致性")
                
                # 5. 翻译流程
                with st.expander("🔄 三步翻译法", expanded=True):
                    st.markdown(result.workflow_steps)
                    st.caption("💡 分步骤的翻译流程，避免机械直译")
                
                # 6. 最终 Prompt
                st.markdown("**✨ 最终完整的翻译 Prompt（可直接复制）：**")
                st.caption("💡 用 {{text}} 占位符表示待翻译的文本")
                st.text_area(
                    "翻译器 Prompt",
                    value=result.final_prompt,
                    height=450,
                    label_visibility="collapsed"
                )
                
                # 直接显示代码框，带有复制按钮
                st.code(result.final_prompt, language=None)
                st.caption("📌 点击代码框右上角的复制按钮即可复制")
        
        # 验证实验室区域
        if 'translation_result' in st.session_state and st.session_state.translation_result:
            self._render_validation_lab(st.session_state.translation_result)
    
    def _render_validation_lab(self, result):
        """渲染翻译验证实验室"""
        st.divider()
        st.subheader("🔬 效果验证实验室")
        st.markdown("*使用测试样本验证翻译质量*")

        source_lang = st.session_state.get('source_lang', '中文')
        target_lang = st.session_state.get('target_lang', '英文')

        # 测试数据来源选择
        st.markdown("**📊 测试数据来源**")
        data_source = st.radio(
            "选择数据来源",
            ["使用默认数据", "上传CSV文件", "手动输入"],
            key="trans_data_source",
            help="选择测试数据的来源方式",
            horizontal=True
        )

        # 根据选择显示相应的输入界面
        if data_source == "上传CSV文件":
            self._render_csv_upload()
        elif data_source == "手动输入":
            self._render_manual_input()

        test_cases = self._get_test_cases(source_lang, target_lang)
        
        col_test1, col_test2 = st.columns([1, 1])
        
        with col_test1:
            st.markdown(f"**📄 测试样本（{source_lang}原文 / {target_lang}参考译文）**")
            st.caption("修改下方的测试文本和参考译文：")

            for i, case in enumerate(test_cases):
                with st.container():
                    st.markdown(f"**测试 {i+1}:**")
                    text = st.text_area(
                        f"原文 {i+1}",
                        value=case["text"],
                        height=120,
                        key=f"trans_test_text_{i}"
                    )
                    expected = st.text_area(
                        f"参考译文 {i+1}",
                        value=case["expected"],
                        height=100,
                        key=f"trans_test_expected_{i}"
                    )
                    test_cases[i] = {"text": text, "expected": expected}
        
        with col_test2:
            st.markdown("**🎯 评分标准**")
            st.info("""
**BLEU Score（翻译任务）**

**BLEU 指标说明**：
- 计算方式：n-gram 精确度的几何平均
- 衡量译文与参考译文的相似度

**评分标准**：
- 🟢 **优秀** ≥ 40%
- 🟡 **良好** 20% - 40%
- 🔴 **需改进** < 20%

📌 **注意**：BLEU 分数只是参考，请结合人工评估
            """)
        
        # 运行验证按钮
        if st.button("🚀 执行翻译", type="primary", use_container_width=True, key="trans_validation_btn"):
            valid_cases = [c for c in test_cases if c["text"].strip() and c["expected"].strip()]
            if not valid_cases:
                st.error("❌ 请至少提供一条完整的测试样本（原文与参考译文）")
            else:
                with st.spinner(f"⏳ 正在从{source_lang}翻译到{target_lang}..."):
                    try:
                        from metrics import MetricsCalculator
                        calc = MetricsCalculator()
                        lang = "zh" if target_lang == "中文" else "en"

                        results = []
                        for case in valid_cases:
                            prompt_with_text = result.final_prompt
                            prompt_with_text = re.sub(r"\{\{\s*text\s*\}\}", case["text"], prompt_with_text)
                            prompt_with_text = re.sub(r"\{\{\{\s*text\s*\}\}\}", case["text"], prompt_with_text)
                            prompt_with_text = re.sub(r"\{\s*text\s*\}", case["text"], prompt_with_text)
                            prompt_with_text = prompt_with_text.replace("[待翻译文本]", case["text"])
                            prompt_with_text = prompt_with_text.replace("【待翻译文本】", case["text"])
                            prompt_with_text = prompt_with_text.replace("<text>", case["text"])

                            strict_prefix = f"【输出要求】只输出{target_lang}译文，不要解释、不要原文、不要双语对照。\n"
                            prompt_with_text = strict_prefix + prompt_with_text

                            response = self.optimizer.llm.invoke(prompt_with_text)
                            translation = response.content.strip()

                            bleu_score = calc.calculate_bleu(translation, case["expected"], lang=lang)

                            results.append({
                                "original": case["text"],
                                "translation": translation,
                                "reference": case["expected"],
                                "bleu_score": bleu_score,
                                "source_lang": source_lang,
                                "target_lang": target_lang
                            })

                        st.session_state.trans_validation_results = results
                        st.session_state.trans_avg_bleu = sum(r["bleu_score"] for r in results) / len(results)

                    except Exception as e:
                        st.error(f"❌ 翻译失败：{str(e)}")
        
        # 显示验证结果
        if 'trans_validation_results' in st.session_state and st.session_state.trans_validation_results:
            results = st.session_state.trans_validation_results
            avg_bleu = st.session_state.get('trans_avg_bleu', 0)

            st.divider()
            st.markdown("### 📊 翻译结果")

            if avg_bleu >= 40:
                st.success(f"🎉 平均 BLEU 分数：{avg_bleu:.2f}% - 🟢 优秀！")
            elif avg_bleu >= 20:
                st.info(f"👍 平均 BLEU 分数：{avg_bleu:.2f}% - 🟡 良好")
            else:
                st.warning(f"⚠️ 平均 BLEU 分数：{avg_bleu:.2f}% - 🔴 需改进")

            for i, r in enumerate(results, 1):
                with st.expander(f"测试 {i} 结果", expanded=(i == 1)):
                    col_result1, col_result2, col_result3 = st.columns(3)

                    with col_result1:
                        st.markdown(f"**📄 {r['source_lang']}原文**")
                        st.text_area(
                            f"原文_{i}",
                            value=r["original"],
                            height=200,
                            label_visibility="collapsed",
                            disabled=True
                        )

                    with col_result2:
                        st.markdown(f"**✨ AI翻译的{r['target_lang']}译文**")
                        st.text_area(
                            f"AI译文_{i}",
                            value=r["translation"],
                            height=200,
                            label_visibility="collapsed"
                        )

                    with col_result3:
                        st.markdown(f"**📌 参考{r['target_lang']}译文**")
                        st.text_area(
                            f"参考译文_{i}",
                            value=r["reference"],
                            height=200,
                            label_visibility="collapsed",
                            disabled=True
                        )

                    st.metric("该样本 BLEU", f"{r['bleu_score']:.2f}%")

            st.markdown("**💡 人工评估建议**")
            st.caption("BLEU 分数是自动化指标，建议结合人工评估判断翻译质量（准确性、流畅性、术语一致性）")

    def _render_csv_upload(self):
        """渲染CSV文件上传界面"""
        st.markdown("**📁 CSV文件上传**")
        st.info("CSV文件应包含两列：'text'（原文）和 'expected'（参考译文）")

        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=["csv"],
            key="trans_csv_upload",
            help="上传包含翻译测试数据的CSV文件"
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

                st.session_state.trans_custom_test_data = df.to_dict('records')

            except Exception as e:
                st.error(f"❌ 文件读取失败：{str(e)}")

    def _render_manual_input(self):
        """渲染手动输入界面"""
        st.markdown("**✏️ 手动输入测试数据**")

        manual_data = st.session_state.get('trans_manual_test_data', [
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
                    key=f"trans_manual_text_{i}",
                    height=100,
                    placeholder="输入待翻译原文"
                )
            with col2:
                expected = st.text_area(
                    f"参考译文 {i+1}",
                    value=item["expected"],
                    key=f"trans_manual_expected_{i}",
                    height=100,
                    placeholder="输入参考译文"
                )
            with col3:
                if st.button("🗑️", key=f"trans_delete_{i}", help=f"删除第{i+1}行"):
                    continue

            if text.strip() or expected.strip():
                updated_data.append({"text": text, "expected": expected})

        if st.button("➕ 添加一行", key="trans_add_manual_row"):
            updated_data.append({"text": "", "expected": ""})

        st.session_state.trans_manual_test_data = updated_data

        valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
        st.info(f"当前有 {valid_count} 条有效测试数据")

    def _get_test_cases(self, source_lang: str, target_lang: str):
        """获取测试数据，根据用户选择返回相应数据"""
        data_source = st.session_state.get('trans_data_source', '使用默认数据')

        default_cases = get_default_lab_dataset("translation")
        filtered_default = [
            {"text": c["text"], "expected": c["expected"]}
            for c in default_cases
            if c.get("source_lang") == source_lang and c.get("target_lang") == target_lang
        ]
        default_result = filtered_default if filtered_default else [
            {"text": c["text"], "expected": c["expected"]} for c in default_cases
        ]

        if data_source == "使用默认数据":
            if 'trans_custom_test_data' in st.session_state:
                del st.session_state.trans_custom_test_data
            if 'trans_manual_test_data' in st.session_state:
                del st.session_state.trans_manual_test_data
            return default_result

        elif data_source == "上传CSV文件":
            if 'trans_custom_test_data' in st.session_state and st.session_state.trans_custom_test_data:
                return st.session_state.trans_custom_test_data
            else:
                return default_result

        elif data_source == "手动输入":
            if 'trans_manual_test_data' in st.session_state:
                manual_data = [item for item in st.session_state.trans_manual_test_data
                              if item["text"].strip() and item["expected"].strip()]
                if manual_data:
                    return manual_data
            return default_result

        return default_result
    
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
