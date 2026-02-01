# 📂 项目结构说明

## 项目目录树

```
PromptUp/
├── 📁 algorithms/          # 优化算法模块
│   ├── search_space.py     # 搜索空间生成器
│   ├── random_search.py    # 随机搜索算法
│   ├── genetic_algorithm.py # 遗传算法
│   ├── bayesian_optimization.py # 贝叶斯优化
│   └── README.md           # 算法模块文档
│
├── 📁 config/              # 配置和数据模型
│   ├── models.py           # Pydantic 数据模型定义
│   ├── template_loader.py  # Meta-Prompt 模板加载器
│   ├── meta_prompts/       # Meta-Prompt 模板文件
│   │   ├── generation.txt
│   │   ├── classification.txt
│   │   ├── summarization.txt
│   │   ├── translation.txt
│   │   └── search_space.txt
│   └── README.md           # 配置模块文档
│
├── 📁 optimizers/          # 任务专用优化器
│   ├── base.py             # 基础优化器抽象类
│   ├── classification.py   # 分类任务优化器
│   ├── summarization.py    # 摘要任务优化器
│   ├── translation.py      # 翻译任务优化器
│   └── README.md           # 优化器模块文档
│
├── 📁 services/            # 服务层
│   ├── llm_service.py      # LLM 创建和管理服务
│   ├── response_parser.py  # 响应解析服务
│   └── README.md           # 服务层文档
│
├── 📁 utils/               # 工具函数
│   ├── json_parser.py      # JSON 解析工具
│   ├── text_cleaner.py     # 文本清理工具
│   ├── prompt_replacer.py  # 占位符替换工具
│   └── README.md           # 工具模块文档
│
├── 📁 ui/                  # UI 组件
│   ├── styles.py           # 样式定义
│   ├── sidebar.py          # 侧边栏组件
│   └── README.md           # UI 模块文档
│
├── 📁 pages/               # Streamlit 页面
│   ├── base_page.py        # 基础页面类
│   ├── generation_page.py  # 通用优化页面
│   ├── classification_page.py # 分类任务页面
│   ├── summarization_page.py  # 摘要任务页面
│   ├── translation_page.py    # 翻译任务页面
│   ├── page_manager.py     # 页面管理器
│   └── README.md           # 页面模块文档
│
├── 📁 tests/               # 测试文件
│   ├── run_tests.py        # 自动化测试运行器
│   ├── test_e2e.py         # 端到端测试
│   ├── test_optimize.py    # 优化器测试
│   ├── test_genetic_algorithm.py
│   ├── test_bayesian_optimization.py
│   ├── test_random_search.py
│   ├── test_random_search_hard.py
│   ├── test_nvidia.py      # NVIDIA API 测试
│   ├── test_llm_response.py
│   ├── compare_algorithms.py # 算法对比
│   └── README.md           # 测试模块文档
│
├── 📄 核心文件
│   ├── app.py              # Streamlit 主应用入口
│   ├── optimizer.py        # 核心优化器（统一接口）
│   ├── templates.py        # 优化策略模板
│   ├── metrics.py          # 评估指标函数
│   └── nvidia_models.py    # NVIDIA 模型列表
│
├── 📄 配置文件
│   ├── requirements.txt    # Python 依赖
│   ├── .env.example        # 环境变量示例
│   ├── .gitignore          # Git 忽略规则
│   └── start.bat           # Windows 启动脚本
│
└── 📄 文档文件
    ├── README.md           # 项目主文档
    ├── Architecture.md     # 架构设计文档
    ├── REFACTORING_LOG.md # 重构日志
    ├── TEST_PLAN.md        # 测试计划
    ├── E2E_TEST_RESULTS.md # 端到端测试报告
    ├── 遗传算法使用指南.md
    ├── 遗传算法实现总结.md
    └── 贝叶斯优化说明.md
```

## 📚 模块详细说明

### 1️⃣ algorithms/ - 优化算法模块
**作用**: 提供 Prompt 自动优化的核心算法

**主要文件**:
- `search_space.py`: 使用 LLM 生成搜索空间（角色、风格、技巧）
- `random_search.py`: 随机搜索算法，快速探索搜索空间
- `genetic_algorithm.py`: 遗传算法，通过选择、交叉、变异优化 Prompt
- `bayesian_optimization.py`: 贝叶斯优化，使用概率模型智能选择

**详细文档**: [algorithms/README.md](algorithms/README.md)

---

### 2️⃣ config/ - 配置和数据模型
**作用**: 管理配置、定义数据结构、加载模板

**主要文件**:
- `models.py`: 定义所有 Pydantic 数据模型（OptimizedPrompt, ClassificationPrompt 等）
- `template_loader.py`: 从外部文件加载 Meta-Prompt 模板
- `meta_prompts/`: 存储所有 Meta-Prompt 文本模板

**详细文档**: [config/README.md](config/README.md)

---

### 3️⃣ optimizers/ - 任务专用优化器
**作用**: 为不同任务类型提供专门的优化逻辑

**主要文件**:
- `base.py`: 基础优化器抽象类，提供通用功能
- `classification.py`: 分类任务优化器
- `summarization.py`: 摘要任务优化器
- `translation.py`: 翻译任务优化器

**详细文档**: [optimizers/README.md](optimizers/README.md)

---

### 4️⃣ services/ - 服务层
**作用**: 提供 LLM 调用、响应解析等核心服务

**主要文件**:
- `llm_service.py`: LLM 实例创建和管理（支持 NVIDIA/OpenAI）
- `response_parser.py`: 解析 LLM 响应，提取 JSON，清理文本

**详细文档**: [services/README.md](services/README.md)

---

### 5️⃣ utils/ - 工具函数
**作用**: 提供通用工具函数

**主要文件**:
- `json_parser.py`: 安全的 JSON 解析（支持非标准格式）
- `text_cleaner.py`: 文本清理和规范化
- `prompt_replacer.py`: Prompt 占位符替换

**详细文档**: [utils/README.md](utils/README.md)

---

### 6️⃣ ui/ - UI 组件
**作用**: Streamlit 应用的 UI 组件

**主要文件**:
- `styles.py`: CSS 样式定义和主题配置
- `sidebar.py`: 侧边栏组件（API 配置、模型选择）

**详细文档**: [ui/README.md](ui/README.md)

---

### 7️⃣ pages/ - Streamlit 页面
**作用**: 多页面应用的页面实现

**主要文件**:
- `base_page.py`: 基础页面类
- `generation_page.py`: 通用 Prompt 优化页面
- `classification_page.py`: 分类任务页面
- `summarization_page.py`: 摘要任务页面
- `translation_page.py`: 翻译任务页面
- `page_manager.py`: 页面路由管理

**详细文档**: [pages/README.md](pages/README.md)

---

### 8️⃣ tests/ - 测试模块
**作用**: 包含所有测试文件

**主要文件**:
- `run_tests.py`: 自动化测试运行器（Level 1-3）
- `test_e2e.py`: 端到端测试（使用真实 API）
- `test_*.py`: 各模块的单元测试
- `compare_algorithms.py`: 算法性能对比

**详细文档**: [tests/README.md](tests/README.md)

---

## 🗂️ 核心文件说明

### app.py
**Streamlit 主应用入口**

- 加载 UI 样式和组件
- 渲染侧边栏配置
- 管理页面路由
- 协调所有模块

### optimizer.py
**核心优化器（统一接口）**

- `PromptOptimizer` 类：整合所有优化功能
- 提供统一的 API 接口
- 协调各个专用优化器
- 集成搜索算法

**主要方法**:
- `optimize()`: 通用 Prompt 优化
- `optimize_classification()`: 分类任务优化
- `optimize_summarization()`: 摘要任务优化
- `optimize_translation()`: 翻译任务优化
- `generate_search_space()`: 生成搜索空间
- `optimize_with_search()`: 使用搜索算法优化

### templates.py
**优化策略模板**

- 定义各种优化框架（CO-STAR, BROKE, CRISPE 等）
- 存储优化原则字典
- 提供场景到策略的映射

### metrics.py
**评估指标函数**

- 定义 Prompt 评估指标
- 提供评估函数接口
- 用于搜索算法的目标函数

### nvidia_models.py
**NVIDIA 模型列表**

- 列出所有可用的 NVIDIA 模型
- 提供模型元数据（参数量、上下文长度等）

---

## 🔗 模块依赖关系

```
┌─────────────────────────────────────────────┐
│              app.py (入口)                   │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │ ui/     │  │ pages/   │  │ optimizer │  │
│  │ styles  │  │ 页面模块  │  │  .py     │  │
│  │ sidebar │  │          │  │           │  │
│  └─────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │   optimizer.PromptOptimizer │
        └────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        │                         │
   ┌─────────┐            ┌────────────┐
   │optimizers/│            │ algorithms/│
   │  专用优化器│            │  搜索算法   │
   └─────────┘            └────────────┘
        │                         │
        ├─────────────┬───────────┤
        │             │           │
   ┌─────────┐  ┌──────────┐  ┌──────┐
   │services/│  │ config/  │  │utils/│
   │  服务层  │  │ 配置模型  │  │ 工具 │
   └─────────┘  └──────────┘  └──────┘
```

**依赖说明**:
- **app.py** → ui, pages, optimizer
- **pages** → optimizer, ui
- **optimizer** → optimizers, algorithms, services
- **optimizers** → services, config, utils
- **algorithms** → services, config
- **services** → utils

---

## 🚀 快速导航

### 想了解如何使用？
→ 查看主 [README.md](README.md)

### 想了解架构设计？
→ 查看 [Architecture.md](Architecture.md)

### 想运行测试？
→ 查看 [tests/README.md](tests/README.md)

### 想开发新功能？
根据功能类型查看对应模块的 README：
- 添加新算法 → [algorithms/README.md](algorithms/README.md)
- 添加新任务类型 → [optimizers/README.md](optimizers/README.md)
- 修改 UI → [ui/README.md](ui/README.md)
- 添加新页面 → [pages/README.md](pages/README.md)

---

## 📊 代码统计

| 模块 | 文件数 | 代码行数 | 功能 |
|------|--------|---------|------|
| algorithms | 4 | ~800 | 搜索算法实现 |
| config | 2 + 5 模板 | ~400 | 配置和模型 |
| optimizers | 4 | ~600 | 任务优化器 |
| services | 2 | ~300 | 服务层 |
| utils | 3 | ~500 | 工具函数 |
| ui | 2 | ~400 | UI 组件 |
| pages | 6 | ~800 | 页面实现 |
| 核心文件 | 5 | ~600 | 主逻辑 |
| **总计** | **28+** | **~4400** | - |

---

## 🎯 开发规范

### 文件命名
- 模块文件：小写 + 下划线（`genetic_algorithm.py`）
- 类名：大驼峰（`GeneticAlgorithm`）
- 函数名：小写 + 下划线（`generate_search_space`）

### 文档规范
- 每个模块都有 README.md
- 每个函数都有 docstring
- 复杂逻辑添加注释

### 测试规范
- 新功能必须有对应测试
- 测试文件命名：`test_*.py`
- 所有测试放在 `tests/` 目录

---

## 📮 相关资源

- **项目仓库**: [GitHub 链接]
- **问题反馈**: [Issues 链接]
- **文档站点**: [文档链接]
- **API 文档**: [API 文档链接]
