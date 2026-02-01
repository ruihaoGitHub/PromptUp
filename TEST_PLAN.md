# PromptUp 项目测试计划

## 📋 测试概览

本测试计划旨在验证 Stage 1-7 重构后的项目完整性和功能正确性。

## 🎯 测试目标

1. ✅ 所有模块可正常导入
2. ✅ 核心功能正常工作
3. ✅ 模块间集成无误
4. ✅ UI 界面可正常启动
5. ✅ 端到端流程完整

## 📊 测试级别

### Level 1: 导入测试（Import Tests）
验证所有模块可以被正确导入，无语法错误。

### Level 2: 单元测试（Unit Tests）
测试单个模块的功能是否正常。

### Level 3: 集成测试（Integration Tests）
测试模块间的协作是否正常。

### Level 4: UI 测试（UI Tests）
测试 Streamlit 应用是否能正常启动和渲染。

### Level 5: 端到端测试（E2E Tests）
模拟真实用户操作，测试完整流程。

---

## 🧪 详细测试用例

### Level 1: 导入测试

#### Test 1.1: 核心模块导入
```python
# 测试所有核心模块能否导入
from optimizer import PromptOptimizer
from metrics import MetricsCalculator
import app
```

#### Test 1.2: 工具模块导入
```python
from utils import safe_json_loads, clean_improved_prompt
from config.models import OptimizedPrompt, SearchSpace
from config.template_loader import get_generation_meta_prompt
```

#### Test 1.3: 业务模块导入
```python
from optimizers import (
    ClassificationOptimizer,
    SummarizationOptimizer,
    TranslationOptimizer
)
from algorithms import (
    SearchSpaceGenerator,
    RandomSearchAlgorithm,
    GeneticAlgorithm,
    BayesianOptimization
)
```

#### Test 1.4: UI 模块导入
```python
from pages import (
    GenerationPage,
    ClassificationPage,
    SummarizationPage,
    TranslationPage
)
from ui import apply_custom_styles, render_sidebar
```

#### Test 1.5: 服务层导入
```python
from services import LLMService, ResponseParser
```

---

### Level 2: 单元测试

#### Test 2.1: LLMService 测试
```python
# 测试 LLM 创建
def test_llm_service_nvidia():
    llm = LLMService.create_llm(
        provider="nvidia",
        api_key="test-key",
        model="test-model"
    )
    assert llm is not None

def test_llm_service_openai():
    llm = LLMService.create_llm(
        provider="openai",
        api_key="test-key",
        model="gpt-4o"
    )
    assert llm is not None

def test_supports_json_mode():
    assert LLMService.supports_json_mode("openai") == True
    assert LLMService.supports_json_mode("nvidia") == False
```

#### Test 2.2: ResponseParser 测试
```python
def test_extract_json_from_markdown():
    content = "```json\n{\"key\": \"value\"}\n```"
    result = ResponseParser.extract_json_from_response(content)
    assert "```" not in result

def test_parse_json():
    json_str = '{"key": "value"}'
    result = ResponseParser.parse_json(json_str)
    assert result["key"] == "value"

def test_clean_prompt_field():
    prompt = '{"improved_prompt": "test"}'
    cleaned, was_cleaned = ResponseParser.clean_prompt_field(prompt)
    assert was_cleaned == True
```

#### Test 2.3: 数据模型测试
```python
def test_optimized_prompt_model():
    data = {
        "thinking_process": "测试思考过程",
        "improved_prompt": "测试改进后的提示",
        "enhancement_techniques": ["技术1"],
        "keywords_added": ["关键词1"],
        "structure_applied": "CO-STAR"
    }
    prompt = OptimizedPrompt(**data)
    assert prompt.thinking_process == "测试思考过程"
```

#### Test 2.4: 工具函数测试
```python
def test_safe_json_loads():
    # 正常 JSON
    result = safe_json_loads('{"key": "value"}')
    assert result["key"] == "value"
    
    # 带转义的 JSON
    result = safe_json_loads(r'{"key": \"value\"}')
    assert "key" in result

def test_clean_improved_prompt():
    # 包含 JSON 包裹的文本
    text = '{"improved_prompt": "实际内容"}'
    cleaned = clean_improved_prompt(text)
    assert cleaned == "实际内容"
```

---

### Level 3: 集成测试

#### Test 3.1: PromptOptimizer 初始化
```python
def test_optimizer_initialization():
    """测试 Optimizer 能否正确初始化所有组件"""
    optimizer = PromptOptimizer(
        api_key="test-key",
        model="test-model",
        provider="nvidia"
    )
    
    # 验证 LLM 已初始化
    assert optimizer.llm is not None
    
    # 验证任务优化器已初始化
    assert optimizer.classification_optimizer is not None
    assert optimizer.summarization_optimizer is not None
    assert optimizer.translation_optimizer is not None
    
    # 验证算法已初始化
    assert optimizer.search_space_generator is not None
    assert optimizer.random_search is not None
    assert optimizer.genetic_algorithm is not None
    assert optimizer.bayesian_optimization is not None
```

#### Test 3.2: 完整优化流程（需要真实 API Key）
```python
def test_optimization_flow():
    """测试完整的优化流程（需要配置真实 API Key）"""
    import os
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("⚠️ 跳过：未配置 NVIDIA_API_KEY")
        return
    
    optimizer = PromptOptimizer(
        api_key=api_key,
        model="meta/llama-3.1-8b-instruct",  # 使用小模型测试
        provider="nvidia"
    )
    
    result = optimizer.optimize(
        user_prompt="写一个简单的问候语",
        scene_desc="友好和礼貌",
        optimization_mode="通用增强 (General)"
    )
    
    # 验证返回结构
    assert result.improved_prompt is not None
    assert result.thinking_process is not None
    assert len(result.enhancement_techniques) > 0
    
    print(f"✅ 优化成功：{result.improved_prompt[:50]}...")
```

#### Test 3.3: 页面模块集成
```python
def test_page_rendering():
    """测试页面能否正确渲染（需要 Streamlit 环境）"""
    # 这个测试需要在 Streamlit 环境中运行
    # 可以通过手动测试或使用 Streamlit testing framework
    pass
```

---

### Level 4: UI 测试

#### Test 4.1: Streamlit 应用启动
```bash
# 测试应用能否启动（无错误）
streamlit run app.py --server.headless true
```

#### Test 4.2: UI 组件渲染
- [ ] 侧边栏正确显示
- [ ] 任务类型选择正常
- [ ] API 配置面板正常
- [ ] 模型选择下拉框正常

#### Test 4.3: 样式应用
- [ ] CSS 样式正确加载
- [ ] 渐变标题显示
- [ ] 按钮样式正确
- [ ] 徽章样式正确

---

### Level 5: 端到端测试

#### Test 5.1: 生成任务完整流程
1. 启动应用
2. 选择 "生成任务"
3. 配置 API Key
4. 输入测试 Prompt："写一个问候语"
5. 点击 "开始魔法优化"
6. 验证结果显示

#### Test 5.2: 分类任务完整流程
1. 选择 "分类任务"
2. 输入任务描述："情感分类"
3. 输入标签："积极, 消极, 中立"
4. 点击优化
5. 验证结果包含 few-shot 示例

#### Test 5.3: 搜索优化流程
1. 选择分类任务
2. 进入优化搜索模式
3. 配置测试数据集
4. 选择随机搜索
5. 运行 5 次迭代
6. 验证结果排序正确

---

## 🚀 执行测试

### 快速测试（5分钟）
测试所有模块能否正常导入和基本功能。

### 完整测试（30分钟）
包括需要 API 调用的集成测试。

### 手动测试（15分钟）
UI 交互和端到端流程测试。

---

## ✅ 测试检查清单

### 导入测试
- [ ] utils 模块导入
- [ ] config 模块导入
- [ ] optimizers 模块导入
- [ ] algorithms 模块导入
- [ ] pages 模块导入
- [ ] ui 模块导入
- [ ] services 模块导入
- [ ] optimizer.py 导入
- [ ] app.py 导入

### 功能测试
- [ ] LLMService 创建 LLM
- [ ] ResponseParser 解析 JSON
- [ ] 数据模型验证
- [ ] 工具函数正常工作

### 集成测试
- [ ] PromptOptimizer 初始化
- [ ] 完整优化流程（需要 API）
- [ ] 搜索算法运行（需要 API）

### UI 测试
- [ ] Streamlit 应用启动
- [ ] 侧边栏渲染
- [ ] 页面切换
- [ ] 样式应用

### E2E 测试
- [ ] 生成任务流程
- [ ] 分类任务流程
- [ ] 摘要任务流程
- [ ] 翻译任务流程
- [ ] 搜索优化流程

---

## 📝 测试报告模板

```markdown
## 测试执行报告

**测试日期**: 2026-02-01
**测试人员**: [姓名]
**测试环境**: 
- Python: 3.x
- OS: Windows/Linux/Mac
- API Provider: NVIDIA/OpenAI

### 测试结果汇总
- 总测试数: X
- 通过: X
- 失败: X
- 跳过: X

### 失败用例详情
1. [用例名称]
   - 错误信息: ...
   - 堆栈跟踪: ...
   - 建议修复: ...

### 性能指标
- 应用启动时间: X 秒
- 首次优化响应: X 秒
- 内存占用: X MB

### 建议和改进
1. ...
2. ...
```

---

## 🔧 测试工具推荐

### Python 测试框架
- **pytest**: 单元测试和集成测试
- **unittest**: Python 内置测试框架
- **coverage**: 代码覆盖率

### Streamlit 测试
- **streamlit-testing**: Streamlit 官方测试工具
- **selenium**: UI 自动化测试

### 性能测试
- **pytest-benchmark**: 性能基准测试
- **memory_profiler**: 内存分析

---

## 📌 注意事项

1. **API Key 安全**: 不要在测试代码中硬编码 API Key
2. **模拟测试**: 单元测试应该使用 mock，避免真实 API 调用
3. **测试隔离**: 每个测试应该独立，不依赖其他测试
4. **清理资源**: 测试后清理临时文件和资源
5. **文档同步**: 测试通过后更新相关文档

---

## 🎯 测试优先级

### P0 (必须通过)
- 所有模块导入测试
- PromptOptimizer 初始化
- Streamlit 应用启动

### P1 (重要)
- LLMService 功能测试
- ResponseParser 功能测试
- 基本优化流程

### P2 (可选)
- 性能测试
- 边界情况测试
- 压力测试
