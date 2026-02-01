"""
测试 Prompt 优化功能（带详细日志）
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("="*60)
print("🧪 Prompt 优化测试")
print("="*60)

# 检查 API Key 配置
nvidia_key = os.getenv("NVIDIA_API_KEY", "")
if nvidia_key:
    print(f"✅ 检测到 .env 文件中的 NVIDIA API Key: {nvidia_key[:15]}...")
else:
    print("❌ 未在 .env 文件中找到 NVIDIA_API_KEY")
    print("💡 请编辑 .env 文件并添加：")
    print("   NVIDIA_API_KEY=nvapi-你的key")
    exit(1)

print("\n导入 optimizer 模块...")
from optimizer import PromptOptimizer

# 测试优化功能
print("\n创建优化器...")
optimizer = PromptOptimizer(
    model="qwen/qwen2.5-72b-instruct",  # 使用 Qwen 测试
    provider="nvidia"
)

print("\n" + "="*60)
print("测试简单 Prompt 优化")
print("="*60)

try:
    result = optimizer.optimize(
        user_prompt="帮我写一个贪吃蛇游戏",
        scene_desc="Python，给小孩学编程用",
        optimization_mode="代码生成 (Coding)"
    )
    
    print("\n" + "="*60)
    print("✅ 测试成功！")
    print("="*60)
    print(f"\n【优化思路】\n{result.thinking_process[:200]}...\n")
    print(f"【使用的技术】{result.enhancement_techniques[:3]}")
    print(f"【新增关键词】{result.keywords_added[:3]}")
    print(f"【应用框架】{result.structure_applied}")
    print(f"\n【优化后 Prompt（前200字）】\n{result.improved_prompt[:200]}...")
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ 测试失败")
    print("="*60)
    print(f"错误: {str(e)[:300]}")
    print("\n请查看上方的详细日志以了解具体问题")
