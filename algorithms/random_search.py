"""
随机搜索算法
通过随机采样搜索空间来寻找最优 Prompt 组合
"""
import time
import random
from config.models import SearchSpace, SearchResult
from metrics import MetricsCalculator


class RandomSearchAlgorithm:
    """随机搜索算法"""
    
    def __init__(self, llm):
        """
        初始化算法
        
        Args:
            llm: LangChain LLM 实例
        """
        self.llm = llm
    
    def run(
        self, 
        task_description: str,
        task_type: str,
        test_dataset: list[dict],
        search_space: SearchSpace,
        iterations: int = 5,
        progress_callback=None,
        labels: list[str] = None
    ) -> tuple[list[SearchResult], SearchResult]:
        """
        执行随机搜索优化
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{'input': '...', 'ground_truth': '...'}]
            search_space: 搜索空间
            iterations: 搜索迭代次数
            progress_callback: 进度回调函数 callback(current, total, message)
            labels: 分类任务的标签列表（仅分类任务需要）
            
        Returns:
            (所有结果列表, 最佳结果)
        """
        results_log = []
        calc = MetricsCalculator()

        # 预生成所有组合，确保不重复
        all_combinations = [
            (role, style, tech)
            for role in search_space.roles
            for style in search_space.styles
            for tech in search_space.techniques
        ]
        total_combinations = len(all_combinations)
        if total_combinations == 0:
            raise ValueError("搜索空间为空，无法进行随机搜索。")

        if iterations > total_combinations:
            print(f"⚠️ 迭代次数 {iterations} 超过搜索空间组合数 {total_combinations}，将自动调整为 {total_combinations} 次以避免重复。")
            iterations = total_combinations

        random.shuffle(all_combinations)
        
        print(f"\n{'='*60}")
        print(f"开始随机搜索优化 - {iterations} 次迭代")
        print(f"{'='*60}\n")
        
        for i in range(iterations):
            # 1. 随机采样：无重复组合
            chosen_role, chosen_style, chosen_tech = all_combinations[i]
            
            print(f"迭代 {i+1}/{iterations}")
            print(f"  角色: {chosen_role}")
            print(f"  风格: {chosen_style}")
            print(f"  技巧: {chosen_tech}")
            
            # 2. 拼装候选 Prompt
            candidate_prompt = self._build_prompt(
                task_type, task_description, chosen_role, chosen_style, chosen_tech, labels
            )
            
            # 3. 在测试集上跑分
            scores = []
            for case_idx, case in enumerate(test_dataset):
                try:
                    print(f"\n  📝 测试样本 {case_idx+1}/{len(test_dataset)}")
                    print(f"    输入: {case['input'][:50]}..." if len(case['input']) > 50 else f"    输入: {case['input']}")
                    print(f"    标准答案: {case['ground_truth']}")
                    
                    # 替换占位符
                    prompt_filled = self._fill_prompt(candidate_prompt, case['input'], task_type)
                    
                    # 调用 LLM
                    print(f"    🤖 调用 LLM...")
                    response = self.llm.invoke(prompt_filled)
                    time.sleep(0.3)  # API 调用延迟
                    prediction = response.content.strip()
                    print(f"    💬 LLM 输出: {prediction[:80]}..." if len(prediction) > 80 else f"    💬 LLM 输出: {prediction}")
                    
                    # 计算分数
                    score = self._calculate_score(prediction, case['ground_truth'], task_type, calc)
                    scores.append(score)
                    print(f"    ✅ 得分: {score:.1f}")
                    
                except Exception as e:
                    print(f"    ❌ 评估失败！")
                    print(f"    错误类型: {type(e).__name__}")
                    print(f"    错误信息: {e}")
                    scores.append(0.0)
            
            # 计算平均分
            avg_score = sum(scores) / len(scores) if scores else 0.0
            print(f"  平均得分: {avg_score:.2f}\n")
            
            # 4. 记录结果
            result = SearchResult(
                iteration_id=i+1,
                role=chosen_role,
                style=chosen_style,
                technique=chosen_tech,
                full_prompt=candidate_prompt,
                avg_score=avg_score,
                task_type=task_type
            )
            results_log.append(result)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i+1, iterations, f"完成迭代 {i+1}/{iterations}，得分: {avg_score:.2f}")
        
        # 找出最佳结果
        best_result = max(results_log, key=lambda x: x.avg_score)
        
        print(f"{'='*60}")
        print(f"搜索完成！最佳得分: {best_result.avg_score:.2f}")
        print(f"最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"{'='*60}\n")
        
        return results_log, best_result
    
    def _build_prompt(self, task_type: str, task_description: str, 
                     role: str, style: str, technique: str, labels: list[str] = None) -> str:
        """构建候选 Prompt"""
        if task_type == "classification":
            # 动态生成标签列表
            if labels:
                labels_str = ", ".join(labels)
                output_instruction = f"只输出以下标签之一：{labels_str}。不要额外解释。"
            else:
                output_instruction = "只输出分类标签，不要额外解释。"
                
            return f"""你是一位{role}。

任务：{task_description}

风格要求：{style}

指令：{technique}

请对以下文本进行分类：
[待分类文本]

{output_instruction}
"""
        elif task_type == "summarization":
            return f"""你是一位{role}。

任务：{task_description}

风格要求：{style}

指令：{technique}

请对以下文本进行摘要：
[待摘要文本]

请按照要求输出摘要。
"""
        elif task_type == "translation":
            return f"""你是一位{role}。

任务：{task_description}

风格要求：{style}

指令：{technique}

请翻译以下文本：
[待翻译文本]

只输出翻译结果，不要额外说明。
"""
        else:
            return f"""角色: {role}
风格: {style}
任务: {task_description}
指令: {technique}

输入: {{input}}
"""
    
    def _fill_prompt(self, prompt: str, input_text: str, task_type: str) -> str:
        """填充 Prompt 中的占位符"""
        if task_type == "classification":
            return prompt.replace("[待分类文本]", input_text)
        elif task_type == "summarization":
            return prompt.replace("[待摘要文本]", input_text)
        elif task_type == "translation":
            return prompt.replace("[待翻译文本]", input_text)
        else:
            return prompt.replace("{{input}}", input_text)
    
    def _calculate_score(self, prediction: str, ground_truth: str, 
                        task_type: str, calc: MetricsCalculator) -> float:
        """计算预测结果的分数"""
        if task_type == "classification":
            # 分类任务：简单匹配
            score = 100.0 if prediction == ground_truth else 0.0
            print(f"    📊 匹配结果: {'✅ 正确' if score == 100.0 else '❌ 错误'}")
            return score
        elif task_type == "summarization":
            # 摘要任务：ROUGE
            print(f"    📊 计算 ROUGE 分数...")
            rouge_scores = calc.calculate_rouge(prediction, ground_truth)
            score = rouge_scores['rouge1']
            print(f"    📊 ROUGE-1: {score:.2f}")
            return score
        elif task_type == "translation":
            # 翻译任务：BLEU
            print(f"    📊 计算 BLEU 分数...")
            score = calc.calculate_bleu(prediction, ground_truth)
            print(f"    📊 BLEU: {score:.2f}")
            return score
        else:
            return 50.0  # 默认分数
