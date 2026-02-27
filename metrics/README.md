# Metrics 模块

本目录提供项目的指标评估能力（Accuracy / ROUGE / BLEU）。

## 📁 文件说明

- `__init__.py`
  - 指标实现：`MetricsCalculator`、`ChineseTokenizer`
  - 兼容性说明：项目早期为根目录 `metrics.py`，现迁移为 `metrics/` 包，以保持 `from metrics import MetricsCalculator` 的导入方式不变。

## ✅ 典型用法

```python
from metrics import MetricsCalculator

calc = MetricsCalculator()
score = calc.calculate_accuracy(["a"], ["a"])
```
