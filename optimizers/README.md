# Optimizers 模块

## 📁 模块简介

本模块包含针对不同任务类型的专用 Prompt 优化器，每个优化器针对特定任务（分类、摘要、翻译）实现定制化的优化逻辑。

## 🎯 核心功能

- **任务专用优化**：为不同类型的 NLP 任务提供专门的优化策略
- **统一接口**：所有优化器继承自 `BaseOptimizer`，提供一致的 API
- **LLM 驱动**：使用 Meta-Prompt 引导 LLM 生成高质量的任务 Prompt
- **结构化输出**：返回符合 Pydantic 模型的结构化结果

## 📄 文件说明

### `base.py`
**基础优化器类**

提供所有任务优化器的通用功能：

#### 核心类

**`BaseOptimizer`**
- **功能**: 所有优化器的抽象基类
- **核心方法**:
  - `_call_llm(meta_prompt: str) -> str`: 调用 LLM 并返回响应
  - `_parse_and_validate(content: str, model_class: Type[BaseModel]) -> BaseModel`: 解析 JSON 并验证数据结构
  - `optimize(...)`: 抽象方法，由子类实现具体优化逻辑

- **通用功能**:
  - LLM 调用和错误处理
  - JSON 响应解析和清理
  - 数据模型验证
  - 日志输出和调试信息

**特点**:
- 使用 `abc.ABC` 和 `@abstractmethod` 确保子类实现必需方法
- 统一的异常处理机制
- 可配置的 LLM 参数（temperature、max_tokens）

### `classification.py`
**分类任务优化器**

针对文本分类任务的专用优化器：

#### 核心类

**`ClassificationOptimizer`**
- **继承**: `BaseOptimizer`
- **任务类型**: 文本分类（情感分析、主题分类、意图识别等）

#### 核心方法

**`optimize(task_description: str, labels: List[str]) -> ClassificationPrompt`**
- **输入**:
  - `task_description`: 分类任务描述，如 "判断用户评论的情感倾向"
  - `labels`: 标签列表，如 `["正面", "负面", "中立"]`
  
- **处理流程**:
  1. 加载 classification Meta-Prompt 模板
  2. 填充任务描述和标签信息
  3. 调用 LLM 生成优化后的分类 Prompt
  4. 解析并验证返回的 JSON
  5. 构建 `ClassificationPrompt` 对象

- **返回**: `ClassificationPrompt` 对象，包含：
  - `role_definition`: 角色设定（如 "你是专业的情感分析专家"）
  - `label_definitions`: 标签详细定义
  - `few_shot_examples`: 自动生成的示例
  - `reasoning_guidance`: 推理引导
  - `output_format`: 输出格式要求
  - `final_prompt`: 最终可用的完整 Prompt

**优化策略**:
- 自动设计合适的角色身份
- 生成高质量的 Few-shot 示例
- 强制输出格式控制（只输出标签名）
- 包含占位符以便后续替换实际文本

### `summarization.py`
**摘要任务优化器**

针对文本摘要任务的专用优化器：

#### 核心类

**`SummarizationOptimizer`**
- **继承**: `BaseOptimizer`
- **任务类型**: 文本摘要（会议纪要、论文摘要、新闻总结等）

#### 核心方法

**`optimize(task_description: str, source_type: str, target_audience: str, focus_points: str, length_constraint: Optional[str]) -> SummarizationPrompt`**

- **输入**:
  - `task_description`: 摘要任务描述，如 "总结技术会议的核心决策"
  - `source_type`: 源文本类型，如 "会议记录"、"学术论文"
  - `target_audience`: 目标读者，如 "技术经理"、"普通用户"
  - `focus_points`: 核心关注点，如 "行动计划和负责人"
  - `length_constraint`: 篇幅限制，如 "100字以内"、"3-5个要点"（可选）

- **处理流程**:
  1. 加载 summarization Meta-Prompt 模板
  2. 填充所有任务参数
  3. 调用 LLM 生成优化后的摘要 Prompt
  4. 解析并验证返回的 JSON
  5. 构建 `SummarizationPrompt` 对象

- **返回**: `SummarizationPrompt` 对象，包含：
  - `role_setting`: 角色设定
  - `extraction_rules`: 提取规则列表
  - `negative_constraints`: 负面约束（告诉模型不要做什么）
  - `step_by_step_guide`: 分步操作指导
  - `final_prompt`: 最终可用的完整 Prompt

**优化策略**:
- 根据目标读者调整语言风格
- 明确信息提取规则
- 设置负面约束避免常见错误
- 提供分步思考框架

### `translation.py`
**翻译任务优化器**

针对文本翻译任务的专用优化器：

#### 核心类

**`TranslationOptimizer`**
- **继承**: `BaseOptimizer`
- **任务类型**: 文本翻译（多语言、领域翻译、风格转换等）

#### 核心方法

**`optimize(source_lang: str, target_lang: str, domain: str, tone: str, user_glossary: str) -> TranslationPrompt`**

- **输入**:
  - `source_lang`: 源语言，如 "中文"、"英文"
  - `target_lang`: 目标语言
  - `domain`: 应用领域，如 "通用日常"、"IT/技术文档"、"法律合同"
  - `tone`: 期望风格，如 "标准/准确"、"地道/口语化"
  - `user_glossary`: 用户提供的术语表，格式如 "Prompt=提示词\nLLM=大语言模型"

- **处理流程**:
  1. 加载 translation Meta-Prompt 模板
  2. 填充语言对、领域、风格、术语表
  3. 调用 LLM 生成优化后的翻译 Prompt
  4. 解析并验证返回的 JSON
  5. 构建 `TranslationPrompt` 对象

- **返回**: `TranslationPrompt` 对象，包含：
  - `role_setting`: 角色设定
  - `domain_knowledge`: 领域知识说明
  - `tone_guidance`: 语气/风格指导
  - `quality_checks`: 质量检查清单
  - `glossary_integration`: 术语表使用说明
  - `final_prompt`: 最终可用的完整 Prompt

**优化策略**:
- 根据领域注入专业知识
- 集成用户术语表
- 提供风格和语气指导
- 包含质量检查清单

### `__init__.py`
**模块接口**

导出所有优化器类：
```python
from optimizers import ClassificationOptimizer, SummarizationOptimizer, TranslationOptimizer
```

## 🔗 与其他模块的关系

- **继承**: 
  - 所有优化器继承自 `base.BaseOptimizer`

- **依赖**:
  - `config.template_loader`: 加载 Meta-Prompt 模板
  - `config.models`: 使用数据模型定义返回值
  - `services.LLMService`: 调用 LLM
  - `utils.safe_json_loads`: JSON 解析

- **被调用**:
  - `optimizer.PromptOptimizer`: 组合使用所有优化器

## 📊 优化器对比

| 优化器 | 任务类型 | 关键输出 | 主要优化点 |
|--------|----------|----------|------------|
| Classification | 文本分类 | Few-shot 示例、输出格式 | 角色设定、示例质量 |
| Summarization | 文本摘要 | 提取规则、步骤指导 | 信息筛选、结构化 |
| Translation | 文本翻译 | 术语表集成、质量检查 | 领域知识、风格控制 |

## 📚 使用示例

```python
from optimizers import ClassificationOptimizer
from services import LLMService

# 创建 LLM 实例
llm = LLMService.create_llm(
    provider="nvidia",
    model="meta/llama-3.1-70b-instruct"
)

# 创建分类优化器
classifier = ClassificationOptimizer(llm)

# 优化分类任务
result = classifier.optimize(
    task_description="判断用户评论的情感倾向",
    labels=["正面", "负面", "中立"]
)

# 使用优化后的 Prompt
print(f"角色设定: {result.role_definition}")
print(f"完整 Prompt:\n{result.final_prompt}")

# 实际分类
final_prompt = result.final_prompt.replace(
    "[待分类文本]", 
    "这个产品太棒了，非常满意！"
)
classification_result = llm.invoke(final_prompt)
print(f"分类结果: {classification_result.content}")
```

## ⚙️ 自定义优化器

如需添加新的任务类型优化器：

1. 继承 `BaseOptimizer`
2. 实现 `optimize()` 方法
3. 在 `config/meta_prompts/` 添加对应的模板文件
4. 在 `config/models.py` 定义数据模型
5. 在 `__init__.py` 中导出

```python
from optimizers.base import BaseOptimizer
from config.models import CustomPrompt

class CustomOptimizer(BaseOptimizer):
    def optimize(self, task_param: str) -> CustomPrompt:
        # 1. 加载模板
        meta_prompt = load_meta_prompt('custom', task_param=task_param)
        
        # 2. 调用 LLM
        content = self._call_llm(meta_prompt)
        
        # 3. 解析验证
        result = self._parse_and_validate(content, CustomPrompt)
        
        return result
```
