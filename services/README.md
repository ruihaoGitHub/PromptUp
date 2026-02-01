# Services 服务层模块

服务层模块提供核心业务服务，包括 LLM 管理、响应解析等可复用的业务逻辑。

## 📁 模块结构

```
services/
├── __init__.py          # 模块导出
├── llm_service.py       # LLM 初始化和管理服务
├── response_parser.py   # 响应解析和清理服务
└── README.md            # 本文档
```

## 🤖 llm_service.py - LLM 管理服务

### 功能
- 统一的 LLM 初始化接口
- 支持多个 API 提供商（OpenAI、NVIDIA）
- 自动配置 API Key 和参数
- 提供商能力检测（如 JSON mode 支持）

### 核心类：LLMService

#### 静态方法

**create_llm()**
```python
LLMService.create_llm(
    provider="nvidia",           # API 提供商
    api_key="your-api-key",      # API Key
    model="meta/llama-3.1-405b-instruct",
    base_url=None,               # 可选的 base URL
    temperature=0.7,
    top_p=0.7,
    max_tokens=2048
)
```
创建并配置 LLM 实例，自动根据 provider 选择 ChatOpenAI 或 ChatNVIDIA。

**supports_json_mode()**
```python
LLMService.supports_json_mode("openai")  # True
LLMService.supports_json_mode("nvidia")  # False
```
检查指定提供商是否支持 JSON mode。

### 使用示例

```python
from services import LLMService

# 创建 NVIDIA LLM
llm = LLMService.create_llm(
    provider="nvidia",
    api_key="nvapi-xxx",
    model="qwen/qwen3-235b-a22b"
)

# 创建 OpenAI LLM
llm = LLMService.create_llm(
    provider="openai",
    api_key="sk-xxx",
    model="gpt-4o"
)

# 检查是否支持 JSON mode
if LLMService.supports_json_mode("openai"):
    response = llm.invoke(
        messages,
        response_format={"type": "json_object"}
    )
```

## 📝 response_parser.py - 响应解析服务

### 功能
- 从响应中提取 JSON（支持 Markdown 代码块）
- 解析 JSON 字符串为字典
- 清理 Prompt 字段（移除错误的 JSON 包裹）
- 友好的错误处理和提示

### 核心类：ResponseParser

#### 静态方法

**extract_json_from_response()**
```python
ResponseParser.extract_json_from_response(content)
```
从 LLM 响应中提取 JSON，支持：
- 纯 JSON 文本
- Markdown JSON 代码块 (\`\`\`json ... \`\`\`)
- 普通代码块 (\`\`\` ... \`\`\`)

**parse_json()**
```python
ResponseParser.parse_json(json_string)
```
解析 JSON 字符串为字典，内部使用 utils 的安全解析函数。

**clean_prompt_field()**
```python
cleaned_text, was_cleaned = ResponseParser.clean_prompt_field(prompt_text)
```
清理 Prompt 字段，返回清理后的文本和是否进行了清理的标志。

**parse_optimization_response()**
```python
result_dict = ResponseParser.parse_optimization_response(response_content)
```
完整的响应解析流程：提取 JSON → 解析为字典。

**handle_parsing_error()**
```python
error_message = ResponseParser.handle_parsing_error(error, response_content)
```
生成友好的错误消息，包含调试信息和建议。

### 使用示例

```python
from services import ResponseParser

# 解析 LLM 响应
try:
    # 完整流程
    result_dict = ResponseParser.parse_optimization_response(response.content)
    
    # 清理 Prompt 字段
    cleaned, was_cleaned = ResponseParser.clean_prompt_field(
        result_dict["improved_prompt"]
    )
    
except Exception as e:
    # 生成友好的错误消息
    error_msg = ResponseParser.handle_parsing_error(e, response.content)
    print(error_msg)
```

## 📊 优化效果

### optimizer.py 重构效果
- **重构前**：509 行
- **重构后**：456 行
- **减少**：53 行 (-10.4%)

### 提取的服务层代码
- **llm_service.py**：127 行
- **response_parser.py**：147 行
- **__init__.py**：8 行
- **总计**：282 行

### 代码质量提升
- ✅ **解耦**：LLM 初始化逻辑从 optimizer.py 提取
- ✅ **复用**：服务可在其他模块中使用
- ✅ **测试**：服务可独立测试
- ✅ **维护**：单一职责，易于修改和扩展

## 🎯 设计原则

### 单一职责原则
- `LLMService` 只负责 LLM 的创建和配置
- `ResponseParser` 只负责响应的解析和清理

### 依赖倒置原则
- optimizer.py 依赖服务层接口，而不是具体实现
- 服务层不依赖 optimizer.py，可独立使用

### 开闭原则
- 添加新的 LLM 提供商：扩展 LLMService
- 添加新的解析策略：扩展 ResponseParser
- 不需要修改现有代码

## 🔧 扩展指南

### 添加新的 LLM 提供商

在 `llm_service.py` 中添加新的私有方法：

```python
@staticmethod
def _create_anthropic_llm(api_key, model, ...):
    """创建 Anthropic LLM 实例"""
    # 实现逻辑
    pass
```

然后在 `create_llm()` 中添加分支：

```python
elif provider == "anthropic":
    return LLMService._create_anthropic_llm(...)
```

### 添加新的解析策略

在 `response_parser.py` 中添加新的静态方法：

```python
@staticmethod
def parse_xml_response(content: str) -> Dict:
    """解析 XML 格式的响应"""
    # 实现逻辑
    pass
```

## 💡 最佳实践

1. **使用服务层而不是直接实例化**
   ```python
   # 好的做法
   llm = LLMService.create_llm(provider="nvidia", ...)
   
   # 不推荐
   llm = ChatNVIDIA(...)  # 直接实例化
   ```

2. **统一的错误处理**
   ```python
   try:
       result = ResponseParser.parse_optimization_response(content)
   except Exception as e:
       error_msg = ResponseParser.handle_parsing_error(e, content)
       # 处理错误
   ```

3. **检查能力再使用**
   ```python
   if LLMService.supports_json_mode(provider):
       # 使用 JSON mode
   else:
       # 使用标准调用
   ```

## 🚀 未来扩展

### 计划添加的服务
- **CacheService**：LLM 响应缓存
- **RateLimitService**：API 调用频率控制
- **ValidationService**：输入输出验证
- **MetricsService**：性能监控和统计

### 可能的优化
- 异步 LLM 调用支持
- 批量请求处理
- 请求重试和降级策略
- 多提供商负载均衡
