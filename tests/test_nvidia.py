"""
测试 NVIDIA API 连接和基本功能
"""
import os
import sys
# 将项目根目录（PromptUp）添加到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# 加载环境变量
load_dotenv()

def test_nvidia_connection():
    """测试 NVIDIA API 连接"""
    print("=" * 60)
    print("测试 NVIDIA AI Endpoints 连接")
    print("=" * 60)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key or api_key == "nvapi-your-key-here":
        print("❌ 错误：请先在 .env 文件中配置 NVIDIA_API_KEY")
        print("   获取 API Key：https://build.nvidia.com/")
        return False
    
    try:
        print(f"✓ 使用 API Key: {api_key[:15]}...")
        print("✓ 初始化 ChatNVIDIA 客户端...")
        
        client = ChatNVIDIA(
            model="meta/llama-3.1-8b-instruct",  # 使用较小的模型测试
            api_key=api_key,
            temperature=0.7,
            max_tokens=100
        )
        
        print("✓ 发送测试消息...")
        response = client.invoke("用一句话介绍你自己")
        
        print("\n" + "=" * 60)
        print("✅ 连接成功！模型回复：")
        print("=" * 60)
        print(response.content)
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败：{str(e)}")
        print("\n可能的原因：")
        print("1. API Key 无效或过期")
        print("2. 网络连接问题")
        print("3. 模型名称不正确")
        return False


def test_optimizer():
    """测试优化器功能"""
    print("\n" + "=" * 60)
    print("测试 Prompt 优化功能")
    print("=" * 60)
    
    from optimizer import PromptOptimizer
    
    try:
        optimizer = PromptOptimizer(
            model="meta/llama-3.1-8b-instruct",
            provider="nvidia"
        )
        
        print("✓ 优化器初始化成功")
        print("✓ 开始优化测试 Prompt...")
        
        result = optimizer.optimize(
            user_prompt="写个 Hello World",
            scene_desc="Python",
            optimization_mode="代码生成 (Coding)"
        )
        
        print("\n" + "=" * 60)
        print("✅ 优化成功！")
        print("=" * 60)
        print(f"\n【优化思路】\n{result.thinking_process[:200]}...\n")
        print(f"【使用的技术】{result.enhancement_techniques}")
        print(f"【新增关键词】{result.keywords_added}")
        print(f"【应用框架】{result.structure_applied}")
        print("\n【优化后的 Prompt（前300字）】")
        print(result.improved_prompt[:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 优化失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 NVIDIA AI Endpoints 功能测试\n")
    
    # 测试1：连接测试
    if test_nvidia_connection():
        print("\n" + "=" * 60)
        print("✅ 第一步测试通过！")
        print("=" * 60)
        
        # 测试2：优化器测试
        if test_optimizer():
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！系统可以正常使用")
            print("=" * 60)
            print("\n现在可以运行主程序：")
            print("  streamlit run app.py")
        else:
            print("\n⚠️ 优化器测试失败，请检查代码")
    else:
        print("\n⚠️ 请先配置正确的 API Key")
