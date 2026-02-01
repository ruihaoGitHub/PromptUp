"""
随机搜索功能测试脚本
用于快速验证随机搜索算法是否正常工作
"""

import os
from dotenv import load_dotenv
from optimizer import PromptOptimizer

# 加载环境变量
load_dotenv()

def test_random_search():
    """测试随机搜索功能"""
    
    print("\n" + "="*60)
    print("🧪 随机搜索功能测试")
    print("="*60 + "\n")
    
    # 配置
    api_provider = os.getenv("API_PROVIDER", "nvidia")
    api_key = os.getenv("NVIDIA_API_KEY") if api_provider == "nvidia" else os.getenv("OPENAI_API_KEY")
    model = "meta/llama-3.1-405b-instruct" if api_provider == "nvidia" else "gpt-4o"
    
    if not api_key:
        print("❌ 未找到 API Key，请在 .env 文件中配置")
        return
    
    print(f"✅ API 提供商: {api_provider}")
    print(f"✅ 使用模型: {model}")
    print(f"✅ API Key: {api_key[:10]}..." + "\n")
    
    # 创建优化器
    try:
        optimizer = PromptOptimizer(
            api_key=api_key,
            model=model,
            provider=api_provider
        )
        print("✅ 优化器初始化成功\n")
    except Exception as e:
        print(f"❌ 优化器初始化失败: {e}")
        return
    
    # 测试任务配置
    task_description = "对用户评论进行情感分类（积极/消极/中立）"
    task_type = "classification"
    
    # 测试数据集（较小规模，快速测试）
    test_dataset = [
        {"input": "这个产品真的很好用，非常满意！", "ground_truth": "积极"},
        {"input": "价格太贵了，性价比不高", "ground_truth": "消极"},
        {"input": "还可以吧，没什么特别的", "ground_truth": "中立"}
    ]
    
    print("📋 测试配置：")
    print(f"  任务类型: {task_type}")
    print(f"  任务描述: {task_description}")
    print(f"  测试样本: {len(test_dataset)} 条")
    print(f"  迭代次数: 3 次")
    print(f"  预计 API 调用: {3 * len(test_dataset)} 次\n")
    
    # 步骤 1: 生成搜索空间
    print("-" * 60)
    print("步骤 1: 生成搜索空间")
    print("-" * 60)
    
    try:
        search_space = optimizer.generate_search_space(
            task_description=task_description,
            task_type=task_type
        )
        
        print("✅ 搜索空间生成成功！")
        print(f"\n🎭 角色池 ({len(search_space.roles)} 个):")
        for i, role in enumerate(search_space.roles, 1):
            print(f"  {i}. {role}")
        
        print(f"\n🎨 风格池 ({len(search_space.styles)} 个):")
        for i, style in enumerate(search_space.styles, 1):
            print(f"  {i}. {style}")
        
        print(f"\n🔧 技巧池 ({len(search_space.techniques)} 个):")
        for i, tech in enumerate(search_space.techniques, 1):
            print(f"  {i}. {tech}")
        print()
        
    except Exception as e:
        print(f"❌ 生成搜索空间失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤 2: 执行随机搜索
    print("-" * 60)
    print("步骤 2: 执行随机搜索")
    print("-" * 60)
    
    try:
        all_results, best_result = optimizer.run_random_search(
            task_description=task_description,
            task_type=task_type,
            test_dataset=test_dataset,
            search_space=search_space,
            iterations=3
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("🏆 搜索结果汇总")
        print("="*60)
        
        print(f"\n🥇 冠军 Prompt:")
        print(f"  得分: {best_result.avg_score:.2f}")
        print(f"  角色: {best_result.role}")
        print(f"  风格: {best_result.style}")
        print(f"  技巧: {best_result.technique}")
        
        print(f"\n📜 完整 Prompt:")
        print("-" * 60)
        print(best_result.full_prompt)
        print("-" * 60)
        
        print(f"\n📊 所有结果排行:")
        sorted_results = sorted(all_results, key=lambda x: x.avg_score, reverse=True)
        for i, result in enumerate(sorted_results, 1):
            print(f"  {i}. 得分 {result.avg_score:.2f} - {result.role} + {result.style}")
        
        print("\n✅ 测试完成！随机搜索功能运行正常。")
        
    except Exception as e:
        print(f"\n❌ 随机搜索执行失败: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    test_random_search()
