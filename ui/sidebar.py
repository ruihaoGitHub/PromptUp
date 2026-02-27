"""
Streamlit 侧边栏配置面板
"""
import streamlit as st
import os
from config.nvidia_models import NVIDIA_MODELS
from .styles import apply_radio_styles


def render_sidebar():
    """
    渲染侧边栏配置面板
    
    Returns:
        dict: 包含用户配置的字典，格式为：
        {
            'task_type': str,  # '生成任务', '分类任务', '摘要任务', '翻译任务'
            'api_provider': str,  # 'NVIDIA', 'OpenAI'
            'api_key': str,
            'base_url': str,
            'model': str
        }
    """
    with st.sidebar:
        st.header("⚙️ 系统配置")
        
        # 应用单选按钮样式
        apply_radio_styles()
        
        # 任务类型选择
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
            config = _render_nvidia_config()
        else:  # OpenAI
            config = _render_openai_config()
        
        st.divider()
        
        # 使用说明
        _render_usage_guide()
        
        # 示例 Prompt
        _render_examples()
    
    # 返回配置
    return {
        'task_type': task_type,
        'api_provider': api_provider,
        'api_key': config['api_key'],
        'base_url': config['base_url'],
        'model': config['model']
    }


def _render_nvidia_config():
    """渲染 NVIDIA API 配置界面"""
    st.markdown("✨ **NVIDIA API 配置**")
    
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
    
    # NVIDIA 模型选择
    categories = list(NVIDIA_MODELS.keys())
    default_category_index = categories.index("Llama 系列") if "Llama 系列" in categories else 0
    
    selected_category = st.selectbox(
        "📂 选择模型系列",
        categories,
        index=default_category_index,
        help="先选择模型发布商/系列"
    )
    
    models_in_category = NVIDIA_MODELS[selected_category]
    default_model = "meta/llama-3.3-70b-instruct"
    default_model_index = 0
    if default_model in models_in_category:
        default_model_index = models_in_category.index(default_model)
    
    model_choice = st.selectbox(
        "🤖 选择具体模型",
        models_in_category,
        index=default_model_index,
        help=f"{selected_category} 下的所有可用模型"
    )
    
    return {
        'api_key': api_key_input,
        'base_url': base_url,
        'model': model_choice
    }


def _render_openai_config():
    """渲染 OpenAI API 配置界面"""
    st.markdown("✨ **OpenAI API 配置**")
    
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
    
    return {
        'api_key': api_key_input,
        'base_url': base_url,
        'model': model_choice
    }


def _render_usage_guide():
    """渲染使用说明"""
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


def _render_examples():
    """渲染示例 Prompt"""
    with st.expander("💡 示例 Prompt", expanded=False):
        st.markdown("""
        **文案类**：
        - "简单prompt：推荐一下索尼降噪耳机\\n场景描述：发在小红书上，目标是学生党，突出性价比和降噪，语气要活泼"
        - "创作一个品牌故事"
        
        **代码类**：
        - "写个贪吃蛇游戏"
        - "帮我实现一个登录系统"
        
        **分析类**：
        - "分析市场趋势"
        - "总结论文要点"
        """)
