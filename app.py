"""
AI Prompt 自动优化系统 - Streamlit 界面
"""
import streamlit as st
import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer, OptimizedPrompt
from nvidia_models import get_model_list

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
    
    # 优化模式
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

# 主界面布局
col1, col2 = st.columns([1, 1])

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

# 优化逻辑
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

# 结果展示区域
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

# 底部信息
st.divider()
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
    "🚀 AI Prompt 自动优化系统 | Powered by LangChain & GPT-4 | "
    "<a href='https://github.com' style='color: #667eea;'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
