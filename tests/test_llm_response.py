"""测试 LLM 返回格式"""
import os
os.environ['NVIDIA_API_KEY'] = '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'

from services import LLMService

llm = LLMService.create_llm(
    provider='nvidia',
    api_key='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',
    model='meta/llama-3.1-8b-instruct'
)

prompt = """请严格按照 JSON 格式返回结果，不要添加任何 Markdown 标记。

要求：返回一个 JSON 对象，包含以下字段：
- thinking_process: 思考过程
- improved_prompt: 改进后的提示词

示例格式：
{
  "thinking_process": "分析...",
  "improved_prompt": "请..."
}

现在请优化这个提示词: 写一个友好的问候语
"""

print("📤 发送请求...")
response = llm.invoke(prompt)

print("\n" + "="*60)
print("📥 原始响应内容")
print("="*60)
print(response.content)
print("\n" + "="*60)
print(f"📏 响应长度: {len(response.content)} 字符")
print("="*60)
