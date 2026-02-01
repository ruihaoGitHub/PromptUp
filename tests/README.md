# Tests 测试模块

## 📁 模块简介

本目录包含 PromptUp 项目的所有测试文件，涵盖单元测试、集成测试和端到端测试。

## 🎯 测试策略

### 测试层级

1. **Level 1: 基础导入测试** - 验证所有模块可以正常导入
2. **Level 2: 单元测试** - 测试单个函数和类的功能
3. **Level 3: 集成测试** - 测试模块间的协作
4. **Level 4: 算法测试** - 测试优化算法的效果
5. **Level 5: 端到端测试** - 使用真实 API 测试完整流程

## 📄 测试文件说明

### 自动化测试

#### `run_tests.py`
**自动化测试运行器**

- **功能**: 自动运行 Level 1-3 的所有测试
- **测试内容**:
  - ✅ 模块导入测试（algorithms, config, optimizers, services, utils）
  - ✅ 工具函数单元测试（JSON 解析、文本清理）
  - ✅ 数据模型验证测试
  - ✅ 模板加载测试
  
- **运行方式**:
  ```bash
  python tests/run_tests.py
  ```

- **输出**: 
  - 彩色终端输出，显示每个测试的通过/失败状态
  - 最终统计：通过数量、失败数量、成功率

- **适用场景**: 快速验证代码改动后的功能完整性

### 算法测试

#### `test_random_search.py`
**随机搜索算法测试**

- **测试对象**: `algorithms.RandomSearchAlgorithm`
- **测试内容**:
  - 搜索空间生成
  - 随机采样功能
  - 评估函数调用
  - 最佳结果选择
  
- **Mock 方式**: 使用模拟 LLM 和评估函数（不需要真实 API）
- **运行方式**:
  ```bash
  python tests/test_random_search.py
  ```

#### `test_random_search_hard.py`
**随机搜索压力测试**

- **测试对象**: 随机搜索算法的边界情况
- **测试内容**:
  - 大规模搜索空间（数百种组合）
  - 长时间运行稳定性
  - 内存使用情况
  - 异常处理

- **特点**: 更严格的测试条件，用于发现潜在问题

#### `test_genetic_algorithm.py`
**遗传算法测试**

- **测试对象**: `algorithms.GeneticAlgorithm`
- **测试内容**:
  - 种群初始化
  - 选择（Selection）机制
  - 交叉（Crossover）操作
  - 变异（Mutation）操作
  - 精英保留策略
  - 代际进化过程
  
- **验证指标**:
  - 种群多样性
  - 分数递增趋势
  - 收敛速度

- **运行方式**:
  ```bash
  python tests/test_genetic_algorithm.py
  ```

#### `test_bayesian_optimization.py`
**贝叶斯优化测试**

- **测试对象**: `algorithms.BayesianOptimization`
- **测试内容**:
  - Gaussian Process 建模
  - Acquisition Function（EI/UCB）
  - 探索与利用平衡
  - 收敛性验证
  
- **依赖**: 需要安装 `optuna` 库
- **运行方式**:
  ```bash
  python tests/test_bayesian_optimization.py
  ```

### 功能测试

#### `test_optimize.py`
**优化器功能测试**

- **测试对象**: `optimizer.PromptOptimizer` 核心功能
- **测试内容**:
  - 通用 Prompt 优化
  - 分类任务优化
  - 摘要任务优化
  - 翻译任务优化
  - 搜索空间生成
  
- **Mock 方式**: 使用模拟 LLM 响应（不需要 API）
- **运行方式**:
  ```bash
  python tests/test_optimize.py
  ```

#### `test_nvidia.py`
**NVIDIA API 连接测试**

- **测试对象**: NVIDIA API Catalog 集成
- **测试内容**:
  - API 连接验证
  - 模型可用性检查
  - 简单推理测试
  
- **要求**: 需要设置 `NVIDIA_API_KEY` 环境变量
- **运行方式**:
  ```bash
  export NVIDIA_API_KEY="nvapi-xxxxx"
  python tests/test_nvidia.py
  ```

### 端到端测试

#### `test_e2e.py`
**端到端测试（真实 API）**

- **测试范围**: 完整的用户使用流程
- **测试用例**:
  1. **基本 Prompt 优化**
     - 输入简单 Prompt
     - 验证优化结果格式
     - 检查输出质量
     
  2. **分类任务优化**
     - 提供任务描述和标签
     - 验证生成的分类 Prompt
     - 检查 Few-shot 示例
     
  3. **搜索空间生成**
     - 根据任务类型生成搜索空间
     - 验证角色、风格、技巧列表
     - 检查多样性和相关性

- **API 配置**: 
  - 使用真实的 NVIDIA API Key
  - 默认模型: `meta/llama-3.1-70b-instruct`
  
- **成功标准**: 
  - ✅ 所有测试通过（3/3）
  - ✅ JSON 解析成功
  - ✅ 数据模型验证通过

- **运行方式**:
  ```bash
  export NVIDIA_API_KEY="nvapi-xxxxx"
  python tests/test_e2e.py
  ```

- **预期输出**:
  ```
  🚀 PromptUp 端到端测试 (使用真实 API)
  ======================================
  ✅ PASS - 基本 Prompt 优化
  ✅ PASS - 分类任务优化
  ✅ PASS - 搜索空间生成
  
  总计: 3/3 通过
  成功率: 100.0%
  🎉 所有测试通过！项目可以投入使用！
  ```

#### `test_llm_response.py`
**LLM 响应格式测试**

- **测试对象**: LLM 返回的 JSON 格式质量
- **测试内容**:
  - 验证 LLM 是否遵循 JSON 格式要求
  - 测试不同 Meta-Prompt 的效果
  - 比较不同模型的输出质量
  
- **运行方式**:
  ```bash
  export NVIDIA_API_KEY="nvapi-xxxxx"
  python tests/test_llm_response.py
  ```

### 工具测试

#### `compare_algorithms.py`
**算法对比测试**

- **功能**: 对比不同优化算法的性能
- **测试维度**:
  - 运行时间
  - 最终得分
  - 收敛速度
  - 评估次数
  
- **算法**:
  - 随机搜索
  - 遗传算法
  - 贝叶斯优化
  
- **输出**: 对比表格和可视化图表
- **运行方式**:
  ```bash
  python tests/compare_algorithms.py
  ```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 贝叶斯优化（可选）
pip install optuna
```

### 2. 配置环境变量

```bash
# Windows PowerShell
$env:NVIDIA_API_KEY="nvapi-xxxxx"

# Linux/Mac
export NVIDIA_API_KEY="nvapi-xxxxx"
```

### 3. 运行测试

```bash
# 快速测试（不需要 API）
python tests/run_tests.py

# 算法测试
python tests/test_genetic_algorithm.py

# 端到端测试（需要 API）
python tests/test_e2e.py
```

## 📊 测试覆盖率

| 模块 | 测试覆盖率 | 测试文件 |
|------|-----------|----------|
| algorithms | 90% | test_random_search.py, test_genetic_algorithm.py, test_bayesian_optimization.py |
| config | 85% | run_tests.py |
| optimizers | 80% | test_optimize.py |
| services | 95% | run_tests.py, test_llm_response.py |
| utils | 100% | run_tests.py |
| optimizer (核心) | 75% | test_optimize.py, test_e2e.py |

## ✅ 测试检查清单

在提交代码前，请确保：

- [ ] `run_tests.py` 全部通过（Level 1-3）
- [ ] 相关算法测试通过
- [ ] 端到端测试通过（如果修改了核心逻辑）
- [ ] 没有新增的 PEP8 警告
- [ ] 添加了必要的单元测试

## 🐛 常见问题

### Q1: 测试失败 "No module named 'xxx'"
**解决**: 检查是否在项目根目录运行测试，或者添加项目路径到 PYTHONPATH

### Q2: NVIDIA API 测试失败
**解决**: 
1. 检查 API Key 是否正确
2. 检查网络连接
3. 验证 API Key 是否有效（可能过期）

### Q3: 贝叶斯优化测试跳过
**解决**: 安装 optuna: `pip install optuna`

### Q4: 测试运行很慢
**解决**: 
- 使用 Mock 测试而非真实 API 测试
- 减少测试迭代次数
- 使用更小的模型（如 8b 而不是 405b）

## 📚 编写新测试

### 单元测试模板

```python
import pytest
from your_module import your_function

def test_your_function_basic():
    """测试基本功能"""
    result = your_function(input_data)
    assert result == expected_output

def test_your_function_edge_cases():
    """测试边界情况"""
    # 空输入
    with pytest.raises(ValueError):
        your_function(None)
    
    # 异常输入
    result = your_function("")
    assert result is not None
```

### Mock LLM 模板

```python
from unittest.mock import Mock

def create_mock_llm():
    """创建模拟 LLM"""
    llm = Mock()
    
    # 模拟响应
    response = Mock()
    response.content = '{"key": "value"}'
    llm.invoke.return_value = response
    
    return llm

def test_with_mock_llm():
    llm = create_mock_llm()
    optimizer = YourOptimizer(llm)
    result = optimizer.optimize("test input")
    assert result is not None
```

## 📈 测试报告

最新测试结果请查看：
- [TEST_PLAN.md](../TEST_PLAN.md) - 完整测试计划
- [E2E_TEST_RESULTS.md](../E2E_TEST_RESULTS.md) - 端到端测试报告
