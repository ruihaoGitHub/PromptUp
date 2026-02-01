"""
随机搜索 vs 遗传算法对比测试
直观展示两种算法的差异
"""

import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer
import matplotlib.pyplot as plt
import matplotlib

# 加载环境变量
load_dotenv()

def compare_algorithms():
    """对比测试：随机搜索 vs 遗传算法"""
    
    print("\n" + "="*60)
    print("🔬 算法对比实验：随机搜索 vs 遗传算法")
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
    
    # 测试任务（使用困难数据集）
    task_description = "对用户评论进行情感分类（积极/消极/中立）"
    task_type = "classification"
    
    test_dataset = [
        {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
        {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
        {"input": "产品质量不错，但是价格有点贵，总体来说还行", "ground_truth": "中立"},
        {"input": "哇，真是太'棒'了，收到就坏了，非常'满意'呢", "ground_truth": "消极"},
    ]
    
    print("📋 实验配置：")
    print(f"  任务: {task_description}")
    print(f"  测试样本: {len(test_dataset)} 条（包含反讽等困难案例）")
    print(f"  迭代次数: 5 次")
    print(f"\n💡 相同的测试条件，看哪个算法表现更好！\n")
    
    # 生成搜索空间
    print("-" * 60)
    print("生成搜索空间...")
    print("-" * 60)
    
    try:
        search_space = optimizer.generate_search_space(
            task_description=task_description,
            task_type=task_type
        )
        print("✅ 搜索空间生成成功！\n")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return
    
    # ===== 实验 1: 随机搜索 =====
    print("\n" + "="*60)
    print("🎲 实验 1: 随机搜索")
    print("="*60 + "\n")
    
    try:
        random_results, random_best = optimizer.run_random_search(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            iterations=5
        )
        
        print(f"\n🏆 随机搜索最佳结果:")
        print(f"  得分: {random_best.avg_score:.2f}")
        print(f"  组合: {random_best.role} + {random_best.style} + {random_best.technique}")
        
        # 收集分数
        random_scores = [r.avg_score for r in random_results]
        
    except Exception as e:
        print(f"❌ 随机搜索失败: {e}")
        return
    
    # ===== 实验 2: 遗传算法 =====
    print("\n" + "="*60)
    print("🧬 实验 2: 遗传算法")
    print("="*60 + "\n")
    
    try:
        ga_results, ga_best, ga_history = optimizer.run_genetic_algorithm(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            generations=5,
            population_size=5,
            elite_ratio=0.2,
            mutation_rate=0.2
        )
        
        print(f"\n🏆 遗传算法最佳结果:")
        print(f"  得分: {ga_best.avg_score:.2f}")
        print(f"  组合: {ga_best.role} + {ga_best.style} + {ga_best.technique}")
        print(f"  进化增益: {ga_history[-1]['best_score'] - ga_history[0]['best_score']:+.2f} 分")
        
    except Exception as e:
        print(f"❌ 遗传算法失败: {e}")
        return
    
    # ===== 对比分析 =====
    print("\n" + "="*60)
    print("📊 对比分析")
    print("="*60 + "\n")
    
    print(f"{'指标':<20}{'🎲 随机搜索':<20}{'🧬 遗传算法':<20}{'胜者'}")
    print("-" * 70)
    
    # 最高分
    winner1 = "🧬 遗传算法" if ga_best.avg_score > random_best.avg_score else "🎲 随机搜索" if random_best.avg_score > ga_best.avg_score else "➡️ 平局"
    print(f"{'最高分':<20}{random_best.avg_score:<20.2f}{ga_best.avg_score:<20.2f}{winner1}")
    
    # 平均分
    random_avg = sum(random_scores) / len(random_scores)
    ga_avg = sum([h['avg_score'] for h in ga_history]) / len(ga_history)
    winner2 = "🧬 遗传算法" if ga_avg > random_avg else "🎲 随机搜索" if random_avg > ga_avg else "➡️ 平局"
    print(f"{'平均分':<20}{random_avg:<20.2f}{ga_avg:<20.2f}{winner2}")
    
    # 最低分
    random_min = min(random_scores)
    ga_min = min([h['worst_score'] for h in ga_history])
    winner3 = "🧬 遗传算法" if ga_min > random_min else "🎲 随机搜索" if random_min > ga_min else "➡️ 平局"
    print(f"{'最低分':<20}{random_min:<20.2f}{ga_min:<20.2f}{winner3}")
    
    # 稳定性（标准差）
    import numpy as np
    random_std = np.std(random_scores)
    ga_best_scores = [h['best_score'] for h in ga_history]
    ga_std = np.std(ga_best_scores)
    winner4 = "🧬 遗传算法" if ga_std < random_std else "🎲 随机搜索" if random_std < ga_std else "➡️ 平局"
    print(f"{'波动性(标准差)':<20}{random_std:<20.2f}{ga_std:<20.2f}{winner4} (越小越稳定)")
    
    print("\n" + "="*60)
    print("结论:")
    print("="*60)
    
    if ga_best.avg_score > random_best.avg_score:
        diff = ga_best.avg_score - random_best.avg_score
        print(f"🏆 遗传算法胜出！最高分比随机搜索高 {diff:.2f} 分")
        print(f"✅ 遗传算法通过进化机制，能够持续改进 Prompt 质量")
    elif random_best.avg_score > ga_best.avg_score:
        diff = random_best.avg_score - ga_best.avg_score
        print(f"🏆 随机搜索胜出！最高分比遗传算法高 {diff:.2f} 分")
        print(f"✅ 随机搜索运气好，但不保证稳定性")
    else:
        print(f"➡️ 两种算法得分相同！")
    
    if ga_std < random_std:
        print(f"✅ 遗传算法波动更小，更稳定可靠")
    
    # 可视化对比
    print("\n📊 生成对比图表...")
    
    # 设置中文字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左图：随机搜索
    ax1.plot(range(1, len(random_scores) + 1), random_scores, 
             marker='o', linewidth=2, markersize=8, color='#3498db')
    ax1.axhline(y=random_best.avg_score, color='r', linestyle='--', 
                linewidth=2, label=f'最佳: {random_best.avg_score:.2f}')
    ax1.set_xlabel('迭代次数')
    ax1.set_ylabel('得分')
    ax1.set_title('🎲 随机搜索 - 随机波动')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 105])
    
    # 右图：遗传算法
    generations = [h['generation'] for h in ga_history]
    best_scores = [h['best_score'] for h in ga_history]
    avg_scores = [h['avg_score'] for h in ga_history]
    
    ax2.plot(generations, best_scores, marker='o', linewidth=2, markersize=8, 
             label='最高分', color='#2ecc71')
    ax2.plot(generations, avg_scores, marker='s', linewidth=2, markersize=6, 
             label='平均分', color='#3498db')
    ax2.set_xlabel('代数')
    ax2.set_ylabel('得分')
    ax2.set_title('🧬 遗传算法 - 持续进化')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 105])
    
    plt.tight_layout()
    
    # 保存图表
    output_file = "algorithm_comparison.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ 图表已保存到: {output_file}")
    
    plt.show()
    
    print("\n✅ 对比测试完成！")
    print("\n💡 **关键发现**:")
    print("   - 随机搜索：像买彩票，靠运气")
    print("   - 遗传算法：像训练运动员，越练越强")
    print("   - 推荐策略：先随机搜索快速探索，再遗传算法精细打磨")


if __name__ == "__main__":
    compare_algorithms()
