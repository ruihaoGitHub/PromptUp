"""
Streamlit 自定义样式
"""
import streamlit as st


def apply_custom_styles():
    """应用自定义 CSS 样式"""
    
    # 页面配置（必须在最开始调用）
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
        div[data-baseweb="tooltip"] {
            visibility: hidden !important;
            opacity: 0 !important;
        }
        .stTextArea textarea {
            font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_radio_styles():
    """应用单选按钮的自定义样式"""
    st.markdown("""
    <style>
        div[data-testid="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 1.3rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] > div:last-child {
            font-size: 1.15rem !important;
            font-weight: 500 !important;
        }
    </style>
    """, unsafe_allow_html=True)
