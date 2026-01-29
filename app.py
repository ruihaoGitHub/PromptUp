"""
AI Prompt 自动优化系统 - Streamlit 界面
"""
import streamlit as st
import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer, OptimizedPrompt, ClassificationPrompt, SummarizationPrompt, TranslationPrompt
from nvidia_models import get_model_list
from metrics import MetricsCalculator

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI Prompt 自动优化大师",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .technique-badge {
        display: inline-block;
        background-color: #e0e7ff;
        color: #4c51bf;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .keyword-badge {
        display: inline-block;
        background-color: #fef3c7;
        color: #d97706;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 标题区域
st.markdown('<p class="main-header">🚀 AI Prompt 自动优化大师</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">输入简单的想法，系统将自动利用 <b>结构化模板、语义扩展、关键词增强</b> 技术为您生成专家级 Prompt</p>', unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 任务类型选择（新增）
    task_type = st.radio(
        "📋 任务类型",
        ["生成任务", "分类任务", "摘要任务", "翻译任务"],
        help="选择要优化的 Prompt 类型"
    )
    
    st.divider()
    
    # API 提供商选择
    api_provider = st.selectbox(
        "🔌 API 提供商",
        ["NVIDIA", "OpenAI"],
        index=0,
        help="选择使用的 API 服务提供商"
    )
    
    st.divider()
    
    # 根据提供商显示不同的配置
    if api_provider == "NVIDIA":
        st.markdown("✨ **NVIDIA API 配置**")
        
        # 只在环境变量真有有效值时才使用
        env_key = os.getenv("NVIDIA_API_KEY", "")
        default_value = env_key if env_key and env_key.startswith("nvapi-") and len(env_key) > 10 else ""
        
        api_key_input = st.text_input(
            "NVIDIA API Key",
            type="password",
            value=default_value,
            help="从 NVIDIA AI Endpoints 获取 API Key"
        )
        
        # API Key 验证提示
        if api_key_input:
            if not api_key_input.startswith("nvapi-"):
                st.warning("⚠️ NVIDIA API Key 应该以 'nvapi-' 开头")
            else:
                st.success("✅ API Key 格式正确")
        else:
            st.error("🔑 请输入 NVIDIA API Key")
            st.info("💡 **获取免费 API Key**：[NVIDIA Build](https://build.nvidia.com/) → 登录 → 选择模型 → Get API Key")
        
        base_url = st.text_input(
            "NVIDIA Base URL",
            value=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            help="NVIDIA API 端点"
        )
        
        # NVIDIA 模型选择（使用完整模型列表）
        nvidia_models = get_model_list("推荐模型")
        
        model_choice = st.selectbox(
            "选择模型",
            nvidia_models,
            index=0,
            help="推荐使用 Llama 3.1 405B 或 Mistral Large 以获得最佳优化效果"
        )
        
        # 高级选项：显示所有模型
        with st.expander("🔧 查看所有可用模型", expanded=False):
            all_models = get_model_list("all")
            st.info(f"共有 {len(all_models)} 个可用模型")
            model_choice_advanced = st.selectbox(
                "从全部模型中选择",
                all_models,
                key="advanced_model"
            )
            if st.button("使用此模型"):
                model_choice = model_choice_advanced
                st.success(f"已切换到：{model_choice}")

        
    else:  # OpenAI
        st.markdown("✨ **OpenAI API 配置**")
        
        # 只在环境变量真有有效值时才使用
        env_key = os.getenv("OPENAI_API_KEY", "")
        default_value = env_key if env_key and env_key.startswith("sk-") and len(env_key) > 10 else ""
        
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=default_value,
            help="从 OpenAI 官网获取 API Key"
        )
        
        # API Key 验证提示
        if api_key_input:
            if not api_key_input.startswith("sk-"):
                st.warning("⚠️ OpenAI API Key 应该以 'sk-' 开头")
            else:
                st.success("✅ API Key 格式正确")
        else:
            st.error("🔑 请输入 OpenAI API Key")
            st.info("💡 **获取 API Key**：[OpenAI Platform](https://platform.openai.com/) → API Keys")
        
        base_url = st.text_input(
            "API Base URL (可选)",
            value=os.getenv("OPENAI_BASE_URL", ""),
            help="如使用代理或第三方服务，请填写完整的 base URL"
        )
        
        model_choice = st.selectbox(
            "选择模型",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
            help="推荐使用 GPT-4o 以获得最佳优化效果"
        )
    
    # 优化模式（仅生成任务显示）
    if task_type == "生成任务":
        optimization_mode = st.selectbox(
            "🎯 优化模式",
            [
                "通用增强 (General)",
                "代码生成 (Coding)",
                "创意写作 (Creative)",
                "学术分析 (Academic)"
            ],
            help="根据任务类型选择合适的优化策略"
        )
    
    st.divider()
    
    # 使用说明
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
        **快速上手**：
        1. 在左侧输入您的 API Key
        2. 在主界面输入简单的 Prompt
        3. （可选）添加场景描述
        4. 点击"开始魔法优化"
        
        **优化模式说明**：
        - **通用增强**：适用于各类日常任务
        - **代码生成**：专门优化编程相关任务
        - **创意写作**：文案、故事、营销内容
        - **学术分析**：研究、论文、数据分析
        
        **核心技术**：
        - 🔍 语义扩展：补充隐含需求
        - 🎯 关键词增强：加入专业术语
        - 📐 模板应用：CO-STAR/BROKE 框架
        """)
    
    # 示例 Prompt
    with st.expander("💡 示例 Prompt", expanded=False):
        st.markdown("""
        **代码类**：
        - "写个贪吃蛇游戏"
        - "帮我实现一个登录系统"
        
        **文案类**：
        - "写个产品介绍"
        - "创作一个品牌故事"
        
        **分析类**：
        - "分析市场趋势"
        - "总结论文要点"
        """)

# 初始化 session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'comparison_done' not in st.session_state:
    st.session_state.comparison_done = False
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = None
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None
if 'summarization_result' not in st.session_state:
    st.session_state.summarization_result = None
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None

# 主界面布局
col1, col2 = st.columns([1, 1])

# ========== 根据任务类型显示不同界面 ==========
if task_type == "生成任务":
    with col1:
        st.subheader("📝 原始输入")
        
        # 用户输入区域
        user_input = st.text_area(
            "输入您的简单 Prompt",
            height=150,
            placeholder="例如：帮我写个贪吃蛇游戏",
            help="描述您想做什么，可以很简单"
        )
        
        scene_input = st.text_input(
            "场景/补充描述（可选）",
            placeholder="例如：Python, 给小孩学编程用",
            help="提供更多背景信息，如编程语言、目标受众等"
        )
        
        # 优化按钮
        start_btn = st.button("✨ 开始魔法优化", type="primary", use_container_width=True)

    # 生成任务优化逻辑
    if start_btn:
        if not user_input or user_input.strip() == "":
            st.error("❌ 请先输入 Prompt")
        elif not api_key_input or api_key_input.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
        else:
            with st.spinner("🔮 正在分析语义、提取关键词、构建结构化模板..."):
                try:
                    # 创建优化器
                    optimizer = PromptOptimizer(
                        api_key=api_key_input,
                        model=model_choice,
                        base_url=base_url if base_url else None,
                        provider=api_provider.lower()
                    )
                    
                    # 执行优化
                    result = optimizer.optimize(
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
                    error_msg = str(e)
                    st.error(f"❌ 优化失败：{error_msg}")
                    
                    # 根据错误类型提供具体的解决方案
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

    # 生成任务结果展示区域
    if st.session_state.result:
        result = st.session_state.result
        
        with col2:
            st.subheader("🌟 优化结果")
        
        # 优化思路展示
        with st.expander("🧠 查看优化思路 (Thinking Process)", expanded=True):
            st.write(result.thinking_process)
            
            # 应用的技术
            st.markdown("**🛠️ 应用的优化技术：**")
            techniques_html = "".join([
                f'<span class="technique-badge">{tech}</span>'
                for tech in result.enhancement_techniques
            ])
            st.markdown(techniques_html, unsafe_allow_html=True)
            
            # 新增的关键词
            if result.keywords_added:
                st.markdown("**🔑 新增的关键词：**")
                keywords_html = "".join([
                    f'<span class="keyword-badge">{kw}</span>'
                    for kw in result.keywords_added
                ])
                st.markdown(keywords_html, unsafe_allow_html=True)
            
            # 应用的框架
            st.markdown(f"**📐 应用的框架：** `{result.structure_applied}`")
        
        # 优化后的 Prompt
        st.markdown("**✨ 优化后的 Prompt（可直接复制）：**")
        st.text_area(
            "优化结果",
            value=result.improved_prompt,
            height=300,
            label_visibility="collapsed"
        )
        
        # 复制按钮
        if st.button("📋 复制到剪贴板", use_container_width=True):
            st.code(result.improved_prompt, language=None)
            st.success("✅ 已显示在代码框中，请手动复制")

# A/B 对比测试区域
if st.session_state.result:
    st.divider()
    st.subheader("🔬 A/B 效果对比测试")
    st.markdown("*让 AI 分别使用原始 Prompt 和优化后的 Prompt 执行任务，直观对比优化效果*")
    
    col_test1, col_test2, col_test3 = st.columns([2, 1, 2])
    
    with col_test2:
        if st.button("🚀 运行对比测试", type="primary", use_container_width=True):
            if not st.session_state.comparison_done:
                with st.spinner("⏳ 正在运行两个版本的 Prompt，请稍候..."):
                    try:
                        optimizer = PromptOptimizer(
                            api_key=api_key_input,
                            model=model_choice,
                            base_url=base_url if base_url else None,
                            provider=api_provider.lower()
                        )
                        
                        res_orig, res_opt = optimizer.compare_results(
                            original_prompt=user_input,
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

# ========== 分类任务界面 ==========
elif task_type == "分类任务":
    with col1:
        st.subheader("🏷️ 分类任务配置")
        st.info("📌 分类任务需要明确的标签定义和示例，系统将自动生成这些要素。")
        
        # 任务描述
        task_description = st.text_area(
            "任务描述",
            height=100,
            placeholder="例如：判断用户评论的情感倾向\n或：识别客服对话中的用户意图",
            help="清晰描述这是一个什么样的分类任务"
        )
        
        # 标签输入
        labels_input = st.text_input(
            "目标标签（用逗号分隔）",
            placeholder="例如：Positive, Negative, Neutral",
            help="输入所有可能的分类标签，用逗号分隔"
        )
        
        # 可选：示例文本
        with st.expander("💡 提供示例文本（可选）", expanded=False):
            st.caption("如果提供示例，系统会基于这些示例生成 Few-Shot 样本")
            example_text_1 = st.text_input("示例 1（可选）", placeholder="例如：这个产品太棒了！")
            example_text_2 = st.text_input("示例 2（可选）", placeholder="例如：质量很差，不推荐购买")
            example_text_3 = st.text_input("示例 3（可选）", placeholder="例如：一般般，没什么特别的")
        
        # 构建分类器按钮
        build_btn = st.button("🔨 构建分类器 Prompt", type="primary", use_container_width=True)
    
    # 分类任务优化逻辑
    if build_btn:
        if not task_description or not labels_input:
            st.error("❌ 请填写任务描述和目标标签！")
        elif not api_key_input or api_key_input.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
        else:
            # 解析标签
            labels_list = [label.strip() for label in labels_input.split(",") if label.strip()]
            
            if len(labels_list) < 2:
                st.error("❌ 至少需要 2 个标签")
            else:
                with st.spinner("🔮 正在生成标签定义、合成训练样本、构建分类器..."):
                    try:
                        # 创建优化器
                        optimizer = PromptOptimizer(
                            api_key=api_key_input,
                            model=model_choice,
                            base_url=base_url if base_url else None,
                            provider=api_provider.lower()
                        )
                        
                        # 收集示例文本
                        example_texts = []
                        if example_text_1:
                            example_texts.append(example_text_1)
                        if example_text_2:
                            example_texts.append(example_text_2)
                        if example_text_3:
                            example_texts.append(example_text_3)
                        
                        # 执行分类任务优化
                        result = optimizer.optimize_classification(
                            task_description=task_description,
                            labels=labels_list,
                            example_texts=example_texts if example_texts else None
                        )
                        
                        # 保存结果
                        st.session_state.classification_result = result
                        
                        st.success("✅ 分类器 Prompt 构建完成！")
                        
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ 构建失败：{error_msg}")
                        
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
            
            # 3. 标签定义
            with st.expander("🏷️ 标签详细定义", expanded=True):
                for label, definition in result.label_definitions.items():
                    st.markdown(f"**{label}**")
                    st.write(definition)
                    st.divider()
                st.caption("💡 系统自动补充了每个标签的具体标准，防止模型混淆。")
            
            # 4. Few-Shot 示例
            with st.expander("📝 自动合成的 Few-Shot 示例", expanded=True):
                for idx, example in enumerate(result.few_shot_examples, 1):
                    st.markdown(f"**示例 {idx}:**")
                    st.code(f"Input: {example.get('input', example.get('text', 'N/A'))}\nLabel: {example.get('label', 'N/A')}")
                st.caption("💡 这些示例帮助模型理解分类标准")
            
            # 5. 思维链引导
            with st.expander("🧠 思维链引导", expanded=False):
                st.write(result.reasoning_guidance)
            
            # 6. 输出格式
            with st.expander("📐 输出格式要求", expanded=False):
                st.code(result.output_format)
            
            # 7. 最终 Prompt
            st.markdown("**✨ 最终完整的分类 Prompt（可直接复制）：**")
            st.text_area(
                "分类器 Prompt",
                value=result.final_prompt,
                height=400,
                label_visibility="collapsed"
            )
            
            # 复制按钮
            if st.button("📋 复制到剪贴板", use_container_width=True, key="copy_classification"):
                st.code(result.final_prompt, language=None)
                st.success("✅ 已显示在代码框中，请手动复制")

elif task_type == "摘要任务":
    with col1:
        st.subheader("📄 摘要任务配置")
        st.info("📌 摘要任务需要明确信息提取规则，系统将设计最优的提取策略。")
        
        # 任务描述
        task_description = st.text_area(
            "任务描述",
            height=100,
            placeholder="例如：总结技术会议的核心决策和行动计划\n或：提取学术论文的研究贡献和创新点",
            help="清晰描述摘要的目的"
        )
        
        # 源文本类型
        source_type = st.selectbox(
            "📝 源文本类型",
            [
                "会议记录",
                "学术论文",
                "新闻报道",
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
            placeholder="例如：技术经理、研发总监、普通用户、投资人",
            help="摘要将呈现给谁看？这会影响语言风格和详细程度"
        )
        
        # 核心关注点
        focus_points = st.text_area(
            "🎯 核心关注点",
            height=100,
            placeholder="例如：\n- Bug 的根本原因\n- 提出的解决方案\n- 负责人和截止时间\n- 资源需求",
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
        if not task_description or not target_audience or not focus_points:
            st.error("❌ 请填写任务描述、目标受众和核心关注点！")
        elif not api_key_input or api_key_input.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
        else:
            with st.spinner("🔮 正在生成提取规则、设计输出格式、构建摘要器..."):
                try:
                    # 创建优化器
                    optimizer = PromptOptimizer(
                        api_key=api_key_input,
                        model=model_choice,
                        base_url=base_url if base_url else None,
                        provider=api_provider.lower()
                    )
                    
                    # 执行摘要任务优化
                    result = optimizer.optimize_summarization(
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
                    error_msg = str(e)
                    st.error(f"❌ 构建失败：{error_msg}")
                    
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
            
            # 5. 输出格式
            with st.expander("📐 输出格式模板", expanded=True):
                st.markdown(result.format_template)
                st.caption("💡 结构化格式让摘要更清晰易读")
            
            # 6. 处理步骤
            with st.expander("🔄 思考步骤引导", expanded=False):
                st.write(result.step_by_step_guide)
            
            # 7. 关注点
            with st.expander("🎯 核心关注领域", expanded=False):
                for idx, area in enumerate(result.focus_areas, 1):
                    st.markdown(f"**关注点 {idx}:** {area}")
            
            # 8. 最终 Prompt
            st.markdown("**✨ 最终完整的摘要 Prompt（可直接复制）：**")
            st.caption("💡 用 {{text}} 占位符表示待摘要的文本")
            st.text_area(
                "摘要器 Prompt",
                value=result.final_prompt,
                height=400,
                label_visibility="collapsed"
            )
            
            # 复制按钮
            if st.button("📋 复制到剪贴板", use_container_width=True, key="copy_summarization"):
                st.code(result.final_prompt, language=None)
                st.success("✅ 已显示在代码框中，请手动复制")

# 翻译任务分支
elif task_type == "翻译任务":
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
            help="专有名词的强制对应关系，模型将严格遵守"
        )
        
        # 构建翻译器按钮
        build_translation_btn = st.button("🔨 构建翻译器 Prompt", type="primary", use_container_width=True)
    
    # 翻译任务优化逻辑
    if build_translation_btn:
        if source_lang == target_lang:
            st.error("❌ 源语言和目标语言不能相同！")
        elif not api_key_input or api_key_input.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
        else:
            with st.spinner("🔮 正在设计领域专家角色、植入术语库、构建三步翻译法..."):
                try:
                    # 创建优化器
                    optimizer = PromptOptimizer(
                        api_key=api_key_input,
                        model=model_choice,
                        base_url=base_url if base_url else None,
                        provider=api_provider.lower()
                    )
                    
                    # 执行翻译任务优化
                    result = optimizer.optimize_translation(
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
                    error_msg = str(e)
                    st.error(f"❌ 构建失败：{error_msg}")
                    
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
            
            # 复制按钮
            if st.button("📋 复制到剪贴板", use_container_width=True, key="copy_translation"):
                st.code(result.final_prompt, language=None)
                st.success("✅ 已显示在代码框中，请手动复制")
            
            # 使用示例
            with st.expander("💡 使用示例", expanded=False):
                st.markdown(f"""
**如何使用这个翻译 Prompt：**

1. 复制上面的完整 Prompt
2. 将 `{{{{text}}}}` 替换为您要翻译的实际文本
3. 发送给 LLM（如 ChatGPT、Claude、Llama 等）

**示例（{source_lang} → {target_lang}）：**
```
{result.final_prompt[:200]}...
[这里放入您的 {source_lang} 文本]
```

**专业提示：**
- ✅ 术语表可以随时更新，每次翻译时保持一致
- ✅ 对于专业文档，建议先翻译一小段测试效果
- ✅ 如果译文不够地道，可以要求模型"再次润色"
                """)

# ========== 效果验证实验室 ==========
st.markdown("---")
st.header("🧪 效果验证实验室")
st.markdown("在此输入测试数据和标准答案，系统将自动计算性能指标（Accuracy / BLEU / ROUGE）。")

# 判断是否已经生成了优化后的 Prompt
has_result = False
current_result = None
placeholder_text = ""

if task_type == "生成任务" and st.session_state.result:
    has_result = True
    current_result = st.session_state.result
    placeholder_text = "待处理的输入"
elif task_type == "分类任务" and st.session_state.classification_result:
    has_result = True
    current_result = st.session_state.classification_result
    placeholder_text = "待分类的文本"
elif task_type == "摘要任务" and st.session_state.summarization_result:
    has_result = True
    current_result = st.session_state.summarization_result
    placeholder_text = "待摘要的文本"
elif task_type == "翻译任务" and st.session_state.translation_result:
    has_result = True
    current_result = st.session_state.translation_result
    placeholder_text = "待翻译的文本"

if not has_result:
    st.info("💡 请先在上方完成 Prompt 优化，然后再进行效果验证。")
else:
    st.success(f"✅ 检测到已优化的 {task_type} Prompt，可以开始验证！")
    
    # 验证区域
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        st.markdown("**📝 测试输入**")
        
        # 根据任务类型显示不同的提示
        if task_type == "分类任务":
            placeholder_hint = """示例（每行一个测试样本）：
这个产品真的很好用，非常满意！
价格太贵了，性价比不高。
还可以吧，没有特别的感觉。"""
            help_text = "分类任务支持批量测试：每行一个测试文本，系统会依次分类并计算整体准确率"
        elif task_type == "摘要任务":
            placeholder_hint = f"输入{placeholder_text}..."
            help_text = "摘要任务输入单个长文本进行测试"
        elif task_type == "翻译任务":
            placeholder_hint = f"输入{placeholder_text}..."
            help_text = "翻译任务输入单个文本进行测试"
        else:
            placeholder_hint = f"输入{placeholder_text}..."
            help_text = "输入需要测试的数据"
        
        test_input = st.text_area(
            "输入测试数据",
            height=150,
            placeholder=placeholder_hint,
            key="test_input",
            help=help_text
        )
        
        # 语言设置（用于 ROUGE 和 BLEU）
        if task_type in ["摘要任务", "翻译任务"]:
            test_lang = st.selectbox(
                "测试数据语言",
                ["中文", "英文"],
                key="test_lang",
                help="用于正确计算 ROUGE/BLEU 分数（中文需要分词）"
            )
    
    with col_test2:
        st.markdown("**✅ 标准参考答案**")
        
        # 根据任务类型显示不同的提示
        if task_type == "分类任务":
            ref_placeholder = """示例（每行一个标签，与测试数据一一对应）：
积极
消极
中立"""
            ref_help = "每行一个标签，顺序与左侧测试数据对应"
        elif task_type == "摘要任务":
            ref_placeholder = "输入人工撰写的标准摘要..."
            ref_help = "用于计算 ROUGE 分数的参考摘要"
        elif task_type == "翻译任务":
            ref_placeholder = "输入人工翻译的标准译文..."
            ref_help = "用于计算 BLEU 分数的参考译文"
        else:
            ref_placeholder = "输入标准答案或期望输出..."
            ref_help = "用于计算评估指标的参考答案"
        
        reference_output = st.text_area(
            "参考答案",
            height=150,
            placeholder=ref_placeholder,
            key="reference_output",
            help=ref_help
        )
        
        st.caption("💡 **为什么需要参考答案？**")
        if task_type == "分类任务":
            st.caption("Accuracy 需要对比「模型预测」和「正确标签」。支持批量测试，更准确评估分类效果。")
        else:
            st.caption("Accuracy/BLEU/ROUGE 等数学指标需要对比「模型输出」和「标准答案」来计算分数。")
    
    # 运行评估按钮
    if st.button("🚀 运行 Prompt 并计算指标", type="primary", use_container_width=True):
        if not test_input or not reference_output:
            st.error("❌ 请同时提供测试输入和参考答案！")
        elif not api_key_input or api_key_input.strip() == "":
            st.error("❌ 请先在侧边栏配置 API Key")
        else:
            # 添加详细日志
            print(f"\n{'='*60}")
            print(f"🧪 开始效果验证")
            print(f"{'='*60}")
            print(f"📋 任务类型: {task_type}")
            print(f"📝 测试输入长度: {len(test_input)} 字符")
            print(f"✅ 参考答案长度: {len(reference_output)} 字符")
            print(f"🔌 API 提供商: {api_provider}")
            print(f"🤖 使用模型: {model_choice}")
            print(f"{'='*60}\n")
            
            with st.spinner("🔮 模型正在根据优化后的 Prompt 生成结果..."):
                try:
                    print("🔧 步骤 1: 创建优化器...")
                    # 创建优化器（使用相同的配置）
                    optimizer = PromptOptimizer(
                        api_key=api_key_input,
                        model=model_choice,
                        base_url=base_url if base_url else None,
                        provider=api_provider.lower()
                    )
                    print("✅ 优化器创建成功")
                    
                    print("\n🔧 步骤 2: 构建最终 Prompt...")
                    
                    # 智能替换函数：尝试多种占位符格式
                    def smart_replace(template: str, text: str, task_type_name: str = "") -> str:
                        """智能替换各种可能的占位符格式"""
                        # 记录原始模板
                        original = template
                        
                        # 尝试各种占位符格式（按优先级排序）
                        replacements = [
                            # 标准占位符
                            ("{{text}}", text),
                            ("{text}", text),
                            ("{{input}}", text),
                            ("{input}", text),
                            
                            # 中文方括号占位符
                            ("[输入评论]", text),
                            ("[待分类文本]", text),
                            ("[待翻译文本]", text),
                            ("[待摘要文本]", text),
                            ("[输入文本]", text),
                            ("[文本内容]", text),
                            ("[用户输入]", text),
                            
                            # 中文花括号占位符
                            ("【输入评论】", text),
                            ("【待分类文本】", text),
                            ("【待翻译文本】", text),
                            ("【待摘要文本】", text),
                            ("【输入文本】", text),
                            ("【文本内容】", text),
                            ("【待处理文本】", text),
                            
                            # 英文描述性占位符
                            ("[INPUT]", text),
                            ("[TEXT]", text),
                            ("[CONTENT]", text),
                            ("{INPUT}", text),
                            ("{TEXT}", text),
                            
                            # 其他常见格式
                            ("<text>", text),
                            ("<input>", text),
                            ("$text", text),
                            ("$input", text),
                        ]
                        
                        result = template
                        replaced_count = 0
                        replaced_placeholders = []
                        
                        for placeholder, replacement in replacements:
                            if placeholder in result:
                                old_result = result
                                result = result.replace(placeholder, replacement)
                                if result != old_result:
                                    replaced_count += 1
                                    replaced_placeholders.append(placeholder)
                                    print(f"   ✅ 替换 '{placeholder}' -> 实际文本")
                        
                        if replaced_count == 0:
                            print(f"   ⚠️ 警告：未找到任何占位符！")
                            print(f"   📋 完整模板内容：")
                            print(f"   {template}")
                            print(f"   💡 提示：请检查模板中使用的占位符格式")
                            print(f"   🔧 尝试自动修复：在 Prompt 末尾添加文本插入位置...")
                            
                            # 根据任务类型添加合适的提示语
                            if "分类" in task_type_name:
                                result = template + f"\n\n待分类文本：{text}\n\n请分析上述文本并输出分类结果。"
                            elif "摘要" in task_type_name:
                                result = template + f"\n\n待摘要文本：\n{text}\n\n请根据上述要求生成摘要。"
                            elif "翻译" in task_type_name:
                                result = template + f"\n\n待翻译文本：\n{text}\n\n请翻译上述文本。"
                            else:
                                result = template + f"\n\n输入内容：{text}"
                            
                            print(f"   ✅ 已自动添加文本到 Prompt 末尾（任务类型：{task_type_name}）")
                        else:
                            print(f"   ✅ 成功替换 {replaced_count} 个占位符: {', '.join(replaced_placeholders)}")
                        
                        return result
                    
                    # 根据任务类型构建最终 Prompt
                    if task_type == "生成任务":
                        # 生成任务直接使用优化后的 prompt
                        print("📄 使用生成任务 Prompt 模板")
                        template = current_result.improved_prompt
                        print(f"📋 模板长度: {len(template)} 字符")
                        if len(template) < 100:
                            print(f"   ⚠️ 警告：Prompt 太短，可能不完整！")
                        print(f"📋 模板前500字符: {template[:500]}...")
                        final_prompt = smart_replace(template, test_input, task_type)
                        
                    elif task_type == "分类任务":
                        print("📄 使用分类任务 Prompt 模板")
                        template = current_result.final_prompt
                        print(f"📋 模板长度: {len(template)} 字符")
                        
                        # 检查 Prompt 质量
                        if len(template) < 200:
                            print(f"   ⚠️ 警告：Prompt 太短（< 200字符），可能不完整！")
                            print(f"   💡 建议：检查 LLM 是否正确生成了完整的 final_prompt")
                            st.warning("⚠️ 检测到生成的 Prompt 较短，可能影响分类效果。建议重新生成 Prompt。")
                        
                        print(f"📋 模板前500字符:\n{template[:500]}...")
                        if len(template) > 500:
                            print(f"📋 模板后200字符:\n...{template[-200:]}")
                        
                        final_prompt = smart_replace(template, test_input, task_type)
                        
                    elif task_type == "摘要任务":
                        print("📄 使用摘要任务 Prompt 模板")
                        template = current_result.final_prompt
                        print(f"📋 模板长度: {len(template)} 字符")
                        if len(template) < 200:
                            print(f"   ⚠️ 警告：Prompt 太短，可能不完整！")
                        print(f"📋 模板前500字符: {template[:500]}...")
                        final_prompt = smart_replace(template, test_input, task_type)
                        
                    elif task_type == "翻译任务":
                        print("📄 使用翻译任务 Prompt 模板")
                        template = current_result.final_prompt
                        print(f"📋 模板长度: {len(template)} 字符")
                        if len(template) < 200:
                            print(f"   ⚠️ 警告：Prompt 太短，可能不完整！")
                        print(f"📋 模板前500字符: {template[:500]}...")
                        final_prompt = smart_replace(template, test_input, task_type)
                    
                    print(f"\n✅ Prompt 构建完成")
                    print(f"📏 最终 Prompt 长度: {len(final_prompt)} 字符")
                    print(f"📋 最终 Prompt（前300字符）:\n{final_prompt[:300]}...")
                    print(f"\n🔍 检查占位符是否被替换:")
                    print(f"   - 是否还包含 '{{{{text}}}}': {'{{text}}' in final_prompt}")
                    print(f"   - 是否还包含 '{{text}}': {'{text}' in final_prompt}")
                    print(f"   - 是否包含测试输入: {test_input[:20] in final_prompt if len(test_input) > 20 else test_input in final_prompt}")
                    
                    print("\n🔧 步骤 3: 调用 LLM...")
                    # 调用 LLM
                    response = optimizer.llm.invoke(final_prompt)
                    prediction = response.content
                    print(f"✅ LLM 响应成功")
                    print(f"📏 预测结果长度: {len(prediction)} 字符")
                    print(f"📋 预测结果（前200字符）: {prediction[:200]}...")
                    
                    # 保存预测结果
                    st.session_state.prediction = prediction
                    st.session_state.test_reference = reference_output
                    
                    # 显示预测结果
                    st.markdown("---")
                    st.subheader("🤖 模型预测结果")
                    st.info(prediction)
                    
                    print("\n🔧 步骤 4: 计算评估指标...")
                    # 计算指标
                    st.markdown("---")
                    st.subheader("📊 性能评分")
                    
                    calc = MetricsCalculator()
                    print(f"📊 任务类型: {task_type}")
                    
                    # 根据任务类型选择指标
                    if task_type == "分类任务":
                        print("📈 计算分类任务 Accuracy...")
                        
                        # 分类任务支持批量测试：按行分割
                        test_samples = [line.strip() for line in test_input.strip().split('\n') if line.strip()]
                        reference_labels = [line.strip() for line in reference_output.strip().split('\n') if line.strip()]
                        
                        print(f"   🔹 测试样本数: {len(test_samples)}")
                        print(f"   🔹 参考标签数: {len(reference_labels)}")
                        
                        # 检查数量是否匹配
                        if len(test_samples) != len(reference_labels):
                            st.error(f"❌ 测试样本数量 ({len(test_samples)}) 与参考标签数量 ({len(reference_labels)}) 不匹配！")
                            print(f"   ❌ 数量不匹配！")
                        else:
                            # 如果只有一个样本，直接使用之前的预测结果
                            if len(test_samples) == 1:
                                pred_clean = prediction.strip().split('\n')[0].strip()
                                predictions = [pred_clean]
                                print(f"   🔹 单样本测试")
                                print(f"   🔹 预测: {pred_clean}")
                                print(f"   🔹 参考: {reference_labels[0]}")
                            else:
                                # 批量预测：对每个样本调用一次
                                predictions = []
                                print(f"   🔹 批量测试模式")
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for idx, sample in enumerate(test_samples):
                                    status_text.text(f"正在处理 {idx+1}/{len(test_samples)} ...")
                                    
                                    # 构建单个样本的 Prompt
                                    sample_prompt = smart_replace(template, sample, task_type)
                                    
                                    # 调用 LLM
                                    response = optimizer.llm.invoke(sample_prompt)
                                    pred = response.content.strip().split('\n')[0].strip()
                                    predictions.append(pred)
                                    
                                    print(f"   样本 {idx+1}: {sample[:30]}... -> 预测: {pred}")
                                    
                                    progress_bar.progress((idx + 1) / len(test_samples))
                                
                                status_text.empty()
                                progress_bar.empty()
                            
                            # 计算准确率
                            score = calc.calculate_accuracy(predictions, reference_labels)
                            print(f"   ✅ Accuracy 分数: {score}%")
                            
                            metric_name = "Accuracy (准确率)"
                            metric_key = "accuracy"
                            
                            col_m1, col_m2 = st.columns([1, 2])
                            with col_m1:
                                st.metric(label=metric_name, value=f"{score}%")
                                st.caption(f"测试样本: {len(test_samples)} 个")
                                st.caption(f"预测正确: {int(score * len(test_samples) / 100)} 个")
                            with col_m2:
                                level, color, advice = calc.get_metric_interpretation(metric_key, score)
                                st.markdown(f"**评级：** {level}")
                                if color == "success":
                                    st.success(advice)
                                elif color == "warning":
                                    st.warning(advice)
                                elif color == "error":
                                    st.error(advice)
                                else:
                                    st.info(advice)
                            
                            # 显示详细结果
                            with st.expander("📋 查看每个样本的预测结果", expanded=False):
                                result_df_data = []
                                for i, (sample, pred, ref) in enumerate(zip(test_samples, predictions, reference_labels), 1):
                                    is_correct = pred.lower() == ref.lower()
                                    result_df_data.append({
                                        "序号": i,
                                        "测试文本": sample[:50] + "..." if len(sample) > 50 else sample,
                                        "预测标签": pred,
                                        "正确标签": ref,
                                        "结果": "✅ 正确" if is_correct else "❌ 错误"
                                    })
                                
                                import pandas as pd
                                result_df = pd.DataFrame(result_df_data)
                                st.dataframe(result_df, use_container_width=True)
                    
                    elif task_type == "摘要任务":
                        print("📈 计算摘要任务 ROUGE...")
                        # 摘要任务：计算 ROUGE
                        lang_code = "zh" if test_lang == "中文" else "en"
                        print(f"   🔹 语言设置: {lang_code}")
                        print(f"   🔹 预测长度: {len(prediction)} 字符")
                        print(f"   🔹 参考长度: {len(reference_output)} 字符")
                        
                        rouge_scores = calc.calculate_rouge(prediction, reference_output, lang=lang_code)
                        print(f"   ✅ ROUGE 分数: {rouge_scores}")
                        
                        st.markdown("**ROUGE 分数：**")
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.metric("ROUGE-1", f"{rouge_scores['rouge1']}%", help="单词重合度")
                        with col_r2:
                            st.metric("ROUGE-2", f"{rouge_scores['rouge2']}%", help="双词组重合度")
                        with col_r3:
                            st.metric("ROUGE-L", f"{rouge_scores['rougeL']}%", help="最长公共子序列")
                        
                        # 使用 ROUGE-L 作为主要评价指标
                        level, color, advice = calc.get_metric_interpretation("rouge", rouge_scores['rougeL'])
                        st.markdown(f"**综合评级（基于 ROUGE-L）：** {level}")
                        if color == "success":
                            st.success(advice)
                        elif color == "warning":
                            st.warning(advice)
                        elif color == "error":
                            st.error(advice)
                        else:
                            st.info(advice)
                    
                    elif task_type == "翻译任务":
                        print("📈 计算翻译任务 BLEU...")
                        # 翻译任务：计算 BLEU
                        lang_code = "zh" if test_lang == "中文" else "en"
                        print(f"   🔹 语言设置: {lang_code}")
                        print(f"   🔹 预测翻译: {prediction[:100]}...")
                        print(f"   🔹 参考翻译: {reference_output[:100]}...")
                        
                        bleu_score = calc.calculate_bleu(prediction, reference_output, lang=lang_code)
                        print(f"   ✅ BLEU 分数: {bleu_score}%")
                        
                        col_b1, col_b2 = st.columns([1, 2])
                        with col_b1:
                            st.metric("BLEU Score", f"{bleu_score}%")
                        with col_b2:
                            level, color, advice = calc.get_metric_interpretation("bleu", bleu_score)
                            st.markdown(f"**评级：** {level}")
                            if color == "success":
                                st.success(advice)
                            elif color == "warning":
                                st.warning(advice)
                            elif color == "error":
                                st.error(advice)
                            else:
                                st.info(advice)
                    
                    elif task_type == "生成任务":
                        print("ℹ️ 生成任务使用定性评估")
                        # 生成任务没有标准指标，使用定性评估
                        st.info("💡 生成任务通常使用人工评估或 LLM-as-a-Judge 进行评价，暂不支持自动化指标。")
                        st.markdown("**建议评估维度：**")
                        st.markdown("- ✅ 是否遵循了 Prompt 的要求？")
                        st.markdown("- ✅ 输出格式是否正确？")
                        st.markdown("- ✅ 内容是否准确、完整？")
                    
                    print("\n✅ 效果验证完成！")
                    print(f"{'='*60}\n")
                    # 对比展示
                    with st.expander("🔍 详细对比", expanded=False):
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.markdown("**🤖 模型输出：**")
                            st.code(prediction, language=None)
                        with comp_col2:
                            st.markdown("**✅ 参考答案：**")
                            st.code(reference_output, language=None)
                    
                except Exception as e:
                    print(f"\n❌ 验证过程发生错误！")
                    print(f"{'='*60}")
                    error_msg = str(e)
                    print(f"🐛 错误类型: {type(e).__name__}")
                    print(f"📝 错误信息: {error_msg}")
                    
                    import traceback
                    print(f"\n📄 完整堆栈信息：")
                    traceback.print_exc()
                    print(f"{'='*60}\n")
                    
                    st.error(f"❌ 评估失败：{str(e)}")
                    import traceback
                    with st.expander("查看错误详情"):
                        st.code(traceback.format_exc())

# ========== 随机搜索优化功能 ==========
st.markdown("---")
st.header("🔬 Prompt 自动寻优实验室")

with st.expander("💡 什么是自动寻优？", expanded=False):
    st.markdown("""
    **自动寻优**将 Prompt 工程从手工艺提升到工业化生产：
    
    ### 🎲 随机搜索 (Random Search)
    
    **原理**: 随机组合不同的角色、风格、技巧，在测试集上实际运行并打分
    
    **优势**:
    - ✅ 快速覆盖搜索空间
    - ✅ 突破人类思维定势
    - ✅ 适合快速探索
    
    **成本**: `迭代次数 × 测试集大小` 次 API 调用
    
    ---
    
    ### 🧬 遗传算法 (Genetic Algorithm)
    
    **原理**: 模拟生物进化，让高分 Prompt "繁衍"出更好的后代
    
    **核心机制**:
    1. **选择**: 保留得分最高的精英个体
    2. **交叉**: 两个高分 Prompt 交换组件（如 A 的角色 + B 的风格）
    3. **变异**: 随机修改某些基因，引入新可能性
    
    **优势**:
    - ✅ **越往后效果越好**（进化趋势）
    - ✅ 自动收敛到局部最优
    - ✅ 适合精细打磨
    
    **成本**: `代数 × 种群大小 × 测试集大小` 次 API 调用（**更高**）
    
    ---
    
    ### 📊 如何选择？
    
    | 场景 | 推荐算法 | 原因 |
    |------|---------|------|
    | 快速探索 | 随机搜索 | 低成本，广撒网 |
    | 精细优化 | 遗传算法 | 持续进化，逼近极致 |
    | 预算有限 | 随机搜索 | API 调用次数更少 |
    | 追求极致 | 遗传算法 | 多代进化，突破瓶颈 |
    
    **建议**: 先用随机搜索找到 70-80 分的 Prompt，再用遗传算法冲刺到 90+ 分！
    """)

# 算法选择器
algo_col1, algo_col2 = st.columns([2, 3])

with algo_col1:
    st.subheader("🎯 选择优化算法")
    
    algo_type = st.radio(
        "算法策略",
        ["🎲 随机搜索", "🧬 遗传算法"],
        help="随机搜索适合快速尝试；遗传算法适合深度优化",
        key="algo_type"
    )
    
    if algo_type == "🎲 随机搜索":
        st.info("""
        **随机搜索特点**:
        - 每次独立随机
        - 搜索速度快
        - 成本相对较低
        """)
    else:
        st.info("""
        **遗传算法特点**:
        - 多代持续进化
        - 得分单调递增
        - 成本相对较高
        - **推荐**: 先随机搜索再遗传算法
        """)

with algo_col2:
    st.markdown("### 📊 算法对比")
    
    comparison_data = {
        "指标": ["搜索策略", "收敛性", "成本", "适用场景"],
        "🎲 随机搜索": ["随机抽样", "无保证", "较低", "快速探索"],
        "🧬 遗传算法": ["进化迭代", "单调递增", "较高", "精细打磨"]
    }
    import pandas as pd
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.markdown("---")

search_col1, search_col2 = st.columns([3, 2])

with search_col1:
    st.subheader("📋 配置搜索任务")
    
    # 任务类型选择
    search_task_type = st.selectbox(
        "选择任务类型",
        ["classification", "summarization", "translation"],
        format_func=lambda x: {
            "classification": "分类任务 (Classification)",
            "summarization": "摘要任务 (Summarization)",
            "translation": "翻译任务 (Translation)"
        }[x],
        key="search_task_type"
    )
    
    # 任务描述
    search_task_desc = st.text_area(
        "任务描述",
        placeholder="例如：对用户评论进行情感分类（积极/消极/中立）",
        height=80,
        key="search_task_desc"
    )
    
    # 测试数据集
    st.markdown("#### 📥 测试数据集 (Validation Set)")
    st.caption("请提供至少2-3个测试样本和对应的标准答案，用于评估不同 Prompt 的实际效果")
    
    # 根据任务类型提供不同的默认数据
    if search_task_type == "classification":
        default_test_data = [
            # 简单案例（基准）
            {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
            {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
            
            # 困难案例：混合情感
            {"input": "产品质量不错，但是价格有点贵，总体来说还行", "ground_truth": "中立"},
            {"input": "功能很强大，就是操作有点复杂，需要学习成本", "ground_truth": "中立"},
            
            # 困难案例：反讽语气
            {"input": "哇，真是太'棒'了，收到就坏了，非常'满意'呢", "ground_truth": "消极"},
            
            # 困难案例：委婉表达
            {"input": "emmm...怎么说呢，可能不太适合我吧", "ground_truth": "消极"},
            
            # 困难案例：纯客观描述
            {"input": "包装是红色的，尺寸和描述一致，昨天收到的", "ground_truth": "中立"},
            
            # 困难案例：期待落空
            {"input": "本来抱了很大期望，结果就这？", "ground_truth": "消极"}
        ]
    elif search_task_type == "summarization":
        default_test_data = [
            {
                "input": "今天召开了产品评审会议，讨论了新功能的设计方案。会议决定采用方案A，由张三负责开发，预计2周完成。此外，还讨论了市场推广策略，决定先在一线城市试点，收集用户反馈后再全面推广。",
                "ground_truth": "会议决定采用方案A，张三负责开发（2周），先在一线城市试点后再全面推广。"
            },
            {
                "input": "公司年会将于下月15日举行，地点在市中心大酒店。各部门需提前准备节目，人力资源部负责协调。预算控制在50万以内，需要提前预定场地和晚宴。",
                "ground_truth": "年会下月15日市中心大酒店举行，各部门准备节目，HR协调，预算50万。"
            },
            {
                "input": "根据最新销售数据，Q3季度营收同比增长35%，主要来自于新产品线的贡献。其中，AI产品线增长最快，达到了60%的同比增长率。但是，传统产品线出现了10%的下滑，需要引起重视。",
                "ground_truth": "Q3营收增长35%，AI产品线增长60%，但传统产品下滑10%需关注。"
            },
            {
                "input": "用户反馈主要集中在三个方面：首先是界面设计需要优化，有42%的用户提到操作不够直观；其次是加载速度慢，有35%的用户抱怨；最后是缺少某些核心功能，占23%。总体满意度为3.2分（满分5分）。",
                "ground_truth": "用户反馈：界面不直观(42%)、加载慢(35%)、缺功能(23%)，满意度3.2/5分。"
            }
        ]
    else:  # translation
        default_test_data = [
            {"input": "人工智能正在改变世界", "ground_truth": "Artificial intelligence is changing the world"},
            {"input": "机器学习是AI的核心技术", "ground_truth": "Machine learning is the core technology of AI"},
            {"input": "深度学习模型在图像识别领域取得了突破性进展", "ground_truth": "Deep learning models have made breakthrough progress in the field of image recognition"},
            {"input": "自然语言处理技术使计算机能够理解和生成人类语言", "ground_truth": "Natural language processing technology enables computers to understand and generate human language"},
            {"input": "大语言模型的出现标志着人工智能发展的新阶段", "ground_truth": "The emergence of large language models marks a new stage in the development of artificial intelligence"}
        ]
    
    # 使用 data_editor 让用户编辑测试数据
    test_dataset = st.data_editor(
        default_test_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "input": st.column_config.TextColumn("测试输入", width="medium"),
            "ground_truth": st.column_config.TextColumn("标准答案", width="medium")
        },
        key="search_test_dataset"
    )

with search_col2:
    st.subheader("⚙️ 搜索参数")
    
    # 根据算法类型显示不同参数
    if algo_type == "🎲 随机搜索":
        # 随机搜索参数
        search_iterations = st.slider(
            "搜索迭代次数",
            min_value=3,
            max_value=20,
            value=5,
            help="尝试多少种不同的 Prompt 组合",
            key="search_iterations"
        )
        
        # 显示预估消耗
        estimated_calls = search_iterations * len(test_dataset) if test_dataset else 0
        st.info(f"💰 预计 API 调用：**{estimated_calls}** 次")
        
    else:  # 遗传算法
        # 遗传算法参数
        ga_generations = st.slider(
            "进化代数 (Generations)",
            min_value=3,
            max_value=10,
            value=5,
            help="种群进化的代数，越多效果越好但成本越高",
            key="ga_generations"
        )
        
        ga_population = st.slider(
            "种群规模 (Population Size)",
            min_value=4,
            max_value=20,
            value=8,
            help="每一代有多少个个体，规模越大覆盖越全面",
            key="ga_population"
        )
        
        # 高级参数
        with st.expander("🔧 高级参数", expanded=False):
            ga_elite_ratio = st.slider(
                "精英保留比例",
                min_value=0.1,
                max_value=0.5,
                value=0.2,
                step=0.1,
                help="保留多少比例的优秀个体到下一代",
                key="ga_elite_ratio"
            )
            
            ga_mutation_rate = st.slider(
                "变异概率",
                min_value=0.1,
                max_value=0.5,
                value=0.2,
                step=0.1,
                help="每个基因发生变异的概率",
                key="ga_mutation_rate"
            )
        
        # 显示预估消耗
        estimated_calls = ga_generations * ga_population * len(test_dataset) if test_dataset else 0
        st.warning(f"💰 预计 API 调用：**{estimated_calls}** 次")
        st.caption("⚠️ 遗传算法成本较高，建议先用小规模参数测试")
    
    st.markdown("---")
    
    # 开始搜索按钮
    start_search_btn = st.button(
        f"🚀 开始{'随机搜索' if algo_type == '🎲 随机搜索' else '遗传进化'}寻优",
        type="primary",
        use_container_width=True,
        disabled=not (search_task_desc and test_dataset and len(test_dataset) >= 1),
        key="start_search_btn"
    )

# 执行搜索（随机搜索或遗传算法）
if start_search_btn:
    if not api_key_input or api_key_input.strip() == "":
        st.error("❌ 请先在侧边栏配置 API Key")
    elif not search_task_desc or search_task_desc.strip() == "":
        st.error("❌ 请输入任务描述")
    elif not test_dataset or len(test_dataset) < 1:
        st.error("❌ 请至少提供 1 条测试数据")
    else:
        try:
            # 创建优化器
            optimizer = PromptOptimizer(
                api_key=api_key_input,
                model=model_choice,
                base_url=base_url if base_url else None,
                provider=api_provider.lower()
            )
            
            # 转换测试数据格式
            import pandas as pd
            if isinstance(test_dataset, pd.DataFrame):
                test_data_list = test_dataset.to_dict('records')
            elif isinstance(test_dataset, list):
                test_data_list = test_dataset
            else:
                test_data_list = list(test_dataset)
            
            # 阶段1: 生成搜索空间
            with st.status("🧠 正在分析任务，生成搜索空间...", expanded=True) as status:
                st.write("让 LLM 分析任务特点，生成可能的角色、风格和技巧组合...")
                
                search_space = optimizer.generate_search_space(
                    task_description=search_task_desc,
                    task_type=search_task_type
                )
                
                st.success("✅ 搜索空间生成完成！")
                
                # 展示生成的变量池
                space_col1, space_col2, space_col3 = st.columns(3)
                with space_col1:
                    st.markdown("**🎭 角色池**")
                    for role in search_space.roles:
                        st.write(f"• {role}")
                with space_col2:
                    st.markdown("**🎨 风格池**")
                    for style in search_space.styles:
                        st.write(f"• {style}")
                with space_col3:
                    st.markdown("**🔧 技巧池**")
                    for tech in search_space.techniques:
                        st.write(f"• {tech}")
                
                # 根据算法类型执行不同逻辑
                if algo_type == "🎲 随机搜索":
                    # === 随机搜索 ===
                    status.update(label="🎲 正在执行随机搜索...", state="running")
                    
                    progress_bar = st.progress(0.0)
                    progress_text = st.empty()
                    
                    def update_progress_random(current, total, message):
                        progress = current / total
                        progress_bar.progress(progress)
                        progress_text.text(f"{message} ({current}/{total})")
                    
                    # 运行随机搜索
                    all_results, best_result = optimizer.run_random_search(
                        task_description=search_task_desc,
                        task_type=search_task_type,
                        test_dataset=test_data_list,
                        search_space=search_space,
                        iterations=search_iterations,
                        progress_callback=update_progress_random
                    )
                    
                    evolution_history = None  # 随机搜索无进化历史
                    
                else:
                    # === 遗传算法 ===
                    status.update(label="🧬 正在执行遗传算法进化...", state="running")
                    
                    progress_bar = st.progress(0.0)
                    progress_text = st.empty()
                    
                    # 实时更新进化曲线
                    chart_placeholder = st.empty()
                    history_data = []
                    
                    def update_progress_ga(gen, total_gen, best_score, avg_score):
                        """遗传算法进度回调"""
                        progress = gen / total_gen
                        progress_bar.progress(progress)
                        progress_text.text(f"第 {gen}/{total_gen} 代：最佳 {best_score:.2f}, 平均 {avg_score:.2f}")
                        
                        # 更新进化曲线
                        history_data.append({
                            "代数": gen,
                            "最高分": best_score,
                            "平均分": avg_score
                        })
                        chart_df = pd.DataFrame(history_data)
                        chart_placeholder.line_chart(chart_df.set_index("代数"))
                    
                    # 运行遗传算法
                    all_results, best_result, evolution_history = optimizer.run_genetic_algorithm(
                        task_description=search_task_desc,
                        task_type=search_task_type,
                        test_dataset=test_data_list,
                        search_space=search_space,
                        generations=ga_generations,
                        population_size=ga_population,
                        elite_ratio=ga_elite_ratio,
                        mutation_rate=ga_mutation_rate,
                        progress_callback=update_progress_ga
                    )
                
                status.update(label="✅ 优化完成！", state="complete")
            
            # 阶段3: 展示结果
            st.markdown("---")
            st.header("🏆 优化结果")
            
            # 最佳结果高亮展示
            if algo_type == "🧬 遗传算法" and evolution_history:
                improvement = evolution_history[-1]['best_score'] - evolution_history[0]['best_score']
                st.success(f"🥇 **最终得分：{best_result.avg_score:.2f}** | 🧬 进化增益：+{improvement:.2f} 分")
            else:
                st.success(f"🥇 **最佳得分：{best_result.avg_score:.2f}**")
            
            result_col1, result_col2 = st.columns([3, 2])
            
            with result_col1:
                st.markdown("### 🎯 冠军 Prompt")
                st.code(best_result.full_prompt, language="text")
            
            with result_col2:
                st.markdown("### 📊 策略组成")
                st.markdown(f"**🎭 角色：** {best_result.role}")
                st.markdown(f"**🎨 风格：** {best_result.style}")
                st.markdown(f"**🔧 技巧：** {best_result.technique}")
                st.markdown(f"**💯 得分：** {best_result.avg_score:.2f}")
                
                if algo_type == "🧬 遗传算法" and evolution_history:
                    st.markdown("---")
                    st.markdown("**🧬 进化统计**")
                    st.markdown(f"• 初始最高分: {evolution_history[0]['best_score']:.2f}")
                    st.markdown(f"• 最终最高分: {evolution_history[-1]['best_score']:.2f}")
                    st.markdown(f"• 进化提升: +{improvement:.2f} 分")
            
            # 所有结果排行榜
            st.markdown("---")
            st.subheader("📋 完整优化记录")
            
            # 构建结果表格
            results_df = pd.DataFrame([
                {
                    "排名": i + 1,
                    "ID": r.iteration_id,
                    "角色": r.role,
                    "风格": r.style,
                    "技巧": r.technique,
                    "得分": f"{r.avg_score:.2f}"
                }
                for i, r in enumerate(sorted(all_results, key=lambda x: x.avg_score, reverse=True))
            ])
            
            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True
            )
            
            # 可视化
            st.markdown("---")
            
            if algo_type == "🧬 遗传算法" and evolution_history:
                # 遗传算法：显示进化曲线
                st.subheader("📈 进化曲线")
                
                import matplotlib.pyplot as plt
                import matplotlib
                matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
                matplotlib.rcParams['axes.unicode_minus'] = False
                
                fig, ax = plt.subplots(figsize=(10, 5))
                
                generations = [h['generation'] for h in evolution_history]
                best_scores = [h['best_score'] for h in evolution_history]
                avg_scores = [h['avg_score'] for h in evolution_history]
                worst_scores = [h['worst_score'] for h in evolution_history]
                
                ax.plot(generations, best_scores, marker='o', linewidth=2, markersize=8, label='最高分', color='#2ecc71')
                ax.plot(generations, avg_scores, marker='s', linewidth=2, markersize=6, label='平均分', color='#3498db')
                ax.plot(generations, worst_scores, marker='^', linewidth=1, markersize=5, label='最低分', color='#e74c3c', alpha=0.5)
                
                ax.fill_between(generations, worst_scores, best_scores, alpha=0.2, color='#3498db')
                
                ax.set_xlabel('代数 (Generation)')
                ax.set_ylabel('得分 (Score)')
                ax.set_title('遗传算法进化曲线 - 可以看到得分持续上升！')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
                # 进化数据表
                with st.expander("📊 查看详细进化数据", expanded=False):
                    evo_df = pd.DataFrame(evolution_history)
                    evo_df.columns = ['代数', '最高分', '平均分', '最低分']
                    st.dataframe(evo_df, use_container_width=True, hide_index=True)
                
            else:
                # 随机搜索：显示得分分布
                st.subheader("📈 得分分布图")
                
                import matplotlib.pyplot as plt
                import matplotlib
                matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
                matplotlib.rcParams['axes.unicode_minus'] = False
                
                fig, ax = plt.subplots(figsize=(10, 4))
                scores = [r.avg_score for r in all_results]
                iterations = [r.iteration_id for r in all_results]
                
                ax.plot(iterations, scores, marker='o', linewidth=2, markersize=8, color='#3498db')
                ax.axhline(y=best_result.avg_score, color='r', linestyle='--', linewidth=2, label=f'最佳得分: {best_result.avg_score:.2f}')
                ax.set_xlabel('迭代次数')
                ax.set_ylabel('得分')
                ax.set_title('随机搜索得分变化 - 随机波动，无规律')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
            
            # 保存最佳结果到 session_state
            st.session_state.best_search_result = best_result
            
            st.success(f"✅ {'随机搜索' if algo_type == '🎲 随机搜索' else '遗传算法'}优化完成！您可以将冠军 Prompt 复制使用。")
            
            if algo_type == "🎲 随机搜索":
                st.info("💡 **提示**: 如果想进一步提升，可以切换到「🧬 遗传算法」进行深度优化！")
            
        except Exception as e:
            st.error(f"❌ 优化过程出错：{str(e)}")
            import traceback
            with st.expander("查看错误详情"):
                st.code(traceback.format_exc())

col_foot1, col_foot2, col_foot3 = st.columns(3)

with col_foot1:
    st.metric("核心技术", "LLM-as-Optimizer", "🤖")
with col_foot2:
    st.metric("优化策略", "3大核心方法", "🎯")
with col_foot3:
    st.metric("框架支持", "4种模板", "📐")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "🚀 AI Prompt 自动优化系统"
    "</div>",
    unsafe_allow_html=True
)
