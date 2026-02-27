"""
遗传算法优化模块
使用进化思想优化 Prompt 组合
"""
import time
import random
import re
from typing import Optional, Callable
from config.models import SearchSpace, SearchResult
from metrics import MetricsCalculator


class GeneticAlgorithm:
    """遗传算法优化器"""
    
    def __init__(self, llm):
        """
        初始化遗传算法
        
        Args:
            llm: LLM 实例
        """
        self.llm = llm
    
    def run(
        self,
        task_description: str,
        task_type: str,
        test_dataset: list,
        search_space: SearchSpace,
        generations: int = 5,
        population_size: int = 8,
        elite_ratio: float = 0.2,
        mutation_rate: float = 0.2,
        progress_callback: Optional[Callable] = None
    ) -> tuple[list, SearchResult, list]:
        """
        遗传算法优化 Prompt
        
        核心思想：通过多代进化，让优秀的 Prompt 组合"繁衍"出更好的后代
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{"input": "...", "ground_truth": "..."}, ...]
            search_space: 搜索空间
            generations: 进化代数（越多越好，但消耗更大）
            population_size: 种群规模（每代有多少个个体）
            elite_ratio: 精英保留比例（保留多少优秀个体到下一代）
            mutation_rate: 变异概率（引入随机性避免局部最优）
            progress_callback: 进度回调函数 callback(gen, total_gen, best_score, avg_score)
        
        Returns:
            (all_results, best_result, evolution_history)
            - all_results: 所有迭代的结果
            - best_result: 最佳结果
            - evolution_history: 进化历史 [{"generation": 1, "best_score": 85.0, "avg_score": 78.5}, ...]
        """
        print(f"\n{'='*60}")
        print("🧬 遗传算法优化开始")
        print(f"{'='*60}")
        print(f"📋 任务类型: {task_type}")
        print(f"📊 代数: {generations}, 种群规模: {population_size}")
        print(f"🔬 精英比例: {elite_ratio * 100}%, 变异率: {mutation_rate * 100}%")
        print(f"📏 测试集样本数: {len(test_dataset)}")
        print(f"💰 预计 API 调用: {generations * population_size * len(test_dataset)} 次")
        print(f"{'='*60}\n")
        
        # 预生成所有组合，确保不重复
        all_combinations = [
            (role, style, tech)
            for role in search_space.roles
            for style in search_space.styles
            for tech in search_space.techniques
        ]
        total_combinations = len(all_combinations)
        if total_combinations == 0:
            raise ValueError("搜索空间为空，无法运行遗传算法。")
        if population_size > total_combinations:
            raise ValueError(f"种群规模 {population_size} 超过搜索空间组合数 {total_combinations}，无法保证不重复。")

        max_generations = total_combinations // population_size
        if max_generations == 0:
            raise ValueError("搜索空间组合数不足以生成完整一代种群。")
        if generations > max_generations:
            print(f"⚠️ 代数 {generations} 超过可用不重复代数 {max_generations}，已自动调整。")
            generations = max_generations

        remaining_combinations = set(all_combinations)

        def _reserve_unique_combo(preferred_combo=None):
            if preferred_combo and preferred_combo in remaining_combinations:
                remaining_combinations.remove(preferred_combo)
                return preferred_combo
            if not remaining_combinations:
                raise RuntimeError("搜索空间组合已耗尽，无法生成不重复的个体。")
            combo = random.choice(list(remaining_combinations))
            remaining_combinations.remove(combo)
            return combo

        def _finalize_unique_combo(individual):
            preferred_combo = (individual["role"], individual["style"], individual["technique"])
            role, style, technique = _reserve_unique_combo(preferred_combo)
            if (role, style, technique) != preferred_combo:
                print("    🔁 去重: 组合已使用，替换为新组合")
            individual["role"], individual["style"], individual["technique"] = role, style, technique
            return individual

        def create_individual():
            """创建一个随机个体（Prompt 组合）"""
            role, style, technique = _reserve_unique_combo()
            return {
                "role": role,
                "style": style,
                "technique": technique,
                "score": 0.0,
                "full_prompt": ""
            }
        
        def evaluate_individual(individual, generation: int, index: int):
            """评估个体的适应度（在测试集上的得分）"""
            def _normalize_space(value: str) -> str:
                return re.sub(r"\s+", " ", str(value)).strip()

            role = _normalize_space(individual["role"])
            style = _normalize_space(individual["style"])
            technique = _normalize_space(individual["technique"])
            individual["role"] = role
            individual["style"] = style
            individual["technique"] = technique

            label_candidates = []
            if task_type == "classification":
                label_candidates = list({
                    str(sample.get("ground_truth", "")).strip()
                    for sample in test_dataset
                    if str(sample.get("ground_truth", "")).strip()
                })
            
            # 构建 Prompt（根据任务类型优化输出格式）
            if task_type == "classification":
                # 分类任务：强制要求只输出标签
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出分类标签（如：积极、消极、中立），不要输出任何解释、分析或其他内容。**

输入：{{{{text}}}}
输出（只输出标签）："""
            elif task_type == "translation":
                # 翻译任务：强制只输出译文，避免解释/标题干扰 BLEU
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出翻译后的文本，不要输出解释、分析、步骤、标题或任何多余内容。**

输入：{{{{text}}}}
输出（只输出译文）："""
            elif task_type == "summarization":
                # 摘要任务：强制只输出摘要正文，减少格式噪音
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出摘要正文，不要输出解释、分析、步骤、标题或任何多余内容。**

输入：{{{{text}}}}
输出（只输出摘要）："""
            else:
                # 其他任务：常规格式
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

输入：{{{{text}}}}
"""
            
            individual["full_prompt"] = prompt_template
            
            # 在测试集上评估
            predictions = []
            ground_truths = []
            
            print(f"  第 {generation} 代个体 {index}:")
            print(f"    🎭 角色: {role}")
            print(f"    🎨 风格: {style}")
            print(f"    🧠 技巧: {technique}")
            
            for idx, sample in enumerate(test_dataset, 1):
                test_input = sample.get("input", "")
                ground_truth = sample.get("ground_truth", "")
                
                # 替换占位符
                final_prompt = prompt_template.replace("{{text}}", test_input)
                
                # 调用 LLM（带重试机制）
                prediction = ""
                max_retries = 5
                retry_delay = 2.0
                
                for retry in range(max_retries):
                    try:
                        response = self.llm.invoke(final_prompt)
                        if not getattr(self.llm, "is_mock", False):
                            time.sleep(1.0)  # API 调用延迟，遗传算法密集调用需要更长延迟
                        prediction = response.content.strip()
                        break  # 成功则跳出重试循环
                        
                    except Exception as e:
                        error_msg = str(e)
                        is_rate_limit = "429" in error_msg or "Too Many Requests" in error_msg
                        is_network_issue = any(
                            key in error_msg
                            for key in [
                                "HTTPSConnectionPool",
                                "ConnectionError",
                                "Read timed out",
                                "ConnectTimeout",
                                "Max retries exceeded"
                            ]
                        )

                        if is_rate_limit or is_network_issue:
                            if retry < max_retries - 1:
                                wait_time = retry_delay * (2 ** retry)  # 指数退避: 2s, 4s, 8s
                                if is_rate_limit:
                                    print(f"    ⚠️ 样本 {idx} 请求过快，等待 {wait_time:.0f}s 后重试（第{retry+1}次）...")
                                else:
                                    print(f"    ⚠️ 样本 {idx} 网络异常，等待 {wait_time:.0f}s 后重试（第{retry+1}次）...")
                                if not getattr(self.llm, "is_mock", False):
                                    time.sleep(wait_time)
                                continue
                            else:
                                print(f"    ❌ 样本 {idx} 达到最大重试次数，跳过")
                                prediction = ""
                                break
                        else:
                            print(f"    ❌ 样本 {idx} 评估失败: {error_msg[:50]}")
                            prediction = ""
                            break
                
                # 清理预测结果
                if prediction and task_type == "classification":
                    # 取第一行
                    prediction = prediction.split('\n')[0].strip()
                    # 移除常见的前缀词
                    for prefix in ["输出：", "输出:", "结果：", "结果:", "分类：", "分类:", "标签：", "标签:"]:
                        if prediction.startswith(prefix):
                            prediction = prediction[len(prefix):].strip()
                    # 如果包含多个词，尝试提取关键标签
                    if label_candidates and prediction not in label_candidates:
                        for label in label_candidates:
                            if label and label in prediction:
                                prediction = label
                                break
                    if len(prediction) > 10 and (not label_candidates or prediction not in label_candidates):
                        # 兜底：尝试在句子中查找常见情感标签关键词
                        for label in ["积极", "消极", "中立", "正面", "负面", "中性"]:
                            if label in prediction:
                                prediction = label
                                break
                
                predictions.append(prediction)
                ground_truths.append(ground_truth)
                
                # 调试输出：显示预测和真实值
                if generation == 1 and index == 1 and idx <= 2:  # 只显示第一代第一个体的前2个样本
                    print(f"      [调试] 样本{idx} 预测='{prediction}' vs 真实='{ground_truth}'")
            
            # 计算分数
            calc = MetricsCalculator()
            
            # 过滤掉空预测（评估失败的样本）
            valid_pairs = [(p, g) for p, g in zip(predictions, ground_truths) if p]
            
            if not valid_pairs:
                # 所有样本都失败了
                score = 0.0
                print("    → 得分: 0.00 (所有样本评估失败)")
            else:
                valid_predictions = [p for p, g in valid_pairs]
                valid_ground_truths = [g for p, g in valid_pairs]
                
                if task_type == "classification":
                    score = calc.calculate_accuracy(valid_predictions, valid_ground_truths)
                elif task_type == "summarization":
                    scores = [calc.calculate_rouge(p, g)['rougeL'] for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                elif task_type == "translation":
                    scores = [calc.calculate_bleu(p, g) for p, g in valid_pairs]
                    score = sum(scores) / len(scores) if scores else 0
                else:
                    score = 0.0
                
                # 如果部分样本失败，显示成功率
                failed_count = len(predictions) - len(valid_pairs)
                if failed_count > 0:
                    print(f"    → 得分: {score:.2f} ({len(valid_pairs)}/{len(predictions)} 样本成功)")
                else:
                    print(f"    → 得分: {score:.2f}")
            
            individual["score"] = score
            
            # 如果得分为0且有成功的样本，显示调试信息
            if score == 0.0 and valid_pairs:
                print(f"      [0分调试] 预测='{valid_predictions[0][:50]}' vs 真实='{valid_ground_truths[0]}'")
            
            return individual
        
        def crossover(parent1, parent2):
            """交叉：孩子继承父母的优良基因"""
            return {
                "role": random.choice([parent1["role"], parent2["role"]]),
                "style": random.choice([parent1["style"], parent2["style"]]),
                "technique": random.choice([parent1["technique"], parent2["technique"]]),
                "score": 0.0,
                "full_prompt": ""
            }
        
        def mutate(individual):
            """变异：随机改变某些基因，引入新可能性"""
            if random.random() < mutation_rate:
                individual["role"] = random.choice(search_space.roles)
                print(f"    🔀 变异: 更换角色 → {individual['role']}")
            if random.random() < mutation_rate:
                individual["style"] = random.choice(search_space.styles)
                print(f"    🔀 变异: 更换风格 → {individual['style']}")
            if random.random() < mutation_rate:
                individual["technique"] = random.choice(search_space.techniques)
                print(f"    🔀 变异: 更换技巧 → {individual['technique']}")
            return individual
        
        # === 遗传算法主循环 ===
        
        # 初始化第一代种群
        print(f"🧬 第 1 代：初始化种群（{population_size} 个个体）")
        population = [create_individual() for _ in range(population_size)]
        
        evolution_history = []
        all_results = []
        
        for gen in range(generations):
            print(f"\n{'='*60}")
            print(f"🧬 第 {gen + 1}/{generations} 代进化")
            print(f"{'='*60}")
            
            # 评估当前种群
            for i, individual in enumerate(population, 1):
                evaluate_individual(individual, gen + 1, i)
            
            # 按适应度排序
            population.sort(key=lambda x: x["score"], reverse=True)
            
            # 记录历史
            best_score = population[0]["score"]
            avg_score = sum(ind["score"] for ind in population) / len(population)
            
            evolution_history.append({
                "generation": gen + 1,
                "best_score": best_score,
                "avg_score": avg_score,
                "worst_score": population[-1]["score"]
            })
            
            print(f"\n📊 第 {gen + 1} 代统计:")
            print(f"  🥇 最高分: {best_score:.2f}")
            print(f"  📊 平均分: {avg_score:.2f}")
            print(f"  📉 最低分: {population[-1]['score']:.2f}")
            print(f"  🏆 冠军: {population[0]['role']} + {population[0]['style']} + {population[0]['technique']}")
            
            # 保存所有结果
            for i, ind in enumerate(population):
                result = SearchResult(
                    iteration_id=gen * population_size + i + 1,
                    role=ind["role"],
                    style=ind["style"],
                    technique=ind["technique"],
                    full_prompt=ind["full_prompt"],
                    avg_score=ind["score"],
                    task_type=task_type
                )
                all_results.append(result)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(gen + 1, generations, best_score, avg_score)
            
            # 如果是最后一代，跳过繁衍
            if gen == generations - 1:
                break
            
            # 选择（精英策略）：去重模式下精英用于父代选择，不直接保留
            elite_count = max(1, int(population_size * elite_ratio))
            print("\n🧬 选择: 精英用于父代选择（去重模式不保留到下一代）")
            new_population = []
            
            # 繁衍（交叉 + 变异）
            print(f"🧬 繁衍: 生成 {population_size} 个新个体")
            while len(new_population) < population_size:
                # 从已排序种群前 elite_count 名中选择父代（分数由高到低排列）
                parent_pool_size = max(2, elite_count)
                parent1 = random.choice(population[:parent_pool_size])
                parent2 = random.choice(population[:parent_pool_size])
                
                # 交叉
                child = crossover(parent1, parent2)
                
                # 变异
                child = mutate(child)

                # 去重并占用组合
                child = _finalize_unique_combo(child)
                
                new_population.append(child)
            
            population = new_population
        
        # 最终结果
        best_result = max(all_results, key=lambda x: x.avg_score)
        
        print(f"\n{'='*60}")
        print("🏆 遗传算法完成！")
        print(f"{'='*60}")
        print(f"🥇 最终冠军得分: {best_result.avg_score:.2f}")
        print(f"🧬 最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"📈 进化增益: {evolution_history[-1]['best_score'] - evolution_history[0]['best_score']:.2f} 分")
        print(f"{'='*60}\n")
        
        return all_results, best_result, evolution_history
