# Algorithms 模块

## 📁 模块简介

本模块包含 Prompt 优化的核心算法实现，负责在搜索空间中自动探索和优化 Prompt 组合。

## 🎯 核心功能

- **搜索空间生成**：定义 Prompt 优化的可选维度（角色、风格、技巧）
- **随机搜索**：通过随机采样快速探索搜索空间
- **遗传算法**：模拟生物进化，通过选择、交叉、变异迭代优化 Prompt
- **贝叶斯优化**：使用概率模型智能选择最有潜力的 Prompt 组合

## 📄 文件说明

### `search_space.py`
**搜索空间生成器**

- **类**: `SearchSpaceGenerator`
- **功能**: 使用 LLM 生成搜索空间（角色列表、风格列表、技巧列表）
- **输入**: 任务类型、任务描述
- **输出**: `SearchSpace` 对象，包含 roles、styles、techniques
- **应用**: 为所有优化算法提供搜索维度

### `random_search.py`
**随机搜索算法**

- **类**: `RandomSearchAlgorithm`
- **功能**: 从搜索空间中随机采样 Prompt 组合并评估
- **参数**:
  - `n_iterations`: 搜索迭代次数（默认 10）
  - `temperature`: LLM 生成温度（影响多样性）
- **优点**: 实现简单，适合快速验证
- **适用场景**: 基线对比、快速原型验证

### `genetic_algorithm.py`
**遗传算法**

- **类**: `GeneticAlgorithm`
- **功能**: 通过模拟自然选择优化 Prompt
- **核心机制**:
  - **选择（Selection）**: 保留高分 Prompt 作为父代
  - **交叉（Crossover）**: 组合两个父代的优势特征
  - **变异（Mutation）**: 引入随机变化避免局部最优
- **参数**:
  - `population_size`: 种群大小（默认 8）
  - `generations`: 进化代数（默认 5）
  - `mutation_rate`: 变异概率（默认 0.3）
  - `elite_size`: 精英保留数量（默认 2）
- **适用场景**: 需要高质量结果的复杂任务

### `bayesian_optimization.py`
**贝叶斯优化**

- **类**: `BayesianOptimization`
- **功能**: 使用 Gaussian Process 建模 Prompt 性能
- **核心机制**:
  - 构建概率代理模型预测未评估 Prompt 的性能
  - 使用 Acquisition Function（EI/UCB）平衡探索与利用
  - 智能选择最有潜力的 Prompt 进行评估
- **参数**:
  - `n_iterations`: 优化迭代次数（默认 15）
  - `n_initial_points`: 初始随机采样点数（默认 5）
  - `acquisition_function`: 采集函数类型（"ei" 或 "ucb"）
- **依赖**: 需要安装 `optuna` 库
- **适用场景**: 评估成本高、需要高效探索的场景

### `__init__.py`
**模块接口**

导出所有算法类，简化外部调用：
```python
from algorithms import SearchSpaceGenerator, RandomSearchAlgorithm, GeneticAlgorithm, BayesianOptimization
```

## 🔗 与其他模块的关系

- **依赖**: 
  - `services.LLMService`: 调用 LLM 生成和评估 Prompt
  - `config.models.SearchSpace`: 搜索空间数据模型
  - `metrics`: 评估 Prompt 性能的指标函数
  
- **被调用**: 
  - `optimizer.PromptOptimizer`: 使用算法进行自动优化

## 📊 算法对比

| 算法 | 速度 | 质量 | 适用场景 |
|------|------|------|----------|
| 随机搜索 | ⭐⭐⭐⭐⭐ | ⭐⭐ | 快速验证、基线对比 |
| 遗传算法 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂任务、高质量要求 |
| 贝叶斯优化 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 评估成本高、样本效率要求高 |

## 📚 使用示例

```python
from algorithms import SearchSpaceGenerator, GeneticAlgorithm

# 1. 生成搜索空间
generator = SearchSpaceGenerator(llm)
search_space = generator.generate(
    task_type="classification",
    task_description="判断电影评论情感"
)

# 2. 使用遗传算法优化
ga = GeneticAlgorithm(
    llm=llm,
    population_size=10,
    generations=8,
    mutation_rate=0.3
)

results = ga.optimize(
    search_space=search_space,
    base_prompt="判断这条评论是正面还是负面",
    eval_function=my_eval_function
)

print(f"最佳 Prompt: {results.best_prompt}")
print(f"最佳得分: {results.best_score}")
```
