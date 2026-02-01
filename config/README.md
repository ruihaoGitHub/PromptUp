# Config 模块

## 📁 模块简介

本模块负责配置管理和数据模型定义，包括 Pydantic 数据模型、Meta-Prompt 模板加载等核心配置功能。

## 🎯 核心功能

- **数据模型定义**：使用 Pydantic 定义所有数据结构，确保类型安全
- **模板管理**：加载和格式化 Meta-Prompt 模板文件
- **配置集中化**：统一管理项目的配置和常量

## 📄 文件说明

### `models.py`
**数据模型定义**

使用 Pydantic BaseModel 定义所有核心数据结构：

#### 优化结果模型
- **`OptimizedPrompt`**: 通用 Prompt 优化结果
  - `thinking_process`: 优化思考过程
  - `improved_prompt`: 优化后的 Prompt
  - `enhancement_techniques`: 使用的优化技术
  - `keywords_added`: 添加的关键词
  - `structure_applied`: 应用的框架名称

- **`ClassificationPrompt`**: 分类任务优化结果
  - `role_definition`: 角色设定
  - `label_definitions`: 标签定义字典
  - `few_shot_examples`: Few-shot 示例
  - `reasoning_guidance`: 推理引导
  - `output_format`: 输出格式要求
  - `final_prompt`: 最终完整 Prompt

- **`SummarizationPrompt`**: 摘要任务优化结果
  - `role_setting`: 角色设定
  - `extraction_rules`: 提取规则列表
  - `negative_constraints`: 负面约束
  - `step_by_step_guide`: 分步指导
  - `final_prompt`: 最终完整 Prompt

- **`TranslationPrompt`**: 翻译任务优化结果
  - `role_setting`: 角色设定
  - `domain_knowledge`: 领域知识
  - `tone_guidance`: 语气指导
  - `quality_checks`: 质量检查清单
  - `glossary_integration`: 术语表集成说明
  - `final_prompt`: 最终完整 Prompt

#### 搜索优化模型
- **`SearchSpace`**: 搜索空间定义
  - `roles`: 可选角色列表
  - `styles`: 可选风格列表
  - `techniques`: 可选技巧列表

- **`SearchResult`**: 搜索优化结果
  - `best_prompt`: 最佳 Prompt
  - `best_score`: 最佳分数
  - `best_combination`: 最佳组合（角色、风格、技巧）
  - `all_results`: 所有尝试的结果历史

**特点**：
- 使用 `Field()` 提供详细的字段描述
- 所有模型都支持 JSON 序列化/反序列化
- 类型提示完整，IDE 友好

### `template_loader.py`
**Meta-Prompt 模板加载器**

负责从外部文件加载和格式化 Meta-Prompt 模板：

#### 核心函数

**`load_meta_prompt(template_file: str, **kwargs) -> str`**
- **功能**: 加载模板文件并填充变量
- **参数**:
  - `template_file`: 模板文件名（不含扩展名）
    - `'generation'`: 通用 Prompt 生成模板
    - `'classification'`: 分类任务模板
    - `'summarization'`: 摘要任务模板
    - `'translation'`: 翻译任务模板
    - `'search_space'`: 搜索空间生成模板
  - `**kwargs`: 模板变量（如 `task_description`, `labels_str` 等）
- **返回**: 填充后的 Meta-Prompt 字符串
- **异常**: 
  - `FileNotFoundError`: 模板文件不存在
  - `ValueError`: 缺少必需的模板变量

**`get_generation_meta_prompt(...) -> str`**
- **功能**: 生成任务的专用 Meta-Prompt 构建器
- **参数**:
  - `template_name`: 框架名称（如 'CO-STAR'、'BROKE'）
  - `focus_principles`: 优化原则列表
  - `extra_requirements`: 额外要求列表
  - `scene_desc`: 场景描述
  - `optimization_principles`: 优化原则字典
- **返回**: 格式化的 generation Meta-Prompt

**特点**：
- 模板文件存储在 `config/meta_prompts/` 目录
- 使用 Python `str.format()` 进行变量替换
- 集中管理所有 Meta-Prompt，便于维护和迭代

### `meta_prompts/` 目录
**Meta-Prompt 模板文件**

存储所有 Meta-Prompt 的文本模板：

- **`generation.txt`**: 通用 Prompt 优化的 Meta-Prompt
  - 教 LLM 如何优化 Prompt
  - 包含优化策略、输出格式要求
  - 支持多种框架（CO-STAR、BROKE 等）
  
- **`classification.txt`**: 分类任务专用 Meta-Prompt
  - 指导如何构建分类 Prompt
  - 强调输出格式控制
  - 包含 Few-shot 示例生成策略

- **`summarization.txt`**: 摘要任务专用 Meta-Prompt
  - 指导如何生成摘要 Prompt
  - 强调信息提取规则
  - 包含负面约束和质量控制

- **`translation.txt`**: 翻译任务专用 Meta-Prompt
  - 指导如何生成翻译 Prompt
  - 强调术语表集成
  - 包含领域知识和语气控制

- **`search_space.txt`**: 搜索空间生成 Meta-Prompt
  - 指导如何生成角色、风格、技巧列表
  - 根据任务类型自动调整
  - 输出 JSON 格式的搜索空间

**格式**：
- 纯文本文件，使用 `{variable}` 作为占位符
- UTF-8 编码
- 包含详细的指导说明和输出格式要求

### `__init__.py`
**模块接口**

导出所有配置类和函数：
```python
from config import OptimizedPrompt, ClassificationPrompt
from config import load_meta_prompt, get_generation_meta_prompt
```

## 🔗 与其他模块的关系

- **被调用**:
  - `optimizer`: 使用数据模型定义返回值
  - `optimizers`: 使用模板加载器获取 Meta-Prompt
  - `algorithms`: 使用 SearchSpace 模型
  - `services.ResponseParser`: 解析为数据模型实例

- **依赖**:
  - `pydantic`: BaseModel 和 Field
  - `pathlib`: 文件路径处理

## 📋 模板变量参考

### generation.txt 需要的变量
- `template_name`: 框架名称（CO-STAR/BROKE/etc.）
- `principles_text`: 优化原则文本
- `extra_text`: 额外要求文本
- `scene_desc`: 场景描述

### classification.txt 需要的变量
- `task_description`: 分类任务描述
- `labels_str`: 标签列表（逗号分隔）
- `first_label`: 第一个标签（示例用）

### summarization.txt 需要的变量
- `task_description`: 摘要任务描述
- `source_type`: 源文本类型
- `target_audience`: 目标读者
- `focus_points`: 关注重点
- `length_constraint`: 篇幅限制

### translation.txt 需要的变量
- `source_lang`: 源语言
- `target_lang`: 目标语言
- `domain`: 应用领域
- `tone`: 期望风格
- `user_glossary`: 用户术语表

## 📚 使用示例

```python
from config import OptimizedPrompt, load_meta_prompt

# 1. 使用数据模型
result = OptimizedPrompt(
    thinking_process="分析用户需求...",
    improved_prompt="你是一位专业的...",
    enhancement_techniques=["语义扩展", "关键词增强"],
    keywords_added=["专业", "详细"],
    structure_applied="CO-STAR"
)

# 2. 加载模板
meta_prompt = load_meta_prompt(
    'classification',
    task_description="判断情感",
    labels_str="正面, 负面, 中立",
    first_label="正面"
)
```
