"""
分类任务页面模块
提供分类器 Prompt 生成和优化功能
"""
import streamlit as st
import pandas as pd
import sys
import os
# 将项目根目录（PromptUp）添加到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.contribution_analysis import render_contribution_analysis
from .base_page import BasePage
from config.defaults import get_default_value, get_placeholder, get_default_lab_dataset, get_default_dataset


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

                render_contribution_analysis(result.final_prompt)

                # 直接显示代码框，带有复制按钮
                st.code(result.final_prompt, language=None)
                st.caption("📌 点击代码框右上角的复制按钮即可复制")
        
        # 验证实验室区域
        if 'classification_result' in st.session_state and st.session_state.classification_result:
            @st.fragment
            def _validation_lab_fragment():
                self._render_validation_lab(st.session_state.classification_result)

            _validation_lab_fragment()

        @st.fragment
        def _optimization_lab_fragment():
            self._render_optimization_lab()

        _optimization_lab_fragment()

    def _render_optimization_lab(self):
        """渲染分类任务优化实验室（随机搜索/遗传算法）"""
        st.divider()
        st.subheader("🧬 提示词优化（随机搜索 / 贝叶斯优化 / 遗传算法）")
        st.markdown("*通过搜索/进化采样角色/风格/技巧组合，在小型测试集上寻找更优 Prompt 结构*" )

        optimization_algorithm = st.radio(
            "选择优化算法",
            ["随机搜索", "贝叶斯优化", "遗传算法"],
            key="cls_opt_algorithm",
            help="随机搜索适合快速体验，遗传算法适合更系统的优化",
            horizontal=True
        )

        st.markdown("**📊 优化数据来源**")
        data_source = st.radio(
            "选择优化使用的数据来源",
            ["使用默认数据", "上传CSV文件", "手动输入"],
            key="cls_opt_data_source",
            help="选择用于优化的测试数据来源",
            horizontal=True
        )

        if data_source == "上传CSV文件":
            self._render_opt_csv_upload()
        elif data_source == "手动输入":
            self._render_opt_manual_input()

        task_desc, task_key, dataset, extra_config = self._get_optimization_config()

        if optimization_algorithm == "随机搜索":
            col_a, col_b = st.columns([1, 2])
            with col_a:
                iterations = st.slider("迭代次数", min_value=5, max_value=50, value=12, step=1, key="cls_opt_iterations")
            with col_b:
                st.caption("建议：快速体验 5-10 次；有效优化 20-50 次（成本更高）。")

            if st.button("🚀 运行随机搜索", type="primary", use_container_width=True, key="cls_opt_random_btn"):
                with st.spinner("⏳ 正在生成搜索空间并执行随机搜索..."):
                    try:
                        search_space = self.optimizer.search_space_generator.generate(
                            task_description=task_desc,
                            task_type=task_key,
                            **extra_config
                        )

                        st.success("✅ 搜索空间生成完成！")
                        st.info("💡 系统将从这些选项中随机组合进行测试，每个组合包含：1个角色 + 1种风格 + 1种技巧")
                        self._render_search_space_preview(search_space)

                        results, best = self.optimizer.random_search.run(
                            task_description=task_desc,
                            task_type=task_key,
                            test_dataset=dataset,
                            search_space=search_space,
                            iterations=iterations,
                            labels=extra_config.get("labels")
                        )

                        st.session_state.cls_opt_random_results = results
                        st.session_state.cls_opt_random_best = best
                        st.session_state.cls_opt_random_space = search_space
                    except Exception as e:
                        st.error(f"❌ 随机搜索失败：{str(e)}")

            if 'cls_opt_random_best' in st.session_state and st.session_state.cls_opt_random_best:
                best = st.session_state.cls_opt_random_best
                search_space = st.session_state.get('cls_opt_random_space')
                results = st.session_state.get('cls_opt_random_results', [])
                # 新增：随机搜索得分曲线
                if results:
                    st.divider()
                    st.markdown("### 📈 随机搜索得分曲线")
                    df = pd.DataFrame({
                        "迭代": [r.iteration_id for r in results],
                        "得分": [r.avg_score for r in results]
                    })
                    st.line_chart(df.set_index("迭代"))
                self._render_optimization_result(best, search_space)
        elif optimization_algorithm == "遗传算法":
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                generations = st.slider("进化代数", min_value=3, max_value=20, value=6, step=1, key="cls_opt_generations")
            with col_b:
                population_size = st.slider("种群规模", min_value=4, max_value=24, value=8, step=1, key="cls_opt_population")
            with col_c:
                elite_ratio = st.slider("精英比例", min_value=0.1, max_value=0.5, value=0.2, step=0.05, key="cls_opt_elite")
            with col_d:
                mutation_rate = st.slider("变异率", min_value=0.05, max_value=0.6, value=0.2, step=0.05, key="cls_opt_mutation")

            if st.button("🧬 运行遗传算法", type="primary", use_container_width=True, key="cls_opt_ga_btn"):
                with st.spinner("⏳ 正在生成搜索空间并执行遗传算法..."):
                    try:
                        search_space = self.optimizer.search_space_generator.generate(
                            task_description=task_desc,
                            task_type=task_key,
                            **extra_config
                        )

                        st.success("✅ 搜索空间生成完成！")
                        st.info("💡 系统将从这些选项中进化组合进行测试，每个组合包含：1个角色 + 1种风格 + 1种技巧")
                        self._render_search_space_preview(search_space)

                        progress = st.progress(0)
                        progress_text = st.empty()

                        def _progress_callback(current_gen, total_gen, best_score, avg_score):
                            if total_gen > 0:
                                progress_value = int(min(100, (current_gen / total_gen) * 100))
                                progress.progress(progress_value)
                            progress_text.info(
                                f"第 {current_gen}/{total_gen} 代 | 最佳得分 {best_score:.2f} | 平均得分 {avg_score:.2f}"
                            )

                        results, best, evolution_history = self.optimizer.run_genetic_algorithm(
                            task_description=task_desc,
                            task_type=task_key,
                            test_dataset=dataset,
                            search_space=search_space,
                            generations=generations,
                            population_size=population_size,
                            elite_ratio=elite_ratio,
                            mutation_rate=mutation_rate,
                            progress_callback=_progress_callback
                        )

                        st.session_state.cls_opt_ga_results = results
                        st.session_state.cls_opt_ga_best = best
                        st.session_state.cls_opt_ga_history = evolution_history
                        st.session_state.cls_opt_ga_space = search_space
                    except Exception as e:
                        st.error(f"❌ 遗传算法失败：{str(e)}")

            if 'cls_opt_ga_best' in st.session_state and st.session_state.cls_opt_ga_best:
                best = st.session_state.cls_opt_ga_best
                search_space = st.session_state.get('cls_opt_ga_space')
                evolution_history = st.session_state.get('cls_opt_ga_history', [])
                self._render_optimization_result(best, search_space, evolution_history)
        else:
            col_a, col_b = st.columns([1, 2])
            with col_a:
                n_trials = st.slider("试验次数", min_value=5, max_value=50, value=12, step=1, key="cls_opt_bo_trials")
            with col_b:
                st.caption("建议：快速体验 8-12 次；稳定优化 15-30 次（成本更高）。")

            if st.button("🧪 运行贝叶斯优化", type="primary", use_container_width=True, key="cls_opt_bo_btn"):
                with st.spinner("⏳ 正在生成搜索空间并执行贝叶斯优化..."):
                    try:
                        search_space = self.optimizer.search_space_generator.generate(
                            task_description=task_desc,
                            task_type=task_key,
                            **extra_config
                        )

                        st.success("✅ 搜索空间生成完成！")
                        st.info("💡 系统将使用 TPE 智能选择组合进行测试，每个组合包含：1个角色 + 1种风格 + 1种技巧")
                        self._render_search_space_preview(search_space)

                        progress = st.progress(0)
                        progress_text = st.empty()

                        def _progress_callback(current_trial, total_trials, best_score):
                            if total_trials > 0:
                                progress_value = int(min(100, (current_trial / total_trials) * 100))
                                progress.progress(progress_value)
                            progress_text.info(
                                f"试验 {current_trial}/{total_trials} | 当前最佳 {best_score:.2f}"
                            )

                        results, best, trial_history = self.optimizer.run_bayesian_optimization(
                            task_description=task_desc,
                            task_type=task_key,
                            test_dataset=dataset,
                            search_space=search_space,
                            n_trials=n_trials,
                            progress_callback=_progress_callback
                        )

                        st.session_state.cls_opt_bo_results = results
                        st.session_state.cls_opt_bo_best = best
                        st.session_state.cls_opt_bo_history = trial_history
                        st.session_state.cls_opt_bo_space = search_space
                    except Exception as e:
                        st.error(f"❌ 贝叶斯优化失败：{str(e)}")

            if 'cls_opt_bo_best' in st.session_state and st.session_state.cls_opt_bo_best:
                best = st.session_state.cls_opt_bo_best
                search_space = st.session_state.get('cls_opt_bo_space')
                trial_history = st.session_state.get('cls_opt_bo_history', [])
                if trial_history:
                    st.divider()
                    st.markdown("### 📈 贝叶斯优化得分曲线")
                    df = pd.DataFrame({
                        "试验": [h["trial"] for h in trial_history],
                        "得分": [h["score"] for h in trial_history],
                        "历史最佳": [h["best_score"] for h in trial_history]
                    })
                    st.line_chart(df.set_index("试验"))
                self._render_optimization_result(best, search_space)

    def _render_search_space_preview(self, search_space):
        with st.expander("🔍 查看生成的搜索空间", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🎭 角色设定 (5个)**")
                for i, role in enumerate(search_space.roles, 1):
                    st.markdown(f"{i}. {role}")
            with col2:
                st.markdown("**🎨 回答风格 (5种)**")
                for i, style in enumerate(search_space.styles, 1):
                    st.markdown(f"{i}. {style}")
            with col3:
                st.markdown("**🛠️ 提示技巧 (3种)**")
                for i, technique in enumerate(search_space.techniques, 1):
                    st.markdown(f"{i}. {technique}")

    def _render_optimization_result(self, best, search_space, evolution_history=None):
        st.success(f"✅ 最佳得分：{best.avg_score:.2f}")
        st.markdown(f"**最佳组合：** {best.role} + {best.style} + {best.technique}")
        st.text_area("最佳 Prompt", value=best.full_prompt, height=200)

        if evolution_history:
            st.divider()
            st.markdown("### 📈 进化过程")
            history_df = pd.DataFrame(evolution_history)
            history_df = history_df.rename(columns={
                "generation": "代数",
                "best_score": "最佳得分",
                "avg_score": "平均得分"
            })
            st.line_chart(history_df.set_index("代数")[["最佳得分", "平均得分"]])

        if search_space:
            st.divider()
            st.markdown("### 🔍 搜索空间详情")
            with st.expander("查看完整的搜索空间", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**🎭 角色设定 (5个)**")
                    for i, role in enumerate(search_space.roles, 1):
                        if role == best.role:
                            st.markdown(f"**{i}. {role} ← 最佳选择**")
                        else:
                            st.markdown(f"{i}. {role}")
                with col2:
                    st.markdown("**🎨 回答风格 (5种)**")
                    for i, style in enumerate(search_space.styles, 1):
                        if style == best.style:
                            st.markdown(f"**{i}. {style} ← 最佳选择**")
                        else:
                            st.markdown(f"{i}. {style}")
                with col3:
                    st.markdown("**🛠️ 提示技巧 (3种)**")
                    for i, technique in enumerate(search_space.techniques, 1):
                        if technique == best.technique:
                            st.markdown(f"**{i}. {technique} ← 最佳选择**")
                        else:
                            st.markdown(f"{i}. {technique}")

    def _render_opt_csv_upload(self):
        st.markdown("**📁 CSV文件上传**")
        st.info("CSV文件应包含两列：'text'（文本）和 'expected'（预期标签）")
        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=["csv"],
            key="cls_opt_csv_upload",
            help="上传包含测试数据的CSV文件"
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
                st.session_state.cls_opt_custom_data = df.to_dict('records')
            except Exception as e:
                st.error(f"❌ 文件读取失败：{str(e)}")

    def _render_opt_manual_input(self):
        st.markdown("**✏️ 手动输入测试数据**")
        manual_data = st.session_state.get('cls_opt_manual_data', [
            {"text": "", "expected": ""},
            {"text": "", "expected": ""},
            {"text": "", "expected": ""}
        ])

        updated_data = []
        for i, item in enumerate(manual_data):
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                text = st.text_input(
                    f"文本 {i+1}",
                    value=item["text"],
                    key=f"cls_opt_manual_text_{i}",
                    placeholder="输入测试文本"
                )
            with col2:
                expected = st.text_input(
                    f"标签 {i+1}",
                    value=item["expected"],
                    key=f"cls_opt_manual_expected_{i}",
                    placeholder="预期标签"
                )
            with col3:
                if st.button("🗑️", key=f"cls_opt_manual_delete_{i}", help=f"删除第{i+1}行"):
                    continue

            if text.strip() or expected.strip():
                updated_data.append({"text": text, "expected": expected})

        if st.button("➕ 添加一行", key="cls_opt_manual_add_row"):
            updated_data.append({"text": "", "expected": ""})

        st.session_state.cls_opt_manual_data = updated_data
        valid_count = sum(1 for item in updated_data if item["text"].strip() and item["expected"].strip())
        st.info(f"当前有 {valid_count} 条有效测试数据用于优化")

    def _get_opt_test_dataset(self):
        data_source = st.session_state.get('cls_opt_data_source', '使用默认数据')

        if data_source == "使用默认数据":
            return get_default_dataset("classification")

        if data_source == "上传CSV文件":
            if st.session_state.get('cls_opt_custom_data'):
                return [
                    {"input": item["text"], "ground_truth": item["expected"]}
                    for item in st.session_state.cls_opt_custom_data
                    if item.get("text", "").strip() and item.get("expected", "").strip()
                ] or get_default_dataset("classification")
            return get_default_dataset("classification")

        if data_source == "手动输入":
            manual_data = [
                item for item in st.session_state.get('cls_opt_manual_data', [])
                if item.get("text", "").strip() and item.get("expected", "").strip()
            ]
            if manual_data:
                return [
                    {"input": item["text"], "ground_truth": item["expected"]}
                    for item in manual_data
                ]
            return get_default_dataset("classification")

        return get_default_dataset("classification")

    def _get_optimization_config(self):
        user_labels = st.session_state.get('user_labels', get_default_value("classification", "labels"))
        if isinstance(user_labels, str):
            labels_input_normalized = user_labels.replace("，", ",")
            user_labels = [label.strip() for label in labels_input_normalized.split(",") if label.strip()]

        user_task_desc = st.session_state.get('user_task_description', get_default_value("classification", "task_description"))
        labels_str = ", ".join(user_labels)
        task_desc = f"{user_task_desc}，判断为{labels_str}"

        test_dataset = self._get_opt_test_dataset()

        return task_desc, "classification", test_dataset, {"labels": user_labels}
    
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
