"""
端到端测试 - 使用真实 API 测试完整功能
"""
import os
from optimizer import PromptOptimizer

# 配置 API Key
NVIDIA_API_KEY = "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"

def test_basic_optimization():
    """测试基本的 Prompt 优化功能"""
    print("\n" + "="*60)
    print("🧪 测试 1: 基本 Prompt 优化")
    print("="*60)
    
    optimizer = PromptOptimizer(
        api_key=NVIDIA_API_KEY,
        model="meta/llama-3.1-70b-instruct",  # 使用 70b 模型，更好的指令遵循能力
        provider="nvidia"
    )
    
    try:
        result = optimizer.optimize(
            user_prompt="写一个友好的问候语",
            scene_desc="正式场合使用",
            optimization_mode="通用增强 (General)"
        )
        
        print("\n✅ 优化成功！")
        print(f"📝 原始提示: 写一个友好的问候语")
        print(f"\n🎯 优化后提示 (前200字符):")
        print(f"{result.improved_prompt[:200]}...")
        print(f"\n💡 应用的技术: {', '.join(result.enhancement_techniques[:3])}")
        print(f"🔑 添加的关键词: {', '.join(result.keywords_added[:3])}")
        print(f"📐 使用的结构: {result.structure_applied}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)[:200]}")
        return False


def test_classification_optimization():
    """测试分类任务优化"""
    print("\n" + "="*60)
    print("🧪 测试 2: 分类任务优化")
    print("="*60)
    
    optimizer = PromptOptimizer(
        api_key=NVIDIA_API_KEY,
        model="meta/llama-3.1-70b-instruct",  # 使用 70b 模型
        provider="nvidia"
    )
    
    try:
        result = optimizer.optimize_classification(
            task_description="判断用户评论的情感倾向",
            labels=["积极", "消极", "中立"]
        )
        
        print("\n✅ 分类优化成功！")
        print(f"📊 标签定义数量: {len(result.label_definitions)}")
        print(f"📝 Few-shot 示例数量: {len(result.few_shot_examples)}")
        print(f"\n🎯 完整 Prompt (前200字符):")
        print(f"{result.final_prompt[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)[:200]}")
        return False


def test_search_space_generation():
    """测试搜索空间生成"""
    print("\n" + "="*60)
    print("🧪 测试 3: 搜索空间生成")
    print("="*60)
    
    optimizer = PromptOptimizer(
        api_key=NVIDIA_API_KEY,
        model="meta/llama-3.1-8b-instruct",
        provider="nvidia"
    )
    
    try:
        search_space = optimizer.generate_search_space(
            task_description="判断电影评论的情感（正面/负面）",
            task_type="classification"
        )
        
        print("\n✅ 搜索空间生成成功！")
        print(f"🎭 角色数量: {len(search_space.roles)}")
        print(f"🎨 风格数量: {len(search_space.styles)}")
        print(f"🛠️  技巧数量: {len(search_space.techniques)}")
        print(f"\n示例角色: {', '.join(search_space.roles[:3])}")
        print(f"示例风格: {', '.join(search_space.styles[:3])}")
        print(f"示例技巧: {', '.join(search_space.techniques[:2])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)[:200]}")
        return False


def main():
    """运行所有端到端测试"""
    print("\n" + "="*70)
    print("🚀 PromptUp 端到端测试 (使用真实 API)")
    print("="*70)
    print(f"📡 API Provider: NVIDIA")
    print(f"🤖 Model: meta/llama-3.1-8b-instruct")
    print("="*70)
    
    results = []
    
    # 测试 1: 基本优化
    results.append(("基本 Prompt 优化", test_basic_optimization()))
    
    # 测试 2: 分类优化
    results.append(("分类任务优化", test_classification_optimization()))
    
    # 测试 3: 搜索空间
    results.append(("搜索空间生成", test_search_space_generation()))
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！项目可以投入使用！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
