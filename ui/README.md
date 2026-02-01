# UI 组件模块

UI 组件模块提供可复用的 Streamlit 界面组件，包括样式、侧边栏配置等。

## 📁 模块结构

```
ui/
├── __init__.py          # 模块导出
├── styles.py            # CSS 样式和页面配置
├── sidebar.py           # 侧边栏配置面板
└── README.md            # 本文档
```

## 🎨 styles.py - 样式模块

### 功能
- 页面配置（标题、图标、布局）
- 自定义 CSS 样式（渐变标题、按钮、徽章等）
- 单选按钮样式优化

### 使用方法

```python
from ui import apply_custom_styles

# 在 app.py 开头调用（必须在其他 Streamlit 组件之前）
apply_custom_styles()
```

### 提供的样式类
- `.main-header` - 渐变主标题
- `.sub-header` - 副标题
- `.technique-badge` - 技术徽章（蓝色）
- `.keyword-badge` - 关键词徽章（黄色）
- `.stButton>button` - 渐变按钮样式

## ⚙️ sidebar.py - 侧边栏配置

### 功能
- 任务类型选择（生成/分类/摘要/翻译）
- API 提供商选择（NVIDIA/OpenAI）
- API Key 配置与验证
- 模型选择
- 使用说明和示例展示

### 使用方法

```python
from ui import render_sidebar

# 渲染侧边栏并获取用户配置
config = render_sidebar()

# config 结构：
# {
#     'task_type': str,      # 任务类型
#     'api_provider': str,   # API 提供商
#     'api_key': str,        # API Key
#     'base_url': str,       # API 端点
#     'model': str           # 模型名称
# }
```

### 内部函数
- `_render_nvidia_config()` - NVIDIA API 配置界面
- `_render_openai_config()` - OpenAI API 配置界面
- `_render_usage_guide()` - 使用说明
- `_render_examples()` - 示例 Prompt

## 📊 优化效果

通过将 UI 相关代码提取到独立模块：
- **app.py**：313 行 → 75 行（-238 行，-76.0%）
- **提取代码**：312 行（ui 模块）
- **净减少**：74 行（通过组件化和代码复用）

## 🔧 扩展建议

### 添加新的样式主题
在 `styles.py` 中添加新的 CSS 类或主题函数。

### 添加新的配置选项
在 `sidebar.py` 的 `render_sidebar()` 中添加新的配置控件，并在返回的 dict 中包含新配置。

### 创建新的 UI 组件
1. 在 `ui/` 目录下创建新的 `.py` 文件
2. 在 `__init__.py` 中导出新组件
3. 在 `app.py` 中导入使用

## 💡 最佳实践

1. **样式独立**：保持样式与业务逻辑分离
2. **配置集中**：所有用户配置通过 sidebar 统一管理
3. **返回字典**：组件返回结构化的配置字典，便于使用
4. **内部函数**：使用 `_` 前缀标记内部函数，不导出到 `__init__.py`
5. **文档字符串**：为每个公开函数提供清晰的文档

## 🎯 设计原则

- **单一职责**：每个模块只负责一类 UI 组件
- **高内聚**：相关的样式和配置放在一起
- **低耦合**：组件之间相互独立，可以单独使用
- **可复用**：组件设计为通用的，可在不同页面复用
