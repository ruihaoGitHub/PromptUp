# PromptUp - AI Prompt 自动优化系统

## 📖 项目简介

PromptUp 是一个基于大语言模型的 Prompt 自动优化系统，能够将用户输入的简单 Prompt 自动优化为结构化、高性能的专家级 Prompt。系统支持**4种任务类型**（生成、分类、摘要、翻译），并提供**自动评估**和**批量验证**功能。

### 核心特性

- 🚀 **多任务支持**：生成、分类、摘要、翻译四大任务类型
- 🎯 **智能优化**：使用 Meta-Prompt 技术自动优化 Prompt 结构
- 📊 **自动评估**：内置 Accuracy、ROUGE、BLEU 三大评估指标
- 🧪 **验证实验室**：批量测试、A/B 对比、详细日志
- 🌐 **双API支持**：NVIDIA AI Endpoints（60+模型）+ OpenAI
- 💻 **友好界面**：Streamlit 图形化界面，零代码使用

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/ruihaoGitHub/PromptUp.git
cd PromptUp

# 安装依赖
pip install -r requirements.txt
```

### 2. 获取 API Key

#### 方式一：NVIDIA AI Endpoints（推荐，免费）

1. 访问 [NVIDIA Build](https://build.nvidia.com/)
2. 注册并登录（支持 Google/GitHub 账号）
3. 在任意模型页面点击 "Get API Key"
4. 复制生成的 API Key（格式：`nvapi-xxxxx`）

#### 方式二：OpenAI API（付费）

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 获取 API Key（格式：`sk-xxxxx`）

### 3. 配置 API Key

编辑 `.env` 文件（从 `.env.example` 复制）：

```env
# 使用 NVIDIA API（推荐）
API_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-你的真实key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# 或使用 OpenAI API
# API_PROVIDER=openai
# OPENAI_API_KEY=sk-你的真实key
```

**或者**在 Streamlit 界面中直接输入 API Key（临时使用）。

### 4. 测试连接

```bash
python test_nvidia.py
```

看到 ✅ 表示配置成功！

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

---

## 📚 使用指南

### 任务类型说明

#### 1. 生成任务 (Generation)
**适用场景**：代码生成、文案创作、内容生成

**示例**：
- 输入：`"写个贪吃蛇游戏"`
- 场景：`"Python, 给初学者"`
- 优化后会包含：技术栈、功能列表、代码规范、输出格式

#### 2. 分类任务 (Classification)
**适用场景**：文本分类、情感分析、意图识别、垃圾邮件检测

**必填信息**：
- 任务描述：例如 "对用户评论进行情感分类"
- 标签列表：例如 "积极, 消极, 中立"

**优化亮点**：
- ✅ 自动生成标签定义（Label Disambiguation）
- ✅ 合成高质量 Few-Shot 示例
- ✅ 添加思维链引导（Chain of Thought）
- ✅ 锁定输出格式（JSON/文本）
- ✅ 内置占位符确保可直接使用

#### 3. 摘要任务 (Summarization)
**适用场景**：会议纪要、新闻摘要、长文提取

**必填信息**：
- 任务描述：例如 "总结技术会议纪要"
- 源文本类型：例如 "会议记录"
- 目标受众：例如 "技术团队成员"
- 核心关注点：例如 "决策, 行动计划, 时间节点"

**优化亮点**：
- ✅ 设计专业角色定位
- ✅ 制定提取规则（关键信息、事实、数据）
- ✅ 添加负面约束（避免主观评价、猜测）
- ✅ 提供格式模板（分段、要点、表格）
- ✅ 分步骤指导（阅读→识别→组织→输出）

#### 4. 翻译任务 (Translation)
**适用场景**：多语言翻译、本地化、术语翻译

**必填信息**：
- 任务描述：例如 "将技术文档从中文翻译成英文"
- 源语言：例如 "中文"
- 目标语言：例如 "英文"
- 翻译风格：例如 "准确专业, 保持术语一致性"

**可选信息**：
- 术语表：例如 "Prompt Engineering=提示词工程, Fine-tuning=微调"

**优化亮点**：
- ✅ 专业译者角色设定
- ✅ 风格指南清单
- ✅ 术语表整合
- ✅ 三步翻译法（直译→意译→润色）

---

## 🧪 验证实验室功能

### 功能说明

验证实验室用于测试优化后的 Prompt 效果，支持：
- ✅ 单样本测试
- ✅ 批量测试（分类任务支持多行输入）
- ✅ 自动计算评估指标（Accuracy/ROUGE/BLEU）
- ✅ 详细日志输出（占位符检测、替换情况）
- ✅ 实时进度显示

### 使用步骤

1. **生成或输入 Prompt**：在左侧优化区生成 Prompt
2. **准备测试数据**：根据任务类型输入测试样本（参见下方示例）
3. **输入参考答案**：用于计算评估指标
4. **点击"运行测试"**：查看结果和指标

### 完整测试用例示例

#### 分类任务测试用例

**任务描述**：
```
对用户评论进行情感分类
```

**标签列表**：
```
积极, 消极, 中立
```

**生成 Prompt 后，进入验证实验室：**

**测试输入**（每行一个样本，支持批量）：
```
这个产品真的很好用，非常满意！
价格太贵了，性价比不高，不推荐购买。
还可以吧，没有特别的感觉。
质量很差，用了一次就坏了，太失望了。
物流很快，包装也很好，赞一个！
一般般，没什么亮点。
超出预期，强烈推荐！
客服态度很好，但产品有点小问题。
```

**参考答案**（每行一个标签，与测试数据一一对应）：
```
积极
消极
中立
消极
积极
中立
积极
中立
```

**预期结果**：
- 📊 Accuracy: 87.5%
- 📈 详细对比表格
- 📝 每个样本的预测日志

---

#### 摘要任务测试用例

**任务描述**：
```
总结技术会议纪要，提取关键决策和行动计划
```

**源文本类型**：
```
技术会议记录
```

**目标受众**：
```
技术团队成员和项目经理
```

**核心关注点**（多个用逗号分隔）：
```
问题总结, 决策事项, 行动计划, 责任人, 时间节点
```

**生成 Prompt 后，进入验证实验室：**

**测试输入**：
```
2026年1月15日，技术部召开了关于新产品开发的讨论会议。会议由技术总监李明主持，参会人员包括前端团队负责人王芳、后端团队负责人张伟、UI设计师刘洋等10人。

会议首先回顾了上个月的进度：前端团队已完成用户界面的80%，后端API开发完成60%，数据库设计已全部完成。王芳提出前端在移动端适配上遇到了一些兼容性问题，需要额外2周时间解决。张伟表示后端的用户认证模块存在性能瓶颈，计划引入Redis缓存优化。

针对遇到的问题，会议做出以下决策：
1. 移动端适配问题由王芳负责，截止时间延长至2月5日
2. 后端性能优化由张伟负责，1月20日前提交优化方案
3. 增加测试人员2名，加强测试力度
4. 下次会议定于1月30日，届时检查各项问题的解决情况

会议还讨论了产品的营销推广策略，市场部建议在发布前进行小范围内测，收集用户反馈。技术总监李明表示支持，并要求各团队配合市场部的内测工作。

会议于下午5点结束。
```

**参考答案**：
```
**会议要点：**
- 时间：2026年1月15日，主持人：李明
- 进度：前端80%，后端60%，数据库100%

**遇到的问题：**
- 前端：移动端兼容性问题
- 后端：用户认证性能瓶颈

**决策与行动计划：**
1. 王芳负责移动端适配，延期至2月5日
2. 张伟负责性能优化，1月20日提交方案
3. 增加2名测试人员
4. 下次会议：1月30日

**其他：**市场部建议内测，技术部支持配合。
```

**预期结果**：
- 📊 ROUGE-1: 65.3%
- 📊 ROUGE-2: 42.1%
- 📊 ROUGE-L: 58.7%

---

#### 翻译任务测试用例

**任务描述**：
```
将技术文档从中文翻译成英文
```

**源语言**：
```
中文
```

**目标语言**：
```
英文
```

**翻译风格**（多个用逗号分隔）：
```
准确专业, 保持术语一致性, 避免口语化
```

**术语表**（可选，格式：源词=目标词，每行一对）：
```
提示词工程=Prompt Engineering
大语言模型=Large Language Model
微调=Fine-tuning
少样本学习=Few-Shot Learning
```

**生成 Prompt 后，进入验证实验室：**

**测试输入**：
```
Prompt Engineering 是一种通过设计和优化输入提示词来提高大语言模型输出质量的技术。它不需要修改模型参数，而是通过精心设计的提示词来引导模型生成更准确、更相关的回答。这种技术在实际应用中非常重要，可以显著提升AI系统的性能和用户体验。
```

**参考答案**：
```
Prompt Engineering is a technique that improves the quality of large language model outputs by designing and optimizing input prompts. It does not require modifying model parameters, but rather guides the model to generate more accurate and relevant responses through carefully designed prompts. This technique is very important in practical applications and can significantly enhance the performance and user experience of AI systems.
```

**预期结果**：
- 📊 BLEU Score: 45.3%
- ✅ 术语翻译准确（Prompt Engineering、Large Language Model）

---

#### 生成任务测试用例

**任务描述**：
```
编写 Python 冒泡排序函数
```

**场景描述**：
```
用于教学演示，需要包含详细注释
```

**优化模式**：
```
代码生成 (Coding)
```

**生成 Prompt 后，进入验证实验室：**

**人工评估标准**：
- ✅ 函数名称合理（如 `bubble_sort`）
- ✅ 包含输入参数和返回值
- ✅ 算法实现正确
- ✅ 有适当的注释
- ✅ 可以直接运行

---

## 🎯 优化技术说明

### Meta-Prompt 技术

系统使用 "LLM-as-an-Optimizer" 技术，即用大模型来优化 Prompt：
1. 分析用户输入的简单 Prompt
2. 补充缺失的上下文和约束条件
3. 应用专业的 Prompt 工程技术
4. 生成结构化、高性能的最终 Prompt

### 支持的 Prompt 框架

- **CO-STAR**：Context, Objective, Style, Tone, Audience, Response
- **BROKE**：Background, Role, Objective, Key Result, Evolve
- **CRISPE**：Capacity, Role, Insight, Statement, Personality, Experiment
- **RASCEF**：Role, Action, Steps, Context, Examples, Format

### 占位符支持

系统支持 30+ 种占位符格式，确保生成的 Prompt 可以直接使用：
- `[待分类文本]`、`[输入评论]`、`[待处理文本]`
- `{{text}}`、`{text}`、`{{input}}`
- `【待处理文本】`、`《待分类内容》`
- `<text>`、`<<输入>>`

如果生成的 Prompt 缺少占位符，系统会自动修复并添加。

---

## 📊 评估指标说明

### Accuracy（分类任务）

- **计算方式**：正确预测数 / 总样本数 × 100%
- **评分标准**：
  - 🟢 优秀：≥ 80%
  - 🟡 良好：60% - 80%
  - 🔴 需改进：< 60%

### ROUGE Score（摘要任务）

- **ROUGE-1**：单词重叠率
- **ROUGE-2**：双词组重叠率
- **ROUGE-L**：最长公共子序列
- **评分标准**：
  - 🟢 优秀：≥ 50%
  - 🟡 良好：30% - 50%
  - 🔴 需改进：< 30%

### BLEU Score（翻译任务）

- **计算方式**：n-gram 精确度的几何平均
- **评分标准**：
  - 🟢 优秀：≥ 40%
  - 🟡 良好：20% - 40%
  - 🔴 需改进：< 20%

---

## 🔧 API 配置说明

### 配置优先级

```
Streamlit 界面输入 > .env 文件配置
```

### 两种配置方式

#### 方式 1：.env 文件（推荐）

**优点**：
- ✅ 配置一次，永久有效
- ✅ 所有脚本和应用都能使用
- ✅ 不需要每次都输入

**使用**：
```bash
# 编辑 .env 文件
NVIDIA_API_KEY=nvapi-你的key
```

#### 方式 2：Streamlit 界面

**优点**：
- ✅ 临时使用，不保存到文件
- ✅ 可以快速切换不同的 API Key
- ✅ 适合演示或测试

**限制**：
- ❌ 只在 Streamlit 应用中有效
- ❌ 测试脚本无法使用
- ❌ 每次重新打开需要重新输入

### 推荐的配置流程

1. **首次使用**：在 `.env` 文件中配置 API Key
2. **测试连接**：运行 `python test_nvidia.py`
3. **启动应用**：运行 `streamlit run app.py`
4. **临时切换**：在界面中输入新的 Key（覆盖 .env 配置）

---

## 📁 项目结构

```
PromptUp/
├── app.py                  # Streamlit 主界面
├── optimizer.py            # Prompt 优化核心逻辑
├── templates.py            # Prompt 模板库
├── metrics.py              # 评估指标计算
├── nvidia_models.py        # NVIDIA 模型列表
├── requirements.txt        # 依赖包
├── .env.example            # 环境变量示例
├── .env                    # 环境变量配置（需自己创建）
├── start.bat               # Windows 启动脚本
├── test_nvidia.py          # API 连接测试
├── test_optimize.py        # 优化功能测试
├── examples.py             # 使用示例
├── README.md               # 本文件
└── Architecture.md         # 架构说明文档
```

详细架构说明请参见 [Architecture.md](Architecture.md)。

---

## 🛠️ 技术栈

- **前端框架**：Streamlit 1.31.0+
- **LLM 框架**：LangChain (langchain-core, langchain-openai, langchain-nvidia-ai-endpoints)
- **数据验证**：Pydantic 2.5.0+
- **评估库**：
  - scikit-learn（Accuracy）
  - rouge-score（ROUGE）
  - nltk（BLEU）
  - jieba（中文分词）
- **API 提供商**：NVIDIA AI Endpoints、OpenAI

---

## ❓ 常见问题

### Q1: 为什么推荐使用 NVIDIA API？

A: 
- ✅ 免费额度充足
- ✅ 支持 60+ 开源模型（Llama、Mistral、Qwen、DeepSeek 等）
- ✅ meta/llama-3.1-405b-instruct 性能强大
- ✅ 无需绑定信用卡

### Q2: 生成的 Prompt 没有占位符怎么办？

A: 
- 系统会自动检测并修复
- 如果生成的 Prompt 缺少占位符，会自动添加任务相关的文本插入点
- 日志中会显示 "✅ 找到占位符" 或 "⚠️ 自动修复：添加了占位符"

### Q3: 分类任务准确率为 0% 怎么办？

A:
1. 检查参考答案是否与标签列表一致（大小写、空格）
2. 查看详细日志，确认 LLM 是否正确输出了标签
3. 尝试重新生成 Prompt，添加更多示例
4. 确保测试数据质量（避免过于模糊的样本）

### Q4: ROUGE/BLEU 分数很低怎么办？

A:
- 检查参考答案是否与 LLM 输出的表述方式接近
- ROUGE/BLEU 对措辞敏感，语义相同但用词不同会导致低分
- 建议配合人工评估，不要完全依赖数值指标

### Q5: 如何切换模型？

A:
- 在 Streamlit 侧边栏选择 API 提供商
- 从模型下拉列表中选择目标模型
- NVIDIA 推荐：`meta/llama-3.1-405b-instruct`（最强）
- OpenAI 推荐：`gpt-4o`（最新）

---

## 📄 许可证

MIT License

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 联系方式

- GitHub: [ruihaoGitHub/PromptUp](https://github.com/ruihaoGitHub/PromptUp)
- Issues: [提交问题](https://github.com/ruihaoGitHub/PromptUp/issues)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
