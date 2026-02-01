"""
遗传算法测试脚本
演示遗传算法如何通过多代进化找到更好的 Prompt
"""

import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer

# 加载环境变量
load_dotenv()

def test_genetic_algorithm():
    """测试遗传算法功能"""
    
    print("\n" + "="*60)
    print("🧬 遗传算法测试")
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
    
    # 增强测试数据集（更多样本 + 更高难度）
    test_dataset = [
        # === 简单情况 ===
        {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
        {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
        
        # === 中等难度：否定句 ===
        {"input": "产品质量不错，但是价格有点贵，总体来说还行", "ground_truth": "中立"},
        {"input": "并不是很满意这次购物体验", "ground_truth": "消极"},
        {"input": "不得不说，这次的服务让我很惊喜", "ground_truth": "积极"},
        
        # === 高难度：讽刺、反语 ===
        {"input": "呵呵，真是物超所值啊，买的时候说得天花乱坠，收到货就是个破烂", "ground_truth": "消极"},
        {"input": "物流速度一般般，不过产品还可以", "ground_truth": "中立"},
        
        # === 高难度：混合情感 ===
        {"input": "外观设计很漂亮，但功能有些鸡肋，用了一周感觉还凑合", "ground_truth": "中立"},
        {"input": "客服态度超级好！虽然产品有点小瑕疵但瑕不掩瑜，强烈推荐", "ground_truth": "积极"},
        
        # === 高难度：委婉表达 ===
        {"input": "可能是我期望太高了吧，总觉得和宣传的不太一样", "ground_truth": "消极"},
    ]
    
    print("📋 测试配置：")
    print(f"  任务类型: {task_type}")
    print(f"  任务描述: {task_description}")
    print(f"  测试样本: {len(test_dataset)} 条")
    print(f"    - 简单样本: 2 条")
    print(f"    - 中等难度: 3 条（否定句）")
    print(f"    - 高难度: 5 条（讽刺/混合情感/委婉表达）")
    print(f"  进化代数: 5 代")
    print(f"  种群规模: 6 个体")
    print(f"  预计 API 调用: {5 * 6 * len(test_dataset)} 次")
    print(f"\n💡 更具挑战性的测试，能更好地体现遗传算法的优化能力\n")
    
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
    
    # 执行遗传算法
    print("-" * 60)
    print("步骤 2: 执行遗传算法进化")
    print("-" * 60)
    
    try:
        all_results, best_result, evolution_history = optimizer.run_genetic_algorithm(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            generations=5,  # 增加到5代
            population_size=6,  # 增加到6个体
            elite_ratio=0.3,  # 保留 2 个精英（6 * 0.3 ≈ 2）
            mutation_rate=0.25  # 25% 变异率
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("🏆 遗传算法结果")
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
        
        # 进化历史分析
        print(f"\n📈 进化历史分析:")
        print(f"{'代数':<8}{'最高分':<12}{'平均分':<12}{'最低分':<12}{'进化状态'}")
        print("-" * 60)
        
        for i, gen in enumerate(evolution_history):
            status = ""
            if i > 0:
                improvement = gen['best_score'] - evolution_history[i-1]['best_score']
                if improvement > 0:
                    status = f"📈 +{improvement:.2f}"
                elif improvement == 0:
                    status = "➡️ 持平"
                else:
                    status = f"📉 {improvement:.2f}"
            
            print(f"第{gen['generation']}代  "
                  f"{gen['best_score']:<12.2f}"
                  f"{gen['avg_score']:<12.2f}"
                  f"{gen['worst_score']:<12.2f}"
                  f"{status}")
        
        # 计算总增益
        total_gain = evolution_history[-1]['best_score'] - evolution_history[0]['best_score']
        print(f"\n🧬 总进化增益: {total_gain:+.2f} 分")
        
        if total_gain > 0:
            print(f"✅ 遗传算法成功！通过 {len(evolution_history)} 代进化，得分提升了 {total_gain:.2f} 分")
        else:
            print(f"ℹ️ 本次测试未见明显提升，可能原因：")
            print(f"   - 测试集太简单（都是 100 分）")
            print(f"   - 代数太少（建议 5-10 代）")
            print(f"   - 种群太小（建议 8-20 个体）")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 遗传算法执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_genetic_algorithm()
