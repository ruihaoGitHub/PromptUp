"""
贝叶斯优化模块
使用概率模型智能优化 Prompt 组合
"""
import time
import random
from typing import Optional, Callable
from config.models import SearchSpace, SearchResult
from metrics import MetricsCalculator

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False


class BayesianOptimization:
    """贝叶斯优化器"""
    
    def __init__(self, llm):
        """
        初始化贝叶斯优化
        
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
        n_trials: int = 20,
        progress_callback: Optional[Callable] = None
    ) -> tuple[list, SearchResult, list]:
        """
        贝叶斯优化 Prompt
        
        核心思想：利用概率模型（TPE）智能选择下一个尝试的参数组合，
        用最少的尝试次数找到最优解，比随机搜索效率高得多。
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            test_dataset: 测试数据集 [{"input": "...", "ground_truth": "..."}, ...]
            search_space: 搜索空间
            n_trials: 尝试次数（贝叶斯优化通常20-50次就能找到好结果）
            progress_callback: 进度回调函数 callback(trial, total_trials, best_score)
        
        Returns:
            (all_results, best_result, trial_history)
            - all_results: 所有试验的结果
            - best_result: 最佳结果
            - trial_history: 试验历史 [{"trial": 1, "score": 85.0, "params": {...}}, ...]
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError("贝叶斯优化需要 optuna 库。请运行: pip install optuna")

        # 预生成所有组合（用于去重 + 冷启动随机探索）
        all_combinations = [
            (role, style, tech)
            for role in search_space.roles
            for style in search_space.styles
            for tech in search_space.techniques
        ]
        if not all_combinations:
            raise ValueError("搜索空间为空，无法运行贝叶斯优化。")

        # 初始随机探索次数：按 n_trials 比例计算（避免 n_trials=5 仍固定探索5次）
        warmup_ratio = 0.25
        warmup_trials = int(round(n_trials * warmup_ratio))
        warmup_trials = max(1, min(n_trials, warmup_trials))
        
        print(f"\n{'='*60}")
        print("🧐 贝叶斯优化开始")
        print(f"{'='*60}")
        print(f"📋 任务类型: {task_type}")
        print("🔬 使用算法: TPE (Tree-structured Parzen Estimator)")
        print(f"🎯 尝试次数: {n_trials}")
        print(f"🌱 初始随机探索: {warmup_trials} 次（{warmup_ratio:.0%}）")
        print(f"📏 测试集样本数: {len(test_dataset)}")
        print(f"💰 预计 API 调用: {n_trials * len(test_dataset)} 次")
        print("💡 贝叶斯优化会根据历史结果智能选择下一个参数组合")
        print(f"{'='*60}\n")
        
        all_results = []
        trial_history = []
        best_score_so_far = 0.0

        # 组合级去重：同一个 (role, style, technique) 只评估一次
        used_combo_keys: set[str] = set()

        def _combo_key(role: str, style: str, technique: str) -> str:
            return f"{role}|||{style}|||{technique}"

        combo_keys = [_combo_key(r, s, t) for (r, s, t) in all_combinations]
        
        def objective(trial):
            """Optuna 的目标函数"""
            nonlocal best_score_so_far

            # 让 Optuna 选择一个不重复的组合（组合级 categorical）
            combo = trial.suggest_categorical('combo', combo_keys)
            if combo in used_combo_keys:
                print("  🔁 去重: 组合已评估，跳过该试验")
                raise optuna.TrialPruned()
            used_combo_keys.add(combo)

            role, style, technique = combo.split("|||", 2)
            
            print(f"\n{'='*60}")
            print(f"🔍 试验 {trial.number + 1}/{n_trials}")
            print(f"{'='*60}")
            
            # 显示策略提示
            if trial.number < warmup_trials:
                print("  📍 策略: 随机探索（冷启动）")
            else:
                print("  📍 策略: TPE 智能选择（利用历史结果）")
            
            print(f"  参数组合: {role} + {style} + {technique}")
            
            # 构建 Prompt
            if task_type == "classification":
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出分类标签（如：积极、消极、中立），不要输出任何解释、分析或其他内容。**

输入：{{{{text}}}}
输出（只输出标签）："""
            elif task_type == "translation":
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出翻译后的文本，不要输出解释、分析、步骤、标题或任何多余内容。**

输入：{{{{text}}}}
输出（只输出译文）："""
            elif task_type == "summarization":
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

**重要：你必须只输出摘要正文，不要输出解释、分析、步骤、标题或任何多余内容。**

输入：{{{{text}}}}
输出（只输出摘要）："""
            else:
                prompt_template = f"""你是一位{role}。

请以{style}的风格完成以下任务：
{task_description}

策略提示：{technique}

输入：{{{{text}}}}
"""
            
            # 在测试集上评估
            predictions = []
            ground_truths = []
            
            for idx, sample in enumerate(test_dataset, 1):
                test_input = sample.get("input", "")
                ground_truth = sample.get("ground_truth", "")
                
                final_prompt = prompt_template.replace("{{text}}", test_input)
                
                # 显示当前进度
                print(f"    📝 评估样本 {idx}/{len(test_dataset)}...", end="", flush=True)
                
                # 调用 LLM（带重试机制）
                prediction = ""
                max_retries = 3
                retry_delay = 2.0
                
                for retry in range(max_retries):
                    try:
                        response = self.llm.invoke(final_prompt)
                        time.sleep(1.2)  # 增加延迟到 1.2s
                        prediction = response.content.strip()
                        print(" ✓")  # 成功标记
                        break
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "Too Many Requests" in error_msg:
                            if retry < max_retries - 1:
                                wait_time = retry_delay * (2 ** retry)
                                print(f" ⚠️ 限流，等待 {wait_time:.0f}s...")
                                time.sleep(wait_time)
                                continue
                            else:
                                print(" ✗ (达到重试上限)")
                                prediction = ""
                                break
                        else:
                            print(f" ✗ ({str(e)[:30]})")
                            prediction = ""
                            break
                
                # 清理预测结果
                if prediction and task_type == "classification":
                    prediction = prediction.split('\n')[0].strip()
                    for prefix in ["输出：", "输出:", "结果：", "结果:", "分类：", "分类:", "标签：", "标签:"]:
                        if prediction.startswith(prefix):
                            prediction = prediction[len(prefix):].strip()
                    if len(prediction) > 10:
                        for label in ["积极", "消极", "中立", "正面", "负面", "中性"]:
                            if label in prediction:
                                prediction = label
                                break
                
                predictions.append(prediction)
                ground_truths.append(ground_truth)
            
            # 计算分数
            calc = MetricsCalculator()
            valid_pairs = [(p, g) for p, g in zip(predictions, ground_truths) if p]
            
            if not valid_pairs:
                score = 0.0
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
            
            # 记录结果
            result = SearchResult(
                iteration_id=trial.number + 1,
                role=role,
                style=style,
                technique=technique,
                full_prompt=prompt_template,
                avg_score=score,
                task_type=task_type
            )
            all_results.append(result)
            
            # 更新最佳分数
            if score > best_score_so_far:
                best_score_so_far = score
                print(f"  → 得分: {score:.2f} 🎉 新纪录！")
            else:
                print(f"  → 得分: {score:.2f}")
            
            # 记录试验历史
            trial_history.append({
                "trial": trial.number + 1,
                "score": score,
                "best_score": best_score_so_far,
                "role": role,
                "style": style,
                "technique": technique
            })
            
            # 进度回调
            if progress_callback:
                progress_callback(trial.number + 1, n_trials, best_score_so_far)
            
            # 试验间增加延迟，避免连续调用触发限流
            if trial.number < n_trials - 1:  # 不是最后一次
                print("  ⏸️  试验间冷却 2秒...")
                time.sleep(2.0)
            
            return score
        
        # 创建 Optuna Study（优化 TPE 参数）
        # 说明：这里使用 n_startup_trials 控制“初始随机探索”轮数。
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(
            direction="maximize",
            sampler=optuna.samplers.TPESampler(
                n_startup_trials=warmup_trials,
                n_ei_candidates=24,
                multivariate=False,
                warn_independent_sampling=False,
                seed=None,
            ),
        )

        # 冷启动：预先 enqueue 不重复的随机组合，确保前 warmup_trials 次确实是“随机且不重复”
        warmup_seeds = random.sample(combo_keys, k=min(warmup_trials, len(combo_keys)))
        for combo in warmup_seeds:
            study.enqueue_trial({"combo": combo})
        
        # 执行优化
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        # 获取最佳结果
        best_trial = study.best_trial
        best_combo = best_trial.params.get("combo")
        if not best_combo:
            raise RuntimeError("未找到最佳试验的 combo 参数，无法定位最佳结果。")
        best_role, best_style, best_technique = best_combo.split("|||", 2)
        best_result = next(
            r
            for r in all_results
            if r.role == best_role and r.style == best_style and r.technique == best_technique
        )
        
        print(f"\n{'='*60}")
        print("🏆 贝叶斯优化完成！")
        print(f"{'='*60}")
        print(f"🥇 最佳得分: {best_result.avg_score:.2f}")
        print(f"🧬 最佳组合: {best_result.role} + {best_result.style} + {best_result.technique}")
        print(f"📊 收敛速度: 在第 {best_trial.number + 1} 次试验中找到最佳结果")
        
        # 分析优化效果（注意：去重可能导致部分 trial 被 pruned，因此历史长度可能 < n_trials）
        scores = [h['score'] for h in trial_history]
        if not scores:
            raise RuntimeError("所有试验均未产生有效评分（可能全部被 pruned 或评估失败）。")

        first_k = min(warmup_trials, len(scores))
        last_k = min(5, len(scores))
        first_avg = sum(scores[:first_k]) / first_k
        last_avg = sum(scores[-last_k:]) / last_k
        
        print("\n📈 优化分析:")
        print(f"  冷启动前{first_k}次平均: {first_avg:.2f}")
        print(f"  最近{last_k}次平均: {last_avg:.2f}")
        if last_avg >= first_avg:
            print(f"  ✅ 后期表现提升 {last_avg - first_avg:.2f} 分（智能优化生效）")
        else:
            print("  ⚠️ 后期探索其他区域（防止陷入局部最优）")
        
        print(f"{'='*60}\n")
        
        return all_results, best_result, trial_history
