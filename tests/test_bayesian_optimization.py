"""
贝叶斯优化测试脚本
演示如何用最少的尝试次数找到最优 Prompt
"""

import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer

# 加载环境变量
load_dotenv()

def test_bayesian_optimization():
    """测试贝叶斯优化功能"""
    
    print("\n" + "="*60)
    print("🧐 贝叶斯优化测试")
    print("="*60 + "\n")
    
    # 配置
    api_provider = os.getenv("API_PROVIDER", "nvidia")
    api_key = os.getenv("NVIDIA_API_KEY") if api_provider == "nvidia" else os.getenv("OPENAI_API_KEY")
    model = "meta/llama-3.1-8b-instruct" if api_provider == "nvidia" else "gpt-4o"
    
    if not api_key:
        print("❌ 未找到 API Key，请在 .env 文件中配置")
        return
    
    print(f"✅ API 提供商: {api_provider}")
    print(f"✅ 使用模型: {model}\n")
    
    # 创建优化器
    optimizer = PromptOptimizer(
        api_key=api_key,
        model=model,
        provider=api_provider
    )
    
    # 测试任务配置
    task_description = "对用户评论进行情感分类（积极/消极/中立）"
    task_type = "classification"
    
    # 测试数据集（适度规模）
    test_dataset = [
        {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
        {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
        {"input": "产品质量不错，但是价格有点贵，总体来说还行", "ground_truth": "中立"},
        {"input": "并不是很满意这次购物体验", "ground_truth": "消极"},
        {"input": "不得不说，这次的服务让我很惊喜", "ground_truth": "积极"},
        {"input": "呵呵，真是物超所值啊，买的时候说得天花乱坠，收到货就是个破烂", "ground_truth": "消极"},
    ]
    
    print("📋 测试配置：")
    print(f"  任务类型: {task_type}")
    print(f"  任务描述: {task_description}")
    print(f"  测试样本: {len(test_dataset)} 条")
    print(f"  尝试次数: 15 次")
    print(f"  预计 API 调用: {15 * len(test_dataset)} 次")
    print(f"\n💡 贝叶斯优化会智能选择参数，通常比随机搜索效率高2-3倍\n")
    
    # 生成搜索空间
    print("-" * 60)
    print("步骤 1: 生成搜索空间")
    print("-" * 60)
    
    try:
        search_space = optimizer.generate_search_space(
            task_description=task_description,
            task_type=task_type
        )
        print("✅ 搜索空间生成成功！\n")
        print(f"  角色池: {search_space.roles}")
        print(f"  风格池: {search_space.styles}")
        print(f"  技巧池: {search_space.techniques}\n")
    except Exception as e:
        print(f"❌ 生成搜索空间失败: {e}")
        return
    
    # 执行贝叶斯优化
    print("-" * 60)
    print("步骤 2: 执行贝叶斯优化")
    print("-" * 60)
    
    try:
        all_results, best_result, trial_history = optimizer.run_bayesian_optimization(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            n_trials=8  # 贝叶斯优化通常15-20次就能找到好结果
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("🏆 贝叶斯优化结果")
        print("="*60)
        
        print(f"\n🥇 最终冠军:")
        print(f"  得分: {best_result.avg_score:.2f}%")
        print(f"  角色: {best_result.role}")
        print(f"  风格: {best_result.style}")
        print(f"  技巧: {best_result.technique}")
        
        print(f"\n📜 完整 Prompt:")
        print("-" * 60)
        print(best_result.full_prompt)
        print("-" * 60)
        
        # 分析收敛情况
        print(f"\n📊 收敛分析:")
        best_trial_num = next(i for i, h in enumerate(trial_history, 1) if h['score'] == best_result.avg_score)
        print(f"  - 在第 {best_trial_num} 次试验中找到最佳结果")
        print(f"  - 总共尝试了 {len(trial_history)} 次")
        print(f"  - 收敛效率: {best_trial_num / len(trial_history) * 100:.1f}% 进度时找到最优解")
        
        # 显示得分分布
        scores = [h['score'] for h in trial_history]
        print(f"\n📈 得分统计:")
        print(f"  - 最高分: {max(scores):.2f}")
        print(f"  - 平均分: {sum(scores)/len(scores):.2f}")
        print(f"  - 最低分: {min(scores):.2f}")
        print(f"  - 分数提升: {trial_history[-1]['best_score'] - trial_history[0]['score']:.2f}")
        
        print("\n✅ 测试完成！")
        
        # 对比说明
        print(f"\n💡 效率对比:")
        print(f"  - 随机搜索需要 30-50 次才能找到好结果")
        print(f"  - 贝叶斯优化通常 15-20 次即可")
        print(f"  - 本次在第 {best_trial_num} 次找到最优，节省了约 {(1 - best_trial_num/30) * 100:.0f}% 的成本")
        
    except ImportError as e:
        print(f"\n❌ 错误: {e}")
        print("请先安装 optuna: pip install optuna")
    except Exception as e:
        print(f"❌ 优化过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_bayesian_optimization()
