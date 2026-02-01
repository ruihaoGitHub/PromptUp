"""
翻译任务页面模块
提供翻译器 Prompt 生成和优化功能
"""
import streamlit as st
import re
from .base_page import BasePage


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
                index=2,
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
                index=4,
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
        st.markdown("*使用示例文本测试翻译质量*")
        
        # 默认测试文本（根据语言方向）
        source_lang = st.session_state.get('source_lang', '中文')
        target_lang = st.session_state.get('target_lang', '英文')
        
        if source_lang == "英文" and target_lang == "中文":
            default_text = """Notwithstanding any provision to the contrary, neither party shall be liable for any delay in performance or failure to perform this Agreement where such delay or failure is due to a Force Majeure event; provided that the affected party shall notify the other party in writing within five (5) business days and use reasonable efforts to mitigate losses."""
            default_reference = """尽管有任何相反约定，若因不可抗力事件导致履行延迟或未能履行本协议，任何一方均不承担责任；但受影响方应在五（5）个工作日内以书面形式通知对方，并尽合理努力减轻损失。"""
        elif source_lang == "中文" and target_lang == "英文":
            default_text = """尽管有任何相反约定，若因不可抗力事件导致履行延迟或未能履行本协议，任何一方均不承担责任；但受影响方应在五（5）个工作日内以书面形式通知对方，并尽合理努力减轻损失。"""
            default_reference = """Notwithstanding any provision to the contrary, neither party shall be liable for any delay in performance or failure to perform this Agreement where such delay or failure is due to a Force Majeure event; provided that the affected party shall notify the other party in writing within five (5) business days and use reasonable efforts to mitigate losses."""
        else:
            default_text = """The company announced a $120 million funding round led by Horizon Capital, valuing the startup at $1.8 billion. The funds will be used to expand its data centers in Asia."""
            default_reference = """该公司宣布由 Horizon Capital 领投的 1.2 亿美元融资轮，使这家初创公司估值达到 18 亿美元。资金将用于扩大其在亚洲的数据中心。"""
        
        col_test1, col_test2 = st.columns([1, 1])
        
        with col_test1:
            st.markdown(f"**📄 {source_lang}原文**")
            test_text = st.text_area(
                "输入要翻译的文本",
                value=default_text,
                height=150,
                key="trans_test_text"
            )
            
            st.markdown(f"**📌 参考译文（用于计算BLEU分数）**")
            reference_translation = st.text_area(
                "输入人工翻译的参考译文",
                value=default_reference,
                height=100,
                key="trans_reference"
            )
        
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
            if not test_text or test_text.strip() == "":
                st.error("❌ 请输入要翻译的文本")
            elif not reference_translation or reference_translation.strip() == "":
                st.error("❌ 请输入参考译文，用于计算BLEU分数")
            else:
                with st.spinner(f"⏳ 正在从{source_lang}翻译到{target_lang}..."):
                    try:
                        # 替换占位符
                        prompt_with_text = result.final_prompt
                        prompt_with_text = re.sub(r"\{\{\s*text\s*\}\}", test_text, prompt_with_text)
                        prompt_with_text = re.sub(r"\{\{\{\s*text\s*\}\}\}", test_text, prompt_with_text)
                        prompt_with_text = re.sub(r"\{\s*text\s*\}", test_text, prompt_with_text)
                        prompt_with_text = prompt_with_text.replace("[待翻译文本]", test_text)
                        prompt_with_text = prompt_with_text.replace("【待翻译文本】", test_text)
                        prompt_with_text = prompt_with_text.replace("<text>", test_text)
                        
                        # 强制输出仅包含目标语言译文
                        strict_prefix = f"【输出要求】只输出{target_lang}译文，不要解释、不要原文、不要双语对照。\n"
                        prompt_with_text = strict_prefix + prompt_with_text
                        
                        # 调用 LLM
                        response = self.optimizer.llm.invoke(prompt_with_text)
                        translation = response.content.strip()
                        
                        # 计算 BLEU 分数
                        from metrics import MetricsCalculator
                        calc = MetricsCalculator()
                        # 根据目标语言选择分词方式
                        lang = "zh" if target_lang == "中文" else "en"
                        bleu_score = calc.calculate_bleu(translation, reference_translation, lang=lang)
                        
                        # 保存结果
                        st.session_state.trans_validation_result = {
                            "original": test_text,
                            "translation": translation,
                            "reference": reference_translation,
                            "bleu_score": bleu_score,
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        }
                        
                    except Exception as e:
                        st.error(f"❌ 翻译失败：{str(e)}")
        
        # 显示验证结果
        if 'trans_validation_result' in st.session_state and st.session_state.trans_validation_result:
            result_data = st.session_state.trans_validation_result
            
            st.divider()
            st.markdown("### 📊 翻译结果")
            
            # 显示BLEU分数和评级
            bleu_score = result_data["bleu_score"]
            
            # 根据BLEU分数显示评级
            if bleu_score >= 40:
                st.success(f"🎉 BLEU 分数：{bleu_score:.2f}% - 🟢 优秀！")
            elif bleu_score >= 20:
                st.info(f"👍 BLEU 分数：{bleu_score:.2f}% - 🟡 良好")
            else:
                st.warning(f"⚠️ BLEU 分数：{bleu_score:.2f}% - 🔴 需改进")
            
            st.divider()
            
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                st.markdown(f"**📄 {result_data['source_lang']}原文**")
                st.text_area(
                    "原文",
                    value=result_data["original"],
                    height=200,
                    label_visibility="collapsed",
                    disabled=True
                )
            
            with col_result2:
                st.markdown(f"**✨ AI翻译的{result_data['target_lang']}译文**")
                st.text_area(
                    "AI译文",
                    value=result_data["translation"],
                    height=200,
                    label_visibility="collapsed"
                )
            
            with col_result3:
                st.markdown(f"**📌 参考{result_data['target_lang']}译文**")
                st.text_area(
                    "参考译文",
                    value=result_data["reference"],
                    height=200,
                    label_visibility="collapsed",
                    disabled=True
                )
            
            st.markdown("**💡 人工评估建议**")
            st.caption("BLEU 分数是自动化指标，建议结合人工评估判断翻译质量（准确性、流畅性、术语一致性）")
    
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
