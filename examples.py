"""
使用示例和测试脚本
"""
from optimizer import PromptOptimizer, quick_optimize
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def example_1_code_generation():
    """示例1：代码生成任务优化"""
    print("=" * 60)
    print("示例 1：代码生成任务（使用 NVIDIA API）")
    print("=" * 60)
    
    original = "写个贪吃蛇游戏"
    scene = "Python, 给小孩学编程用"
    
    result = quick_optimize(
        user_prompt=original,
        scene=scene,
        mode="代码生成 (Coding)",
        provider="nvidia"  # 使用 NVIDIA API
    )
    
    print(f"\n【原始 Prompt】\n{original}\n")
    print(f"【场景描述】\n{scene}\n")
    print(f"【优化思路】\n{result.thinking_process}\n")
    print(f"【优化后 Prompt】\n{result.improved_prompt}\n")
    print(f"【使用技术】{result.enhancement_techniques}")
    print(f"【新增关键词】{result.keywords_added}")
    print(f"【应用框架】{result.structure_applied}")


def example_2_creative_writing():
    """示例2：创意写作任务优化"""
    print("\n" + "=" * 60)
    print("示例 2：创意写作任务")
    print("=" * 60)
    
    original = "写个产品介绍"
    scene = "智能手表，面向年轻人"
    
    result = quick_optimize(
        user_prompt=original,
        scene=scene,
        mode="创意写作 (Creative)"
    )
    
    print(f"\n【原始 Prompt】\n{original}\n")
    print(f"【场景描述】\n{scene}\n")
    print(f"【优化思路】\n{result.thinking_process}\n")
    print(f"【优化后 Prompt】\n{result.improved_prompt}\n")


def example_3_academic_analysis():
    """示例3：学术分析任务优化"""
    print("\n" + "=" * 60)
    print("示例 3：学术分析任务")
    print("=" * 60)
    
    original = "分析人工智能的发展趋势"
    scene = "大学毕业论文，需要严谨"
    
    result = quick_optimize(
        user_prompt=original,
        scene=scene,
        mode="学术分析 (Academic)"
    )
    
    print(f"\n【原始 Prompt】\n{original}\n")
    print(f"【场景描述】\n{scene}\n")
    print(f"【优化思路】\n{result.thinking_process}\n")
    print(f"【优化后 Prompt】\n{result.improved_prompt}\n")


def example_4_ab_testing():
    """示例4：A/B 对比测试"""
    print("\n" + "=" * 60)
    print("示例 4：A/B 对比测试")
    print("=" * 60)
    
    optimizer = PromptOptimizer()
    
    original = "解释什么是递归"
    result = optimizer.optimize(original, scene_desc="给编程新手讲解")
    
    print(f"\n【原始 Prompt】\n{original}\n")
    print(f"【优化后 Prompt】\n{result.improved_prompt}\n")
    
    print("【开始 A/B 测试】")
    res_orig, res_opt = optimizer.compare_results(original, result.improved_prompt)
    
    print(f"\n【原始 Prompt 的回答】\n{res_orig[:300]}...\n")
    print(f"【优化 Prompt 的回答】\n{res_opt[:300]}...\n")


def example_5_batch_optimize():
    """示例5：批量优化"""
    print("\n" + "=" * 60)
    print("示例 5：批量优化多个 Prompt")
    print("=" * 60)
    
    optimizer = PromptOptimizer()
    
    prompts = [
        "写个计算器",
        "设计一个登录界面",
        "实现数据排序算法"
    ]
    
    results = optimizer.batch_optimize(
        prompts=prompts,
        scene_desc="Python 项目",
        optimization_mode="代码生成 (Coding)"
    )
    
    for i, (prompt, result) in enumerate(zip(prompts, results), 1):
        print(f"\n【任务 {i}】{prompt}")
        print(f"优化框架：{result.structure_applied}")
        print(f"技术：{', '.join(result.enhancement_techniques[:3])}")


if __name__ == "__main__":
    # 运行所有示例（需要先配置 API Key）
    
    # 单个示例测试
    example_1_code_generation()
    
    # 如果想运行所有示例，取消下面的注释：
    example_2_creative_writing()
    example_3_academic_analysis()
    example_4_ab_testing()
    example_5_batch_optimize()
    
    print("\n" + "=" * 60)
    print("✅ 示例运行完成！")
    print("=" * 60)
