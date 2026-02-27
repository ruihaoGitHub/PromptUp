"""关键词贡献度分析（UI 渲染组件）"""

import streamlit as st

from utils.keyword_analyzer import analyze_keyword_contribution


def render_contribution_analysis(prompt: str) -> None:
    """在 Streamlit 页面中渲染关键词贡献度分析结果。"""
    with st.spinner("正在分析关键词贡献度..."):
        df_contrib = analyze_keyword_contribution(prompt)

    st.subheader("📊 关键词贡献度分析")
    st.dataframe(df_contrib, use_container_width=True)

    csv = df_contrib.to_csv(index=True, encoding="utf-8-sig")
    st.download_button(
        label="📥 下载分析结果CSV",
        data=csv,
        file_name="关键词贡献度分析结果.csv",
        mime="text/csv",
    )
