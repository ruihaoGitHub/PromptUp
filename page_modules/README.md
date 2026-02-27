# page_modules 页面模块

本模块用于将 Streamlit 的页面逻辑模块化：每个任务（生成/分类/摘要/翻译）各自维护 UI、验证实验室、以及搜索算法实验区。

## 📁 当前结构（以仓库实际为准）

```
page_modules/
├── __init__.py
├── base_page.py
├── generation_page.py
├── classification_page.py
├── summarization_page.py
├── translation_page.py
└── page_manager.py
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

`page_manager.py` 提供了一个通用的“注册/路由”实现，但当前主入口 [app.py](../app.py) 采用更直接的方式：根据侧边栏选择的任务类型，实例化对应 Page 类并调用 `render()`。

## 使用示例

```python
from page_modules import GenerationPage

page = GenerationPage(optimizer)
page.render()
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
