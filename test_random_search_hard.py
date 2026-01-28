"""
随机搜索功能测试脚本 - 困难版
使用更复杂的测试数据，能够真正区分不同 Prompt 的效果
"""

import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer

# 加载环境变量
load_dotenv()

def test_random_search_hard():
    """测试随机搜索功能 - 使用困难测试集"""
    
    print("\n" + "="*60)
    print("🧪 随机搜索功能测试 - 困难版")
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
    
    # 困难测试数据集 - 包含边界案例和模糊情感
    test_dataset = [
        # 简单案例（基准）
        {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
        {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
        
        # 困难案例1：混合情感（应该是中立，但容易被误判）
        {"input": "产品质量不错，但是价格有点贵，总体来说还行", "ground_truth": "中立"},
        
        # 困难案例2：反讽（应该是消极，但字面意思是积极）
        {"input": "哇，真是太'棒'了，收到就坏了，非常'满意'呢", "ground_truth": "消极"},
        
        # 困难案例3：委婉的负面（应该是消极）
        {"input": "emmm...怎么说呢，可能不太适合我吧", "ground_truth": "消极"},
        
        # 困难案例4：客观描述（应该是中立）
        {"input": "包装是红色的，尺寸和描述一致，昨天收到的", "ground_truth": "中立"},
        
        # 困难案例5：期待落空（应该是消极）
        {"input": "本来抱了很大期望，结果就这？", "ground_truth": "消极"},
        
        # 困难案例6：轻微不满但整体可以（应该是中立）
        {"input": "有一点小瑕疵，不过凑合能用", "ground_truth": "中立"}
    ]
    
    print("📋 测试配置：")
    print(f"  任务类型: {task_type}")
    print(f"  任务描述: {task_description}")
    print(f"  测试样本: {len(test_dataset)} 条（包含 6 个困难边界案例）")
    print(f"  迭代次数: 5 次")
    print(f"  预计 API 调用: {5 * len(test_dataset)} 次")
    print(f"\n💡 困难点：反讽、混合情感、委婉表达、客观描述\n")
    
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
    except Exception as e:
        print(f"❌ 生成搜索空间失败: {e}")
        return
    
    # 执行随机搜索
    print("-" * 60)
    print("步骤 2: 执行随机搜索")
    print("-" * 60)
    
    try:
        all_results, best_result = optimizer.run_random_search(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            iterations=5
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("🏆 搜索结果汇总")
        print("="*60)
        
        print(f"\n🥇 冠军 Prompt:")
        print(f"  得分: {best_result.avg_score:.2f}%")
        print(f"  角色: {best_result.role}")
        print(f"  风格: {best_result.style}")
        print(f"  技巧: {best_result.technique}")
        
        print(f"\n📜 完整 Prompt:")
        print("-" * 60)
        print(best_result.full_prompt)
        print("-" * 60)
        
        print(f"\n📊 所有结果排行（可以看出差异）:")
        sorted_results = sorted(all_results, key=lambda x: x.avg_score, reverse=True)
        for i, result in enumerate(sorted_results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"  {emoji} {i}. 得分 {result.avg_score:.2f}% - {result.role} + {result.style}")
        
        # 分析得分差异
        scores = [r.avg_score for r in all_results]
        score_range = max(scores) - min(scores)
        
        print(f"\n📈 得分分析：")
        print(f"  最高分: {max(scores):.2f}%")
        print(f"  最低分: {min(scores):.2f}%")
        print(f"  分数跨度: {score_range:.2f}%")
        
        if score_range > 10:
            print(f"  ✅ 差异明显！不同 Prompt 确实有显著影响")
        elif score_range > 5:
            print(f"  📊 有一定差异，说明 Prompt 策略有影响")
        else:
            print(f"  ⚠️ 差异较小，可能需要更难的测试集或更多样本")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 随机搜索执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_random_search_hard()
