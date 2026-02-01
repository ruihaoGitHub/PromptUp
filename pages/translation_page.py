"""
翻译任务页面模块
提供翻译器 Prompt 生成和优化功能
"""
import streamlit as st
from pages.base_page import BasePage


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
                    help="要翻译的原始文本语言"
                )
            with lang_col2:
                target_lang = st.selectbox(
                    "目标语言",
                    ["英文", "中文", "日文", "法文", "德文", "西班牙文", "韩文"],
                    index=0,
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
                help="决定译文的表达方式和语言风格"
            )
            
            # 术语表（核心功能）
            st.markdown("**📖 术语库（Glossary）- 可选**")
            st.caption("强制指定某些词的译法，确保术语一致性。每行一个，格式：原文=译文")
            glossary_input = st.text_area(
                "术语映射",
                height=120,
                placeholder="""例如（IT领域）：
Prompt Engineering=提示词工程
LLM=大语言模型
Token=令牌
Fine-tuning=微调

例如（文学作品）：
修炼=Cultivation
筑基=Foundation Establishment
金丹=Golden Core""",
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
                        
                        st.success("✅ 翻译器 Prompt 构建完成！")
                        
                    except Exception as e:
                        self._handle_optimization_error(e)
        
        # 显示翻译任务优化结果
        if st.session_state.translation_result:
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
                
                # 使用示例
                with st.expander("💡 使用示例", expanded=False):
                    st.markdown(f"""
**如何使用这个翻译 Prompt：**

1. 复制上面的完整 Prompt
2. 将 `{{{{text}}}}` 替换为你要翻译的实际文本
3. 发送给 LLM (如 GPT-4, Claude 等)

**示例：**
```
{result.final_prompt.split('{{text}}')[0]}
今天天气真好。
{result.final_prompt.split('{{text}}')[-1] if '{{text}}' in result.final_prompt else ''}
```
                    """)
    
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
