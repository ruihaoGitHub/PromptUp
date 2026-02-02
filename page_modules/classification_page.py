"""
分类任务页面模块
提供分类器 Prompt 生成和优化功能
"""
import streamlit as st
import pandas as pd
import io
from .base_page import BasePage
from config.defaults import get_default_value, get_placeholder, get_default_lab_dataset


class ClassificationPage(BasePage):
    """分类任务页面"""
    
    def render(self):
        """渲染分类任务页面"""
        col1, col2 = self.create_two_columns()
        
        with col1:
            st.subheader("🏷️ 分类任务配置")
            
            # 任务描述
            task_description = st.text_area(
                "任务描述",
                height=100,
                placeholder=get_placeholder("classification", "task_description"),
                help="清晰描述这是一个什么样的分类任务。",
                key="cls_task_desc"
            )
            
            # 标签输入
            labels_input = st.text_input(
                "目标标签（用逗号分隔）",
                placeholder=get_placeholder("classification", "labels"),
                help="输入所有可能的分类标签，用逗号分隔（中文逗号、英文逗号均可）。",
                key="cls_labels"
            )
            
            # 构建分类器按钮
            build_btn = st.button("🔨 构建分类器 Prompt", type="primary", use_container_width=True)
        
        # 分类任务优化逻辑
        if build_btn:
            if not self._validate_api_key():
                return
            
            # 如果用户没有输入，使用默认值
            if not task_description or task_description.strip() == "":
                task_description = get_default_value("classification", "task_description")
                st.info("💡 未输入任务描述，使用默认示例")
            
            if not labels_input or labels_input.strip() == "":
                labels_input = get_default_value("classification", "labels")
                st.info("💡 未输入标签，使用默认标签：" + labels_input)
            
            # 解析标签（支持中文逗号和英文逗号）
            labels_input_normalized = labels_input.replace("，", ",")
            labels_list = [label.strip() for label in labels_input_normalized.split(",") if label.strip()]
            
            # 保存用户输入的标签到 session_state，供随机搜索使用
            st.session_state.user_labels = labels_list
            st.session_state.user_task_description = task_description
            
            if len(labels_list) < 2:
                st.error("❌ 至少需要 2 个标签")
            else:
                with st.spinner("🔮 正在构建分类器..."):
                    try:
                        # 执行分类任务优化
                        result = self.optimizer.optimize_classification(
                            task_description=task_description,
                            labels=labels_list
                        )
                        
                        # 保存结果
                        st.session_state.classification_result = result
                        
                        st.success("✅ 分类器 Prompt 构建完成！")
                        
                    except Exception as e:
                        self._handle_optimization_error(e)
        
        # 显示分类任务优化结果
        if 'classification_result' in st.session_state and st.session_state.classification_result:
            result = st.session_state.classification_result
            
            with col2:
                st.subheader("🎯 分类器 Prompt")
                
                # 1. 优化思路
                with st.expander("🧠 查看优化思路", expanded=True):
                    st.write(result.thinking_process)
                
                # 2. 角色定义
                with st.expander("👤 角色设定", expanded=False):
                    st.info(result.role_definition)
                
                # 3. 最终 Prompt
                st.markdown("**✨ 最终完整的分类 Prompt（可直接复制）：**")
                st.text_area(
                    "分类器 Prompt",
                    value=result.final_prompt,
                    height=400,
                    label_visibility="collapsed"
                )
                
                # 直接显示代码框，带有复制按钮
                st.code(result.final_prompt, language=None)
                st.caption("📌 点击代码框右上角的复制按钮即可复制")
        
        # 验证实验室区域
        if 'classification_result' in st.session_state and st.session_state.classification_result:
            self._render_validation_lab(st.session_state.classification_result)
    
    def _render_validation_lab(self, result):
        """渲染分类验证实验室"""
        st.divider()
        st.subheader("🔬 效果验证实验室")
        st.markdown("*使用测试样本验证分类器的准确性*")

        # 测试数据来源选择
        st.markdown("**📊 测试数据来源**")
        data_source = st.radio(
            "选择数据来源",
            ["使用默认数据", "上传CSV文件", "手动输入"],
            key="cls_data_source",
            help="选择测试数据的来源方式",
            horizontal=True
        )

        # 根据选择显示相应的输入界面
        if data_source == "上传CSV文件":
            self._render_csv_upload()
        elif data_source == "手动输入":
            self._render_manual_input()

        # 获取测试数据（优先使用自定义数据，否则使用默认数据）
        test_cases = self._get_test_cases()
        
        col_test1, col_test2 = st.columns([1, 1])
        
        with col_test1:
            st.markdown("**📝 测试样本**")
            st.caption("修改下方的测试文本和预期标签：")
            
            # 显示测试样本
            for i, case in enumerate(test_cases):
                with st.container():
                    st.markdown(f"**测试 {i+1}:**")
                    text = st.text_input(f"文本 {i+1}", value=case["text"], key=f"cls_test_text_{i}")
                    expected = st.text_input(f"预期标签 {i+1}", value=case["expected"], key=f"cls_test_expected_{i}")
                    test_cases[i] = {"text": text, "expected": expected}
        
        with col_test2:
            st.markdown("**🎯 评分标准**")
            st.info("""
**Accuracy（准确率）**
- 🟢 **优秀** ≥ 80%
- 🟡 **良好** 60% - 80%
- 🔴 **需改进** < 60%

**计算方式**：正确预测数 / 总样本数 × 100%
            """)
        
        # 运行验证按钮
        if st.button("🚀 运行验证测试", type="primary", use_container_width=True, key="cls_validation_btn"):
            with st.spinner("⏳ 正在使用优化后的 Prompt 进行分类..."):
                try:
                    results = []
                    for i, case in enumerate(test_cases):
                        # 替换占位符
                        prompt_with_text = result.final_prompt.replace("[待分类文本]", case["text"])
                        prompt_with_text = prompt_with_text.replace("{{text}}", case["text"])
                        prompt_with_text = prompt_with_text.replace("{text}", case["text"])
                        
                        # 调用 LLM
                        response = self.optimizer.llm.invoke(prompt_with_text)
                        predicted = response.content.strip()
                        
                        results.append({
                            "text": case["text"],
                            "expected": case["expected"],
                            "predicted": predicted,
                            "correct": predicted == case["expected"]
                        })
                    
                    # 保存结果
                    st.session_state.cls_validation_results = results
                    
                    # 计算准确率
                    accuracy = sum(1 for r in results if r["correct"]) / len(results) * 100
                    st.session_state.cls_accuracy = accuracy
                    
                except Exception as e:
                    st.error(f"❌ 验证失败：{str(e)}")
        
        # 显示验证结果
        if 'cls_validation_results' in st.session_state and st.session_state.cls_validation_results:
            results = st.session_state.cls_validation_results
            accuracy = st.session_state.cls_accuracy
            
            st.divider()
            st.markdown("### 📊 验证结果")
            
            # 显示准确率
            if accuracy >= 80:
                st.success(f"🎉 准确率：{accuracy:.1f}% - 🟢 优秀！")
            elif accuracy >= 60:
                st.info(f"👍 准确率：{accuracy:.1f}% - 🟡 良好")
            else:
                st.warning(f"⚠️ 准确率：{accuracy:.1f}% - 🔴 需改进")
            
            # 详细结果表格
            st.markdown("**详细结果：**")
            for i, r in enumerate(results, 1):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.text(f"{r['text'][:40]}...")
                with col2:
                    st.text(f"预期: {r['expected']}")
                with col3:
                    st.text(f"预测: {r['predicted']}")
                with col4:
                    if r['correct']:
                        st.success("✅")
                    else:
                        st.error("❌")
    
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
    
    def _render_csv_upload(self):
        """渲染CSV文件上传界面"""
        st.markdown("**📁 CSV文件上传**")
        st.info("CSV文件应包含两列：'text'（文本）和 'expected'（预期标签）")
        
        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=["csv"],
            key="cls_csv_upload",
            help="上传包含测试数据的CSV文件"
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
                st.success(f"✅ 成功加载 {len(df)} 条测试数据")
                st.markdown("**数据预览：**")
                st.dataframe(df.head(), use_container_width=True)
                
                # 保存到session_state
                st.session_state.custom_test_data = df.to_dict('records')
                
            except Exception as e:
                st.error(f"❌ 文件读取失败：{str(e)}")
    
    def _render_manual_input(self):
        """渲染手动输入界面"""
        st.markdown("**✏️ 手动输入测试数据**")
        
        # 获取当前的手动输入数据
        manual_data = st.session_state.get('manual_test_data', [
            {"text": "", "expected": ""},
            {"text": "", "expected": ""},
            {"text": "", "expected": ""}
        ])
        
        st.markdown("添加测试样本：")
        
        # 显示现有的输入框
        updated_data = []
        for i, item in enumerate(manual_data):
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                text = st.text_input(
                    f"文本 {i+1}",
                    value=item["text"],
                    key=f"manual_text_{i}",
                    placeholder="输入测试文本"
                )
            with col2:
                expected = st.text_input(
                    f"标签 {i+1}",
                    value=item["expected"],
                    key=f"manual_expected_{i}",
                    placeholder="预期标签"
                )
            with col3:
                if st.button("🗑️", key=f"delete_{i}", help=f"删除第{i+1}行"):
                    continue  # 跳过这行，不添加到updated_data中
            
            if text.strip() or expected.strip():  # 只保存非空行
                updated_data.append({"text": text, "expected": expected})
        
        # 添加新行的按钮
        if st.button("➕ 添加一行", key="add_manual_row"):
            updated_data.append({"text": "", "expected": ""})
        
        # 保存到session_state
        st.session_state.manual_test_data = updated_data
        
        # 显示有效数据数量
        valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
        st.info(f"当前有 {valid_count} 条有效测试数据")
    
    def _get_test_cases(self):
        """获取测试数据，根据用户选择返回相应数据"""
        data_source = st.session_state.get('cls_data_source', '使用默认数据')

        if data_source == "使用默认数据":
            # 清除自定义数据
            if 'custom_test_data' in st.session_state:
                del st.session_state.custom_test_data
            if 'manual_test_data' in st.session_state:
                del st.session_state.manual_test_data
            return get_default_lab_dataset("classification")

        elif data_source == "上传CSV文件":
            # 返回CSV数据，如果没有则返回默认数据
            if 'custom_test_data' in st.session_state and st.session_state.custom_test_data:
                return st.session_state.custom_test_data
            else:
                return get_default_lab_dataset("classification")

        elif data_source == "手动输入":
            # 返回手动输入数据，如果没有则返回默认数据
            if 'manual_test_data' in st.session_state:
                manual_data = [item for item in st.session_state.manual_test_data
                              if item["text"].strip() and item["expected"].strip()]
                if manual_data:
                    return manual_data
            return get_default_lab_dataset("classification")

        # 默认情况
        return get_default_lab_dataset("classification")
