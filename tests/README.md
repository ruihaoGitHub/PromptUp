# Tests 脚本与验证

本目录以“可运行脚本”为主，用于验证 API 连通性、对比算法效果、以及做简单的安全检查。

说明：这些脚本不会被 `app.py`/UI 在运行时自动调用；它们的定位是“评审可复现的自检工具”和“演示/截图证据生成器”。

如果你只想快速确认仓库没有语法/导入错误：

```bash
python -m compileall .
```

## ✅ 可用脚本（以目录实际文件为准）

### 1) tests/test_nvidia.py（需要 API Key）
验证 NVIDIA AI Endpoints 是否可用，并跑一次最小优化链路。

```bash
python tests/test_nvidia.py
```

### 2) tests/compare_algorithms.py（需要 API Key）
随机搜索 vs 遗传算法对比，输出对比图 `algorithm_comparison.png`。

```bash
python tests/compare_algorithms.py
```

### 3) tests/check_api_security.py（不需要 API Key）
扫描代码中是否存在硬编码 key、泄露风险等。

```bash
python tests/check_api_security.py
```

---

## 🧹 清理说明

- 本目录不保留历史生成物（例如旧的 baseline 报告、临时日志）。
- 如果你需要产出报告/截图，建议在项目根目录单独保存，并避免提交到仓库。
