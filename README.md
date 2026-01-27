# AI Prompt 自动优化系统

## 项目简介

这是一个基于大语言模型的 Prompt 自动优化系统，能够将用户输入的简单 Prompt 自动优化为结构化、高性能的专家级 Prompt。

## 核心功能

1. **语义扩展**：分析用户意图，补充缺失的上下文和约束条件
2. **关键词增强**：识别核心任务，加入专业术语
3. **模板化重写**：使用 CO-STAR、BROKE 等经典框架
4. **A/B 对比测试**：直接展示优化前后的效果差异

## 技术架构

- **前端**：Streamlit 图形化界面
- **后端**：LangChain + NVIDIA AI Endpoints / OpenAI API
- **核心算法**：LLM-as-an-Optimizer（以大模型优化大模型）

## 支持的 API 提供商

### NVIDIA AI Endpoints（推荐）
- 支持 60+ 开源模型
- 包括 Llama 3.1 405B、DeepSeek R1、Qwen 2.5、Mistral 等
- 免费额度可用
- 获取 API Key：[NVIDIA AI Endpoints](https://build.nvidia.com/)

### OpenAI
- 支持 GPT-4o、GPT-4 Turbo 等
- 需要付费 API Key

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
```

**使用 NVIDIA API（推荐）**：
1. 访问 [NVIDIA Build](https://build.nvidia.com/)
2. 注册并获取免费 API Key
3. 在 `.env` 文件中设置 `NVIDIA_API_KEY`

**或使用 OpenAI API**：
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 获取 API Key
3. 在 `.env` 文件中设置 `OPENAI_API_KEY`

### 3. 运行系统

```bash
streamlit run app.py
```

## 使用示例

**输入：** "写个贪吃蛇游戏"

**场景：** "Python, 给小孩学编程用"

**选择模式：** 代码生成

**选择模型：** meta/llama-3.1-405b-instruct

**输出：** 
```
你是一位资深的 Python 游戏开发工程师。请为初学者设计一个贪吃蛇游戏程序。

要求：
1. 使用 Python 的 pygame 库实现
2. 代码需要包含详细的中文注释
3. 游戏需具备以下功能：
   - 蛇的移动和转向
   - 食物随机生成
   - 碰撞检测（墙壁和自身）
   - 得分显示
4. 代码结构清晰，符合 PEP8 规范
5. 输出格式：完整的 .py 文件，可直接运行

受众：编程初学者，需要通过代码学习游戏开发基础。
```

## 项目结构

```
PromptUp/
├── app.py              # Streamlit 主界面
├── optimizer.py        # Prompt 优化核心逻辑
├── templates.py        # Prompt 模板库
├── requirements.txt    # 依赖包
├── .env.example        # 环境变量示例
└── README.md          # 项目文档
```

## 优化模式

系统支持多种优化模式：
- **通用增强**：适用于各类任务
- **代码生成**：针对编程任务优化
- **创意写作**：文案、故事创作
- **学术分析**：研究、论文写作

## 技术亮点

1. **Meta-Prompt 设计**：通过精心设计的元提示词，让 LLM 成为 Prompt 专家
2. **结构化输出**：使用 Pydantic 保证输出格式稳定
3. **多模板支持**：集成业界验证的优质框架
4. **实时对比**：A/B 测试直观展示优化效果

## License

MIT License
