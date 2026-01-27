# 🚀 快速开始指南

## 获取 NVIDIA API Key（推荐，免费）

1. 访问 [NVIDIA AI Endpoints](https://build.nvidia.com/)
2. 点击右上角 "Sign in" 或 "Get API Key"
3. 使用 NVIDIA 账号登录（可以用 Google/GitHub 账号）
4. 在任意模型页面点击 "Get API Key"
5. 复制生成的 API Key（格式：`nvapi-xxxxx`）

## 配置项目

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件：

```env
# 使用 NVIDIA API（推荐）
API_PROVIDER=nvidia
NVIDIA_API_KEY=nvapi-你的真实key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# 或使用 OpenAI API
API_PROVIDER=openai
OPENAI_API_KEY=sk-你的真实key
```

### 3. 测试连接

运行测试脚本验证配置：

```bash
python test_nvidia.py
```

如果看到 ✅ 表示配置成功！

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

## 使用界面

### 左侧边栏配置

1. **API 提供商**：选择 NVIDIA 或 OpenAI
2. **API Key**：输入你的 API Key（也可以在 .env 中配置）
3. **模型选择**：
   - NVIDIA 推荐：`meta/llama-3.1-405b-instruct`（最强）
   - 或：`meta/llama-3.1-70b-instruct`（平衡）
   - 或：`deepseek/deepseek-r1`（推理能力强）
4. **优化模式**：根据任务选择
   - 代码生成：编程任务
   - 创意写作：文案、故事
   - 学术分析：研究、论文
   - 通用增强：其他任务

### 主界面使用

**左侧 - 输入区**：
1. 输入你的简单 Prompt（如："写个计算器"）
2. （可选）补充场景描述（如："Python, 给初学者"）
3. 点击 "开始魔法优化"

**右侧 - 结果区**：
- 查看优化思路
- 复制优化后的 Prompt
- （可选）运行 A/B 对比测试

## 示例场景

### 场景1：代码生成

**输入**：
```
Prompt: 写个贪吃蛇游戏
场景: Python, 给小孩学编程用
模式: 代码生成
```

**优化后效果**：
- ✅ 明确技术栈（pygame）
- ✅ 添加功能列表（移动、碰撞、得分）
- ✅ 要求代码注释和规范
- ✅ 指定输出格式

### 场景2：文案创作

**输入**：
```
Prompt: 写个产品介绍
场景: 智能手表，面向年轻人
模式: 创意写作
```

**优化后效果**：
- ✅ 设定营销文案角色
- ✅ 明确目标受众和情感诉求
- ✅ 规定内容结构（标题、亮点、场景）
- ✅ 添加行动号召

### 场景3：学术分析

**输入**：
```
Prompt: 分析 AI 发展趋势
场景: 大学论文
模式: 学术分析
```

**优化后效果**：
- ✅ 要求理论框架和数据支撑
- ✅ 强调逻辑性和客观性
- ✅ 规范引用和结论
- ✅ 批判性思考

## 可用的 NVIDIA 模型

### 推荐模型（最佳效果）

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| `meta/llama-3.1-405b-instruct` | 最强大 | 所有任务 |
| `meta/llama-3.1-70b-instruct` | 平衡性能 | 通用任务 |
| `deepseek/deepseek-r1` | 推理能力强 | 复杂分析 |
| `mistral/mistral-large-2-instruct` | 多语言 | 国际化项目 |
| `qwen/qwen2.5-72b-instruct` | 中文优秀 | 中文任务 |

### 其他可用模型

在界面的 "查看所有可用模型" 中可以看到 60+ 个模型，包括：
- Llama 系列（3.1/3.2/3.3）
- DeepSeek 系列（R1/V3）
- Qwen 系列
- Mistral/Mixtral 系列
- Google Gemma 系列
- Microsoft Phi 系列

## 常见问题

### Q: API Key 无效？
A: 
1. 确认从 https://build.nvidia.com/ 获取
2. 检查格式是否为 `nvapi-xxxxx`
3. 确认 Key 没有过期

### Q: 网络连接超时？
A: 
1. 检查网络连接
2. 可能需要科学上网（NVIDIA 服务器在国外）
3. 尝试更换网络环境

### Q: 优化效果不理想？
A: 
1. 尝试更大的模型（405B > 70B > 8B）
2. 在场景描述中提供更多信息
3. 选择更合适的优化模式
4. 查看优化思路，了解系统的改进方向

### Q: 模型返回结果很慢？
A: 
1. 大模型（405B）响应较慢是正常的
2. 可以选择较小的模型（70B/8B）提速
3. 确保网络连接稳定

### Q: JSON 解析错误？
A: 
1. 系统有自动容错机制，会提供基础优化版本
2. 某些模型可能不完全遵循 JSON 格式
3. 推荐使用 Llama 3.1 系列，格式输出最稳定

## 进阶技巧

### 1. 批量优化

编写 Python 脚本批量处理：

```python
from optimizer import PromptOptimizer

optimizer = PromptOptimizer(provider="nvidia")

prompts = [
    "写个登录功能",
    "设计一个数据库",
    "创作一首诗"
]

results = optimizer.batch_optimize(prompts)
```

### 2. 自定义优化策略

编辑 `templates.py` 添加自己的场景：

```python
SCENE_STRATEGIES["我的场景"] = {
    "focus": ["clarity", "examples"],
    "template": "CO-STAR",
    "extra_requirements": ["自定义要求"]
}
```

### 3. API 切换

如果 NVIDIA API 不可用，可以快速切换到 OpenAI：

1. 在界面左侧选择 "OpenAI"
2. 输入 OpenAI API Key
3. 选择 GPT-4o 模型
4. 其他使用方式完全相同

## 获取帮助

- 📖 查看 [README.md](README.md) - 项目概览
- 📚 查看 [USAGE.md](USAGE.md) - 详细文档
- 🧪 运行 `python examples.py` - 查看示例
- 🔧 运行 `python test_nvidia.py` - 测试连接

---

**祝你使用愉快！有问题随时查看文档或提 Issue 🚀**
