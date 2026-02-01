# Pages 模块

## 模块说明

此模块用于将 Streamlit UI 组件模块化，将大型 app.py 拆分为独立的页面模块。

## 当前结构

```
pages/
├── __init__.py          # 模块导出
├── base_page.py         # 页面基类
├── page_manager.py      # 页面管理器
└── README.md            # 本文件
```

## 页面基类 (BasePage)

所有页面都继承自 `BasePage`，提供以下通用功能：

- `render()`: 渲染页面内容（子类必须实现）
- `show_thinking_process()`: 显示 AI 思考过程
- `show_techniques()`: 显示优化技术
- `show_keywords()`: 显示新增关键词
- `show_error()`: 显示错误信息
- `show_success()`: 显示成功信息
- `create_two_columns()`: 创建两列布局
- `create_tabs()`: 创建标签页

## 页面管理器 (PageManager)

负责页面注册和路由：

```python
from pages import page_manager

# 注册页面
page_manager.register_page("生成任务", GenerationPage)
page_manager.register_page("分类任务", ClassificationPage)

# 渲染页面
page_manager.render_page("生成任务", optimizer)
```

## 后续重构计划

### 待创建的页面模块

1. **generation_page.py** - 通用 Prompt 生成页面
   - 功能：用户输入原始 Prompt，系统优化输出
   - 预计：~300 行

2. **classification_page.py** - 分类任务优化页面
   - 功能：输入任务描述和标签，生成分类 Prompt
   - 预计：~250 行

3. **summarization_page.py** - 摘要任务优化页面
   - 功能：输入文本类型和摘要要求，生成摘要 Prompt
   - 预计：~250 行

4. **translation_page.py** - 翻译任务优化页面
   - 功能：输入语言对和领域，生成翻译 Prompt
   - 预计：~250 行

5. **lab_page.py** - 实验室页面
   - 功能：搜索算法实验（随机搜索、遗传算法、贝叶斯优化）
   - 预计：~400 行

### 预期收益

- **app.py**: 从 2162 行减少到 ~300 行（-86%）
- **新增代码**: ~1450 行（分散在 5 个页面文件）
- **净减少**: ~400 行
- **可维护性**: 大幅提升，每个页面独立开发和测试

## 使用示例

```python
# 在 app.py 中
from pages import page_manager
from pages.generation_page import GenerationPage
from pages.classification_page import ClassificationPage

# 注册所有页面
page_manager.register_page("生成任务", GenerationPage)
page_manager.register_page("分类任务", ClassificationPage)
# ... 注册其他页面

# 根据任务类型渲染对应页面
task_type = st.radio("任务类型", ["生成任务", "分类任务", ...])
page_manager.render_page(task_type, optimizer)
```

## 设计原则

1. **单一职责**: 每个页面只负责一种任务类型的 UI
2. **可复用**: 通用功能放在基类中
3. **可测试**: 页面逻辑独立于 app.py，便于单元测试
4. **可扩展**: 新增页面只需继承 BasePage 并注册

## 注意事项

- 页面类需要接受 `optimizer` 参数（PromptOptimizer 实例）
- 页面之间的数据通过 `st.session_state` 共享
- 样式定义仍保留在 app.py 中（全局生效）
