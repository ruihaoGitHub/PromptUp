"""
AI Prompt 自动优化系统 - Streamlit 主界面
重构后的精简版本，使用页面模块和 UI 组件系统
"""
import streamlit as st
import pandas as pd
from config.defaults import get_default_value, get_default_dataset
from config.defaults import get_default_value
from dotenv import load_dotenv
from optimizer import PromptOptimizer
from page_modules import (
    GenerationPage,
    ClassificationPage, 
    SummarizationPage,
    TranslationPage
)
from ui import apply_custom_styles, render_sidebar

# 加载环境变量
load_dotenv()

# 应用自定义样式（包含页面配置）
apply_custom_styles()

# 标题区域
st.markdown('<p class="main-header">🚀 AI Prompt 自动优化大师</p>', unsafe_allow_html=True)

# 渲染侧边栏并获取配置
config = render_sidebar()
task_type = config['task_type']
api_provider = config['api_provider']
api_key_input = config['api_key']
base_url = config['base_url']
model_choice = config['model']

# 根据任务类型显示不同的副标题
if task_type == "生成任务":
    st.markdown('<p class="sub-header">输入简单的想法，系统将自动利用 <b>结构化模板、语义扩展、关键词增强</b> 技术为您生成专家级 Prompt</p>', unsafe_allow_html=True)
elif task_type == "分类任务":
    st.markdown('<p class="sub-header">系统将为您设计专业的分类器 Prompt，自动生成最佳分类策略</p>', unsafe_allow_html=True)
elif task_type == "摘要任务":
    st.markdown('<p class="sub-header">系统将为您设计智能的摘要器 Prompt，自动优化 <b>信息提取规则、压缩策略</b> 和输出格式</p>', unsafe_allow_html=True)
elif task_type == "翻译任务":
    st.markdown('<p class="sub-header">系统将为您构建专业的翻译器 Prompt，整合 <b>术语表、风格指南</b> 和领域知识库</p>', unsafe_allow_html=True)

# 创建优化器实例（所有页面共享）
if api_key_input and api_key_input.strip():
    optimizer = PromptOptimizer(
        api_key=api_key_input,
        model=model_choice,
        base_url=base_url if base_url else None,
        provider=api_provider.lower()
    )
    
    # 将配置保存到 session_state，供页面模块使用
    st.session_state.api_key_input = api_key_input
    st.session_state.api_provider = api_provider
    st.session_state.model_choice = model_choice
    st.session_state.base_url = base_url
else:
    optimizer = None

# 根据任务类型渲染对应的页面
if not optimizer:
    # 如果没有配置 API Key，显示提示
    st.warning("⚠️ 请先在左侧边栏配置 API Key")
elif task_type == "生成任务":
    generation_page = GenerationPage(optimizer)
    generation_page.render()
elif task_type == "分类任务":
    classification_page = ClassificationPage(optimizer)
    classification_page.render()
elif task_type == "摘要任务":
    summarization_page = SummarizationPage(optimizer)
    summarization_page.render()
elif task_type == "翻译任务":
    translation_page = TranslationPage(optimizer)
    translation_page.render()


def _get_classification_test_dataset():
    """获取分类任务的测试数据集，优先使用用户自定义数据"""
    # 检查是否有自定义CSV数据
    if 'custom_test_data' in st.session_state and st.session_state.custom_test_data:
        custom_data = st.session_state.custom_test_data
        # 转换为标准格式
        return [{"input": item["text"], "ground_truth": item["expected"]} for item in custom_data]

    # 检查是否有手动输入数据
    if 'manual_test_data' in st.session_state:
        manual_data = [item for item in st.session_state.manual_test_data
                      if item["text"].strip() and item["expected"].strip()]
        if manual_data:
            # 转换为标准格式
            return [{"input": item["text"], "ground_truth": item["expected"]} for item in manual_data]

    # 使用默认数据集
    return get_default_dataset("classification")


def _get_random_search_test_dataset(task_key: str):
    """获取随机搜索使用的测试数据集，根据用户选择的数据源"""
    if task_key == "classification":
        data_source_key = "random_search_data_source"
        custom_key = "random_search_custom_test_data"
        manual_key = "random_search_manual_test_data"
        default_dataset = get_default_dataset("classification")
    elif task_key == "summarization":
        data_source_key = "random_search_data_source_summarization"
        custom_key = "random_search_custom_test_data_summarization"
        manual_key = "random_search_manual_test_data_summarization"
        default_dataset = get_default_dataset("summarization")
    elif task_key == "translation":
        data_source_key = "random_search_data_source_translation"
        custom_key = "random_search_custom_test_data_translation"
        manual_key = "random_search_manual_test_data_translation"
        default_dataset = get_default_dataset("translation")
    else:
        return []

    data_source = st.session_state.get(data_source_key, '使用默认数据')

    if data_source == "使用默认数据":
        # 清除随机搜索的自定义数据
        if custom_key in st.session_state:
            del st.session_state[custom_key]
        if manual_key in st.session_state:
            del st.session_state[manual_key]
        return default_dataset

    elif data_source == "上传CSV文件":
        # 返回随机搜索的CSV数据，如果没有则返回默认数据
        if custom_key in st.session_state and st.session_state[custom_key]:
            custom_data = st.session_state[custom_key]
            return [{"input": item["text"], "ground_truth": item["expected"]} for item in custom_data]
        else:
            return default_dataset

    elif data_source == "手动输入":
        # 返回随机搜索的手动输入数据，如果没有则返回默认数据
        if manual_key in st.session_state:
            manual_data = [item for item in st.session_state[manual_key]
                          if item["text"].strip() and item["expected"].strip()]
            if manual_data:
                return [{"input": item["text"], "ground_truth": item["expected"]} for item in manual_data]
        return default_dataset

    # 默认情况
    return default_dataset


def _render_random_search_csv_upload():
    """渲染随机搜索CSV文件上传界面"""
    st.markdown("**📁 随机搜索CSV文件上传**")
    st.info("CSV文件应包含两列：'text'（文本）和 'expected'（预期标签）")

    uploaded_file = st.file_uploader(
        "选择用于随机搜索的CSV文件",
        type=["csv"],
        key="random_search_csv_upload",
        help="上传包含测试数据的CSV文件用于随机搜索优化"
    )

    if uploaded_file is not None:
        try:
            # 读取CSV文件
            df = pd.read_csv(uploaded_file)

            # 验证列名
            required_columns = ["text", "expected"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"❌ CSV文件必须包含以下列：{', '.join(required_columns)}")
                return

            # 显示数据预览
            st.success(f"✅ 成功加载 {len(df)} 条测试数据用于随机搜索")
            st.markdown("**数据预览：**")
            st.dataframe(df.head(), use_container_width=True)

            # 保存到session_state
            st.session_state.random_search_custom_test_data = df.to_dict('records')

        except Exception as e:
            st.error(f"❌ 文件读取失败：{str(e)}")


def _render_random_search_manual_input():
    """渲染随机搜索手动输入界面"""
    st.markdown("**✏️ 随机搜索手动输入测试数据**")

    # 获取当前的手动输入数据
    manual_data = st.session_state.get('random_search_manual_test_data', [
        {"text": "", "expected": ""},
        {"text": "", "expected": ""},
        {"text": "", "expected": ""}
    ])

    st.markdown("添加用于随机搜索的测试样本：")

    # 显示现有的输入框
    updated_data = []
    for i, item in enumerate(manual_data):
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            text = st.text_input(
                f"文本 {i+1}",
                value=item["text"],
                key=f"random_search_manual_text_{i}",
                placeholder="输入测试文本"
            )
        with col2:
            expected = st.text_input(
                f"标签 {i+1}",
                value=item["expected"],
                key=f"random_search_manual_expected_{i}",
                placeholder="预期标签"
            )
        with col3:
            if st.button("🗑️", key=f"random_search_delete_{i}", help=f"删除第{i+1}行"):
                continue  # 跳过这行，不添加到updated_data中

        if text.strip() or expected.strip():  # 只保存非空行
            updated_data.append({"text": text, "expected": expected})

    # 添加新行的按钮
    if st.button("➕ 添加一行", key="random_search_add_manual_row"):
        updated_data.append({"text": "", "expected": ""})

    # 保存到session_state
    st.session_state.random_search_manual_test_data = updated_data

    # 显示有效数据数量
    valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
    st.info(f"当前有 {valid_count} 条有效测试数据用于随机搜索")


def _render_random_search_csv_upload_summarization():
    """渲染摘要任务随机搜索CSV文件上传界面"""
    st.markdown("**📁 随机搜索CSV文件上传（摘要任务）**")
    st.info("CSV文件应包含两列：'text'（原文）和 'expected'（参考摘要）")

    uploaded_file = st.file_uploader(
        "选择用于随机搜索的CSV文件",
        type=["csv"],
        key="random_search_csv_upload_summarization",
        help="上传包含摘要测试数据的CSV文件用于随机搜索优化"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            required_columns = ["text", "expected"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"❌ CSV文件必须包含以下列：{', '.join(required_columns)}")
                return

            st.success(f"✅ 成功加载 {len(df)} 条测试数据用于随机搜索")
            st.markdown("**数据预览：**")
            st.dataframe(df.head(), use_container_width=True)

            st.session_state.random_search_custom_test_data_summarization = df.to_dict('records')

        except Exception as e:
            st.error(f"❌ 文件读取失败：{str(e)}")


def _render_random_search_manual_input_summarization():
    """渲染摘要任务随机搜索手动输入界面"""
    st.markdown("**✏️ 随机搜索手动输入测试数据（摘要任务）**")

    manual_data = st.session_state.get('random_search_manual_test_data_summarization', [
        {"text": "", "expected": ""},
        {"text": "", "expected": ""},
        {"text": "", "expected": ""}
    ])

    st.markdown("添加用于随机搜索的测试样本：")

    updated_data = []
    for i, item in enumerate(manual_data):
        col1, col2, col3 = st.columns([4, 4, 1])
        with col1:
            text = st.text_area(
                f"原文 {i+1}",
                value=item["text"],
                key=f"random_search_sum_manual_text_{i}",
                height=100,
                placeholder="输入待摘要原文"
            )
        with col2:
            expected = st.text_area(
                f"参考摘要 {i+1}",
                value=item["expected"],
                key=f"random_search_sum_manual_expected_{i}",
                height=100,
                placeholder="输入参考摘要"
            )
        with col3:
            if st.button("🗑️", key=f"random_search_sum_delete_{i}", help=f"删除第{i+1}行"):
                continue

        if text.strip() or expected.strip():
            updated_data.append({"text": text, "expected": expected})

    if st.button("➕ 添加一行", key="random_search_sum_add_manual_row"):
        updated_data.append({"text": "", "expected": ""})

    st.session_state.random_search_manual_test_data_summarization = updated_data

    valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
    st.info(f"当前有 {valid_count} 条有效测试数据用于随机搜索")


def _render_random_search_csv_upload_translation():
    """渲染翻译任务随机搜索CSV文件上传界面"""
    st.markdown("**📁 随机搜索CSV文件上传（翻译任务）**")
    st.info("CSV文件应包含两列：'text'（原文）和 'expected'（参考译文）")

    uploaded_file = st.file_uploader(
        "选择用于随机搜索的CSV文件",
        type=["csv"],
        key="random_search_csv_upload_translation",
        help="上传包含翻译测试数据的CSV文件用于随机搜索优化"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            required_columns = ["text", "expected"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"❌ CSV文件必须包含以下列：{', '.join(required_columns)}")
                return

            st.success(f"✅ 成功加载 {len(df)} 条测试数据用于随机搜索")
            st.markdown("**数据预览：**")
            st.dataframe(df.head(), use_container_width=True)

            st.session_state.random_search_custom_test_data_translation = df.to_dict('records')

        except Exception as e:
            st.error(f"❌ 文件读取失败：{str(e)}")


def _render_random_search_manual_input_translation():
    """渲染翻译任务随机搜索手动输入界面"""
    st.markdown("**✏️ 随机搜索手动输入测试数据（翻译任务）**")

    manual_data = st.session_state.get('random_search_manual_test_data_translation', [
        {"text": "", "expected": ""},
        {"text": "", "expected": ""},
        {"text": "", "expected": ""}
    ])

    st.markdown("添加用于随机搜索的测试样本：")

    updated_data = []
    for i, item in enumerate(manual_data):
        col1, col2, col3 = st.columns([4, 4, 1])
        with col1:
            text = st.text_area(
                f"原文 {i+1}",
                value=item["text"],
                key=f"random_search_trans_manual_text_{i}",
                height=100,
                placeholder="输入待翻译原文"
            )
        with col2:
            expected = st.text_area(
                f"参考译文 {i+1}",
                value=item["expected"],
                key=f"random_search_trans_manual_expected_{i}",
                height=100,
                placeholder="输入参考译文"
            )
        with col3:
            if st.button("🗑️", key=f"random_search_trans_delete_{i}", help=f"删除第{i+1}行"):
                continue

        if text.strip() or expected.strip():
            updated_data.append({"text": text, "expected": expected})

    if st.button("➕ 添加一行", key="random_search_trans_add_manual_row"):
        updated_data.append({"text": "", "expected": ""})

    st.session_state.random_search_manual_test_data_translation = updated_data

    valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
    st.info(f"当前有 {valid_count} 条有效测试数据用于随机搜索")


def _get_random_search_config(task_type_label: str):
    """根据任务类型返回随机搜索配置"""
    if task_type_label == "分类任务":
        # 获取用户输入的标签和任务描述
        user_labels = st.session_state.get('user_labels', ["积极", "消极", "中立"])
        user_task_desc = st.session_state.get('user_task_description', get_default_value("classification", "task_description"))
        
        # 动态生成任务描述
        labels_str = ", ".join(user_labels)
        task_desc = f"{user_task_desc}，判断为{labels_str}"
        
        # 获取测试数据集（使用随机搜索专用数据集获取函数）
        test_dataset = _get_random_search_test_dataset("classification")
        
        return (task_desc, "classification", test_dataset, {"labels": user_labels})
    if task_type_label == "摘要任务":
        # 获取用户输入的任务描述
        user_task_desc = st.session_state.get('user_task_description_summarization', get_default_value("summarization", "task_description"))
        
        # 获取其他摘要配置
        source_type = st.session_state.get(
            'summarization_source_type',
            get_default_value("summarization", "source_type")
        )
        target_audience = st.session_state.get(
            'summarization_target_audience',
            get_default_value("summarization", "target_audience")
        )
        focus_points = st.session_state.get(
            'summarization_focus_points',
            get_default_value("summarization", "focus_points")
        )
        
        # 动态生成任务描述
        task_desc = user_task_desc
        
        test_dataset = _get_random_search_test_dataset("summarization")

        return (task_desc, "summarization", test_dataset, {
            "source_type": source_type,
            "target_audience": target_audience,
            "focus_points": focus_points
        })
    if task_type_label == "翻译任务":
        # 获取用户输入的任务描述
        user_task_desc = st.session_state.get('user_task_description_translation', get_default_value("translation", "task_description"))
        
        # 获取其他翻译配置
        source_lang = st.session_state.get('translation_source_lang', '英文')
        target_lang = st.session_state.get('translation_target_lang', '中文')
        domain = st.session_state.get(
            'translation_domain',
            get_default_value("translation", "domain")
        )
        tone = st.session_state.get(
            'translation_tone',
            get_default_value("translation", "tone")
        )
        
        # 动态生成任务描述
        task_desc = user_task_desc
        
        test_dataset = _get_random_search_test_dataset("translation")

        return (task_desc, "translation", test_dataset, {
            "source_lang": source_lang,
            "target_lang": target_lang,
            "domain": domain,
            "tone": tone
        })
    return None


