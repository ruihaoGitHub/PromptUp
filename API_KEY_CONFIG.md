# API Key 配置说明

## 📋 API Key 配置的两种方式

### 方式 1：在 .env 文件中配置（推荐）

**优点**：
- ✅ 配置一次，永久有效
- ✅ Streamlit 应用和测试脚本都能使用
- ✅ 不需要每次都输入

**步骤**：
1. 编辑 `.env` 文件
2. 填入你的 API Key：
   ```env
   NVIDIA_API_KEY=nvapi-你的真实key
   ```
3. 保存文件
4. 重启应用或脚本

**适用场景**：
- ✅ `streamlit run app.py` - Streamlit 应用
- ✅ `python test_nvidia.py` - 测试脚本
- ✅ `python examples.py` - 示例脚本

### 方式 2：在 Streamlit 界面中输入

**优点**：
- ✅ 临时使用，不保存到文件
- ✅ 可以快速切换不同的 API Key
- ✅ 适合演示或测试

**步骤**：
1. 运行 `streamlit run app.py`
2. 在侧边栏的输入框中输入 API Key
3. 点击优化按钮

**限制**：
- ❌ 只在 Streamlit 应用中有效
- ❌ test_nvidia.py 和 examples.py 无法使用
- ❌ 每次重新打开应用需要重新输入

## 🔄 两种方式的关系

### 配置优先级

```
Streamlit 界面输入 > .env 文件配置
```

- 如果 `.env` 文件中有配置，Streamlit 会自动读取并显示
- 如果在界面中输入新的 Key，会**覆盖** .env 中的配置（仅本次有效）

### 实际表现

| 情况 | .env 文件 | Streamlit 输入 | 最终使用 |
|-----|----------|---------------|---------|
| 1 | 有 Key | 未输入 | .env 中的 Key |
| 2 | 有 Key | 输入新 Key | 新输入的 Key |
| 3 | 无 Key | 输入 Key | 输入的 Key |
| 4 | 无 Key | 未输入 | ❌ 报错 |

## 🎯 推荐的配置流程

### 第一次使用

1. **获取 API Key**
   ```
   访问 https://build.nvidia.com/
   → 登录 → 选择任意模型 → Get API Key
   ```

2. **配置到 .env 文件**
   ```bash
   # 编辑 .env 文件
   NVIDIA_API_KEY=nvapi-你的key
   ```

3. **测试连接**
   ```bash
   python test_nvidia.py
   ```
   
   如果看到 ✅ 连接成功，说明配置正确。

4. **启动应用**
   ```bash
   streamlit run app.py
   ```
   
   应该能看到 "✅ 已从 .env 文件读取 API Key"

### 临时使用不同的 Key

如果你想临时测试另一个 API Key：

1. 直接在 Streamlit 界面输入新的 Key
2. 点击优化按钮
3. 本次会话使用新的 Key
4. 下次打开应用仍然使用 .env 中的 Key

## 🐛 常见问题

### Q: 为什么在 Streamlit 中填了 Key，运行 test_nvidia.py 还是失败？

**原因**：Streamlit 界面中输入的 Key 只存在于内存中，不会保存到 .env 文件。

**解决方案**：
```bash
# 将 Key 添加到 .env 文件
echo "NVIDIA_API_KEY=nvapi-你的key" >> .env

# 或者手动编辑 .env 文件
```

### Q: 我修改了 .env 文件，Streamlit 界面没有更新？

**原因**：Streamlit 在启动时读取环境变量，运行中不会自动刷新。

**解决方案**：
```bash
# 停止 Streamlit (Ctrl+C)
# 重新启动
streamlit run app.py
```

### Q: .env 文件和 .env.example 有什么区别？

- `.env.example` - 模板文件，给其他人参考用，不包含真实密钥
- `.env` - 实际配置文件，包含你的真实密钥，**不应该提交到 Git**

## 💡 最佳实践

### ✅ 推荐做法

1. **生产环境**：
   ```
   在 .env 文件中配置
   不要在代码中硬编码
   ```

2. **开发测试**：
   ```
   先配置 .env 文件
   运行 test_nvidia.py 验证
   再启动 Streamlit 应用
   ```

3. **团队协作**：
   ```
   .env 添加到 .gitignore
   分享 .env.example 给队友
   每人配置自己的 .env
   ```

### ❌ 不推荐做法

1. ❌ 在代码中硬编码 API Key
2. ❌ 将 .env 文件提交到 Git
3. ❌ 只在 Streamlit 界面配置（测试脚本无法使用）
4. ❌ 使用不安全的 Key 存储方式

## 🔧 验证配置是否正确

```bash
# 1. 检查 .env 文件
cat .env | grep NVIDIA_API_KEY

# 2. 测试 API 连接
python test_nvidia.py

# 3. 启动应用
streamlit run app.py
```

如果三步都成功，说明配置完全正确！🎉
