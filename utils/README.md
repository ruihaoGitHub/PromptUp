# Utils 模块

## 📁 模块简介

本模块提供通用工具函数，包括 JSON 解析、文本清理、字符串替换等基础功能，为整个项目提供底层支持。

## 🎯 核心功能

- **JSON 解析**：安全、容错的 JSON 解析功能
- **文本清理**：清理和规范化 LLM 生成的文本
- **字符串处理**：Prompt 模板中的占位符替换

## 📄 文件说明

### `keyword_analyzer.py`
**关键词贡献度分析工具（后端逻辑）**

用于对优化后的 Prompt 做分词与 Mask，对比句向量相似度下降幅度来估计关键词贡献度，并输出排序后的 DataFrame。
（注意：首次调用会加载 `text2vec` 模型，可能较慢）

### `json_parser.py`
**JSON 解析工具**

提供安全、容错的 JSON 解析功能，能够处理 LLM 返回的各种非标准 JSON 格式。

#### 核心函数

**`safe_json_loads(content: str) -> Dict[str, Any]`**
```python
def safe_json_loads(content: str) -> Dict[str, Any]
```

- **功能**: 安全地解析 JSON 字符串，具有强大的容错能力
  
- **支持的格式**:
  - ✅ 标准 JSON: `{"key": "value"}`
  - ✅ 单引号: `{'key': 'value'}` → 自动转换为双引号
  - ✅ Markdown 代码块: ` ```json\n{...}\n``` ` → 自动提取
  - ✅ 尾部逗号: `{"key": "value",}` → 自动移除
  - ✅ 换行符: `{"key": "line1\nline2"}` → 自动转义
  - ✅ Python 风格: `None`, `True`, `False` → 转换为 JSON 格式

- **处理流程**:
  1. **去除代码块标记**:
     - 检测 ` ```json ` 或 ` ``` ` 标记
     - 提取代码块中间的纯 JSON 内容
     
  2. **字符串清理**:
     - 去除首尾空白字符
     - 移除 BOM (Byte Order Mark)
     - 处理 Unicode 转义序列
     
  3. **格式修正**:
     - 将单引号替换为双引号（排除转义情况）
     - 移除尾部多余逗号
     - 转换 Python 字面量 (None/True/False)
     
  4. **尝试解析**:
     - 首先尝试标准 `json.loads()`
     - 如果失败，应用各种修正策略
     - 提供详细的错误信息

- **返回**: Python 字典对象
  
- **异常**: `json.JSONDecodeError` 当所有解析尝试都失败时

**`extract_json_from_markdown(content: str) -> str`**
```python
def extract_json_from_markdown(content: str) -> str
```

- **功能**: 从 Markdown 格式中提取 JSON 内容
- **支持格式**:
  - ` ```json\n{...}\n``` `
  - ` ```\n{...}\n``` `
  
- **返回**: 提取的纯 JSON 字符串

**使用场景**:
- 解析 LLM 返回的 JSON 响应
- 处理用户输入的 JSON 配置
- 解析外部 API 返回的数据

**特点**:
- 极强的容错能力，能处理各种非标准 JSON
- 详细的调试日志，便于排查问题
- 自动处理常见的 LLM 输出问题

### `text_cleaner.py`
**文本清理工具**

清理和规范化 LLM 生成的文本内容。

#### 核心函数

**`clean_improved_prompt(prompt_text: str) -> str`**
```python
def clean_improved_prompt(prompt_text: str) -> str
```

- **功能**: 清理 `improved_prompt` 字段，处理 LLM 错误返回 JSON 对象的情况
  
- **问题场景**:
  LLM 有时会错误地将 Prompt 包装成 JSON 对象：
  ```json
  {
    "role": "你是一位专业的数据分析师",
    "task": "请分析以下数据",
    "requirements": ["准确", "详细"],
    "output_format": "以表格形式呈现"
  }
  ```
  
  期望的正确格式应该是自然语言文本：
  ```
  你是一位专业的数据分析师。请分析以下数据。
  
  要求：
  - 准确
  - 详细
  
  输出格式：以表格形式呈现
  ```

- **处理逻辑**:
  1. 检测是否为 JSON 对象（以 `{` 开头，包含 `":"`）
  2. 如果是 JSON，解析并提取各个字段
  3. 将字段组合成自然语言格式：
     - `role`: 作为开头
     - `task`: 作为主要任务描述
     - `context`: 作为背景信息
     - `requirements`: 转换为列表格式
     - `examples`: 作为示例部分
     - `output_format`: 作为输出要求
     - `constraints`: 作为约束条件
  4. 如果不是 JSON，直接返回原文本

- **返回**: 清理后的自然语言 Prompt

**`remove_code_blocks(text: str) -> str`**
```python
def remove_code_blocks(text: str) -> str
```

- **功能**: 移除 Markdown 代码块标记
- **处理**: 移除 ` ```json `, ` ``` ` 等标记
- **返回**: 纯文本内容

**`normalize_whitespace(text: str) -> str`**
```python
def normalize_whitespace(text: str) -> str
```

- **功能**: 规范化空白字符
- **处理**:
  - 将多个空格合并为一个
  - 去除行首行尾空格
  - 统一换行符为 `\n`
  
- **返回**: 规范化后的文本

### `prompt_replacer.py`
**Prompt 占位符替换工具**

处理 Prompt 模板中的占位符替换。

#### 核心函数

**`replace_placeholder(prompt: str, placeholder: str, content: str) -> str`**
```python
def replace_placeholder(prompt: str, placeholder: str, content: str) -> str
```

- **功能**: 在 Prompt 中替换指定占位符
  
- **参数**:
  - `prompt`: 包含占位符的 Prompt 模板
  - `placeholder`: 占位符文本（如 `"[待分类文本]"`）
  - `content`: 要填充的实际内容
  
- **返回**: 替换后的 Prompt

**`batch_replace(prompt: str, replacements: Dict[str, str]) -> str`**
```python
def batch_replace(prompt: str, replacements: Dict[str, str]) -> str
```

- **功能**: 批量替换多个占位符
  
- **参数**:
  - `prompt`: Prompt 模板
  - `replacements`: 占位符到内容的映射字典
    ```python
    {
      "[用户名]": "张三",
      "[日期]": "2026-02-01",
      "[任务]": "数据分析"
    }
    ```
  
- **返回**: 全部替换后的 Prompt

**`find_placeholders(prompt: str) -> List[str]`**
```python
def find_placeholders(prompt: str) -> List[str]
```

- **功能**: 查找 Prompt 中的所有占位符
  
- **识别模式**:
  - `[...]`: 方括号包裹
  - `{...}`: 花括号包裹（Python format 风格）
  - `{{...}}`: 双花括号（Jinja2 风格）
  
- **返回**: 占位符列表

**使用场景**:
- 在分类 Prompt 中替换 `[待分类文本]`
- 在摘要 Prompt 中替换 `[源文本]`
- 在翻译 Prompt 中替换 `[待翻译文本]`

### `__init__.py`
**模块接口**

导出所有工具函数：
```python
from utils import safe_json_loads, clean_improved_prompt
from utils import replace_placeholder, batch_replace, find_placeholders
```

## 🔗 与其他模块的关系

- **被调用**:
  - `services.ResponseParser`: 使用 `safe_json_loads` 解析 JSON
  - `services.ResponseParser`: 使用 `clean_improved_prompt` 清理文本
  - `optimizers.base.BaseOptimizer`: 使用 JSON 解析功能
  - **所有模块**: 通用工具，被广泛调用

- **依赖**:
  - `json`: Python 标准库
  - `re`: 正则表达式模块
  - `typing`: 类型提示

## 📊 设计原则

1. **纯函数**: 所有函数都是无副作用的纯函数
2. **容错性**: 提供强大的容错能力
3. **可测试**: 每个函数都易于单元测试
4. **文档化**: 详细的文档字符串

## 📚 使用示例

### 示例 1: 安全解析 JSON

```python
from utils import safe_json_loads

# 处理 LLM 返回的非标准 JSON
content = """
```json
{
  'name': 'Test',
  'items': ['a', 'b', 'c',],
  'active': True,
  'value': None
}
```
"""

data = safe_json_loads(content)
print(data['name'])  # "Test"
print(data['items'])  # ['a', 'b', 'c']
```

### 示例 2: 清理 Prompt 字段

```python
from utils import clean_improved_prompt

# LLM 错误返回 JSON 对象
bad_prompt = """{
  "role": "你是一位资深的情感分析专家",
  "task": "请判断以下评论的情感倾向",
  "requirements": ["准确", "快速"],
  "output_format": "只输出标签名称"
}"""

# 清理为自然语言
cleaned = clean_improved_prompt(bad_prompt)
print(cleaned)
# 输出：
# 你是一位资深的情感分析专家。请判断以下评论的情感倾向。
# 
# 要求：
# - 准确
# - 快速
# 
# 输出格式：只输出标签名称
```

### 示例 3: 替换占位符

```python
from utils import replace_placeholder, batch_replace

# 单个替换
prompt = "请分析以下文本：[待分类文本]"
final_prompt = replace_placeholder(
    prompt, 
    "[待分类文本]", 
    "这个产品真不错！"
)
print(final_prompt)
# 输出: "请分析以下文本：这个产品真不错！"

# 批量替换
template = """
用户：[用户名]
日期：[日期]
任务：[任务描述]
"""

filled = batch_replace(template, {
    "[用户名]": "张三",
    "[日期]": "2026-02-01",
    "[任务描述]": "完成数据分析报告"
})
print(filled)
```

### 示例 4: 查找占位符

```python
from utils import find_placeholders

prompt = """
角色：{role}
任务：{task}
输入：[user_input]
要求：{{requirements}}
"""

placeholders = find_placeholders(prompt)
print(placeholders)
# 输出: ['{role}', '{task}', '[user_input]', '{{requirements}}']
```

## 🧪 测试建议

每个工具函数都应该有完整的单元测试：

```python
import pytest
from utils import safe_json_loads

def test_safe_json_loads_standard():
    """测试标准 JSON"""
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}

def test_safe_json_loads_single_quotes():
    """测试单引号"""
    result = safe_json_loads("{'key': 'value'}")
    assert result == {"key": "value"}

def test_safe_json_loads_markdown():
    """测试 Markdown 代码块"""
    content = '```json\n{"key": "value"}\n```'
    result = safe_json_loads(content)
    assert result == {"key": "value"}

def test_safe_json_loads_trailing_comma():
    """测试尾部逗号"""
    result = safe_json_loads('{"items": ["a", "b",]}')
    assert result == {"items": ["a", "b"]}
```

## ⚡ 性能优化

- **缓存正则表达式**: 使用 `re.compile()` 预编译常用模式
- **避免重复解析**: 在循环中缓存解析结果
- **惰性处理**: 只在需要时才进行复杂清理操作
