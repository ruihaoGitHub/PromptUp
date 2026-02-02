# PromptUp - AI Prompt 自动优化系统

**将简单 Prompt 优化为专家级 Prompt 的智能系统**

[快速开始](#-快速开始) • [项目结构](#-项目结构) • [使用指南](#-使用指南) • [文档](#-文档导航) • [测试](#-测试)

</div>

---

## 📖 项目简介

PromptUp 是一个基于 **LLM-as-an-Optimizer** 技术的模块化 Prompt 优化系统。通过智能算法和专业框架,将用户的简单描述转化为结构化、高性能的专家级 Prompt。

### ✨ 核心特性

- 🎯 **多任务支持**：生成、分类、摘要、翻译四大任务类型
- 🧠 **智能优化**：支持多种 Prompt 框架（CO-STAR、BROKE、CRISPE、RASCEF）
- 🔬 **算法驱动**：集成随机搜索、遗传算法、贝叶斯优化
- 📊 **自动评估**：内置 Accuracy、ROUGE、BLEU 等评估指标
- 🧪 **完整测试**：E2E 测试 100% 通过（3/3），测试覆盖率完整
- 🎨 **现代化 UI**：Streamlit 构建，操作简单直观
- 🏗️ **模块化架构**：8 个独立模块，代码减少 88.3%
- ⚡ **灵活扩展**：支持 NVIDIA、OpenAI 等多种 LLM API

### 🏆 重构成果

经过 Stage 1-7 全面重构，项目已从单体应用升级为模块化架构：

- **代码减少**：从 4541 行减少到 530 行（88.3% ↓）
- **模块化**：拆分为 8 个独立模块，职责清晰
- **测试完善**：10 个测试文件，Level 1-5 全覆盖
- **文档齐全**：每个模块都有详细 README 文档

详细重构记录请参见 [REFACTORING_LOG.md](REFACTORING_LOG.md)

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

**系统要求**：
- Python 3.8+
- pip 20.0+
- 网络连接（访问 LLM API）

### 2. 获取 API Key

#### 方案 1：NVIDIA API（推荐）

1. 访问 [NVIDIA AI Endpoints](https://build.nvidia.com/explore/discover)
2. 注册账号（免费）
3. 点击右上角头像 → "Get API Key" → 生成 Key

**推荐模型**：`meta/llama-3.1-70b-instruct`（E2E 测试 100% 通过）

#### 方案 2：OpenAI API

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录账号
3. 创建新的 API Key

**推荐模型**：`gpt-4o`

### 3. 配置 API Key

创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
NVIDIA_API_KEY=nvapi-你的key
# 或者
# OPENAI_API_KEY=sk-你的key
```

### 4. 测试连接（推荐）

```bash
# 测试 API 连接
python tests/test_nvidia.py

# 运行端到端测试
python tests/test_e2e.py
```

预期输出：
```
✅ 测试 1/3: 分类任务优化 - 通过
✅ 测试 2/3: 摘要任务优化 - 通过
✅ 测试 3/3: 翻译任务优化 - 通过

🎉 所有测试通过！(3/3)
```

### 5. 启动应用

```bash
# 方式 1：直接启动
streamlit run app.py

# 方式 2：使用批处理文件（Windows）
start.bat
```

应用将在浏览器自动打开：http://localhost:8501

---

## 📁 项目结构

```
PromptUp/
│
├── 📄 核心文件
│   ├── app.py                    # Streamlit 主应用（76 行）
│   ├── optimizer.py              # 统一优化器接口（456 行）
│   ├── templates.py              # 优化策略模板
│   ├── metrics.py                # 评估指标计算
│   └── nvidia_models.py          # NVIDIA 模型列表
│
├── 📦 核心模块（8 个）
│   ├── algorithms/               # 优化算法（随机搜索、遗传、贝叶斯）
│   ├── config/                   # 配置和数据模型
│   ├── optimizers/               # 任务优化器（生成、分类、摘要、翻译）
│   ├── services/                 # LLM 服务层
│   ├── utils/                    # 工具函数（占位符、日志、评估）
│   ├── ui/                       # UI 组件（侧边栏、输入表单）
│   ├── pages/                    # Streamlit 页面模块
│   └── tests/                    # 测试模块（10 个测试文件）
│
├── 📚 文档
│   ├── README.md                 # 本文件
│   ├── PROJECT_STRUCTURE.md      # 项目结构详解
│   ├── Architecture.md           # 架构设计文档
│   ├── REFACTORING_LOG.md        # 重构日志
│   ├── TEST_PLAN.md              # 测试计划
│   └── E2E_TEST_RESULTS.md       # E2E 测试报告
│
└── 📋 配置文件
    ├── requirements.txt          # Python 依赖
    ├── .env.example              # 环境变量示例
    └── .env                      # 环境变量配置（需创建）
```

**模块统计**：
- **总文件数**：28+ 个文件
- **总代码行数**：约 4400 行
- **测试文件**：10 个
- **文档文件**：14 个（根目录 6 个 + 模块 8 个）

详细结构说明请参见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 🎯 使用指南

### 任务类型说明

PromptUp 支持四种任务类型，每种类型都有专门的优化策略：

#### 1️⃣ 生成任务 (Generation)

**适用场景**：文本创作、代码生成、内容撰写

**必填信息**：
- 任务描述：例如 "编写 Python 冒泡排序函数"
- 场景描述：例如 "用于教学演示"

**优化亮点**：
- ✅ 自动补充角色定义
- ✅ 添加输出格式要求
- ✅ 提供分步指导
- ✅ 增强上下文信息

详细说明请参见 [optimizers/README.md](optimizers/README.md#生成任务优化器)

#### 2️⃣ 分类任务 (Classification)

**适用场景**：情感分析、意图识别、内容审核

**必填信息**：
- 任务描述：例如 "对用户评论进行情感分类"
- 标签列表：例如 "积极, 消极, 中立"

**优化亮点**：
- ✅ 添加思维链引导
- ✅ 锁定输出格式（JSON/文本）

详细说明请参见 [optimizers/README.md](optimizers/README.md#分类任务优化器)

#### 3️⃣ 摘要任务 (Summarization)

**适用场景**：会议纪要、新闻摘要、长文提取

**必填信息**：
- 任务描述：例如 "总结技术会议纪要"
- 源文本类型：例如 "会议记录"
- 目标受众：例如 "技术团队成员"
- 核心关注点：例如 "决策, 行动计划"

**优化亮点**：
- ✅ 设计专业角色定位
- ✅ 制定提取规则
- ✅ 添加负面约束
- ✅ 提供格式模板

详细说明请参见 [optimizers/README.md](optimizers/README.md#摘要任务优化器)

#### 4️⃣ 翻译任务 (Translation)

**适用场景**：多语言翻译、本地化、术语翻译

**必填信息**：
- 任务描述：例如 "技术文档中英翻译"
- 源语言/目标语言：例如 "中文" / "英文"
- 翻译风格：例如 "准确专业"

**优化亮点**：
- ✅ 专业译者角色设定
- ✅ 风格指南清单
- ✅ 术语表整合
- ✅ 三步翻译法

详细说明请参见 [optimizers/README.md](optimizers/README.md#翻译任务优化器)

---

## 🧪 验证实验室

验证实验室用于测试优化后的 Prompt 效果，支持：

- ✅ **单样本测试**：快速验证 Prompt 效果
- ✅ **批量测试**：分类任务支持多行输入
- ✅ **自动评估**：Accuracy、ROUGE、BLEU 等指标
- ✅ **详细日志**：占位符检测、替换情况
- ✅ **实时进度**：测试进度可视化

### 使用流程

1. 在 "Prompt 优化器" 页面生成 Prompt
2. 切换到 "验证实验室" 页面
3. 输入测试数据和参考答案
4. 点击 "运行测试" 查看结果

### 测试用例示例

#### 分类任务测试用例

**任务描述**：对用户评论进行情感分类

**测试输入**（每行一个样本）：
```
这个产品真的很好用，非常满意！
价格太贵了，性价比不高，不推荐购买。
还可以吧，没有特别的感觉。
```

**参考答案**（每行一个标签）：
```
积极
消极
中立
```

**预期结果**：
- 📊 Accuracy: 87.5%
- 📈 详细对比表格

更多测试用例请参见 [pages/README.md](pages/README.md#验证实验室页面)

---

## 🔬 优化技术

### Meta-Prompt 技术

系统使用 **LLM-as-an-Optimizer** 技术：
1. 分析用户输入的简单 Prompt
2. 补充缺失的上下文和约束
3. 应用专业的 Prompt 工程技术
4. 生成结构化、高性能的最终 Prompt

详细技术说明请参见 [config/README.md](config/README.md#meta-prompt-模板)

### 优化算法

系统支持三种优化算法：

- **随机搜索（Random Search）**：快速探索搜索空间
- **遗传算法（Genetic Algorithm）**：进化式优化
- **贝叶斯优化（Bayesian Optimization）**：智能参数调优

详细算法说明请参见 [algorithms/README.md](algorithms/README.md)

### Prompt 框架

支持多种专业 Prompt 框架：

- **CO-STAR**：Context, Objective, Style, Tone, Audience, Response
- **BROKE**：Background, Role, Objective, Key Result, Evolve
- **CRISPE**：Capacity, Role, Insight, Statement, Personality, Experiment
- **RASCEF**：Role, Action, Steps, Context, Examples, Format

框架详细说明请参见 [config/README.md](config/README.md#prompt-框架)

### 占位符支持

系统支持 30+ 种占位符格式，确保生成的 Prompt 可直接使用：

```
[待分类文本]、[输入评论]、[待处理文本]
{{text}}、{text}、{{input}}
【待处理文本】、《待分类内容》
<text>、<<输入>>
```

占位符详细说明请参见 [utils/README.md](utils/README.md#占位符工具)

---

## 📊 评估指标

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

指标详细说明请参见 [utils/README.md](utils/README.md#评估工具)

---

## 🧬 测试

### 测试状态

```
✅ E2E 测试：3/3 通过（100%）
✅ 单元测试：完整覆盖
✅ 算法测试：Level 1-5 全覆盖
```

详细测试报告请参见 [E2E_TEST_RESULTS.md](E2E_TEST_RESULTS.md)

### 运行测试

```bash
# 运行所有测试
python tests/run_tests.py

# 运行 E2E 测试
python tests/test_e2e.py

# 运行单个算法测试
python tests/test_genetic_algorithm.py
python tests/test_bayesian_optimization.py
python tests/test_random_search.py
```

### 测试层级

- **Level 1**：基础功能测试（API 连接、模板加载）
- **Level 2**：单任务优化测试（分类、摘要、翻译）
- **Level 3**：算法测试（随机搜索、遗传、贝叶斯）
- **Level 4**：集成测试（多任务、多算法）
- **Level 5**：E2E 测试（真实 API 调用）

测试计划请参见 [TEST_PLAN.md](TEST_PLAN.md)

---

## 📚 文档导航

### 核心文档

- [项目结构详解](PROJECT_STRUCTURE.md) - 完整的项目结构说明
- [架构设计](Architecture.md) - 系统架构和设计原则
- [重构日志](REFACTORING_LOG.md) - Stage 1-7 重构记录
- [测试计划](TEST_PLAN.md) - 测试策略和计划
- [E2E 测试报告](E2E_TEST_RESULTS.md) - 端到端测试结果

### 模块文档

- [algorithms/README.md](algorithms/README.md) - 优化算法模块
- [config/README.md](config/README.md) - 配置和数据模型
- [optimizers/README.md](optimizers/README.md) - 任务优化器
- [services/README.md](services/README.md) - LLM 服务层
- [utils/README.md](utils/README.md) - 工具函数
- [ui/README.md](ui/README.md) - UI 组件
- [pages/README.md](pages/README.md) - Streamlit 页面
- [tests/README.md](tests/README.md) - 测试模块

---

## 🔧 API 配置

### 配置优先级

```
Streamlit 界面输入 > .env 文件配置
```

### 方式 1：.env 文件（推荐）

**优点**：
- ✅ 配置一次，永久有效
- ✅ 所有脚本和应用都能使用
- ✅ 不需要每次都输入

**使用**：
```bash
# 编辑 .env 文件
NVIDIA_API_KEY=nvapi-你的key
```

### 方式 2：Streamlit 界面

**优点**：
- ✅ 临时使用，不保存到文件
- ✅ 可以快速切换不同的 API Key
- ✅ 适合演示或测试

**限制**：
- ❌ 只在 Streamlit 应用中有效
- ❌ 测试脚本无法使用

---

## 🛠️ 技术栈

- **前端框架**：Streamlit 1.31.0+
- **LLM 框架**：LangChain（langchain-core, langchain-nvidia-ai-endpoints）
- **数据验证**：Pydantic 2.5.0+
- **评估库**：scikit-learn、rouge-score、nltk、jieba
- **API 提供商**：NVIDIA AI Endpoints、OpenAI

详细技术栈请参见 [Architecture.md](Architecture.md#技术栈)

---

## 💡 开发指南

### 添加新任务类型

1. 在 [config/task_configs.py](config/task_configs.py) 定义数据模型
2. 在 [config/meta_prompts/](config/meta_prompts/) 创建 Meta-Prompt 模板
3. 在 [optimizers/](optimizers/) 创建任务优化器
4. 在 [pages/optimizer_page.py](pages/optimizer_page.py) 添加 UI
5. 编写测试用例

详细开发指南请参见 [Architecture.md](Architecture.md#开发指南)

### 添加新优化算法

1. 在 [algorithms/](algorithms/) 实现算法类
2. 在 [algorithms/search_space.py](algorithms/search_space.py) 定义搜索空间
3. 在 [optimizer.py](optimizer.py) 集成算法
4. 编写测试用例

算法接口说明请参见 [algorithms/README.md](algorithms/README.md)

---

## ❓ 常见问题

### Q1: 为什么推荐使用 NVIDIA API？

**A:** 
- ✅ 免费额度充足
- ✅ 支持 60+ 开源模型（Llama、Mistral、Qwen 等）
- ✅ meta/llama-3.1-70b-instruct 性能强大
- ✅ 无需绑定信用卡

### Q2: 生成的 Prompt 没有占位符怎么办？

**A:** 
- 系统会自动检测并修复
- 日志中会显示 "✅ 找到占位符" 或 "⚠️ 自动修复：添加了占位符"
- 详见 [utils/README.md](utils/README.md#占位符自动修复)

### Q3: 分类任务准确率为 0% 怎么办？

**A:**
1. 检查参考答案是否与标签列表一致
2. 查看详细日志，确认 LLM 是否正确输出
3. 尝试重新生成 Prompt，添加更多示例
4. 详见 [troubleshooting 指南](pages/README.md#常见问题)

### Q4: 如何切换模型？

**A:**
- 在 Streamlit 侧边栏选择 API 提供商
- 从模型下拉列表中选择目标模型
- NVIDIA 推荐：`meta/llama-3.1-70b-instruct`
- OpenAI 推荐：`gpt-4o`

### Q5: 如何贡献代码？

**A:**
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request
5. 详见 [开发指南](#-开发指南)

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢以下开源项目：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [Streamlit](https://github.com/streamlit/streamlit) - Web 应用框架
- [Pydantic](https://github.com/pydantic/pydantic) - 数据验证库
- [NVIDIA AI Endpoints](https://build.nvidia.com/) - LLM API 服务

---

## 📧 联系方式

- **GitHub**：[ruihaoGitHub/PromptUp](https://github.com/ruihaoGitHub/PromptUp)
- **Issues**：[提交问题](https://github.com/ruihaoGitHub/PromptUp/issues)
- **Discussions**：[参与讨论](https://github.com/ruihaoGitHub/PromptUp/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by [Ruihao](https://github.com/ruihaoGitHub)

</div>
