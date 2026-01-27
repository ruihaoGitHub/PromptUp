@echo off
chcp 65001 > nul
echo ========================================
echo   AI Prompt 自动优化系统
echo ========================================
echo.

REM 检查 .env 文件
if not exist .env (
    echo [警告] 未找到 .env 文件
    echo 正在从 .env.example 创建...
    copy .env.example .env > nul
    echo.
    echo ✓ 已创建 .env 文件
    echo 请编辑 .env 文件，填入你的 NVIDIA_API_KEY
    echo.
    pause
    exit /b
)

REM 检查是否在虚�拟环境中
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo [提示] 建议在虚拟环境中运行
    echo.
)

echo [检查依赖包...]
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [启动应用...]
echo.
echo 浏览器会自动打开 http://localhost:8501
echo 按 Ctrl+C 停止服务
echo.
echo ========================================
streamlit run app.py

pause
