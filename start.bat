@echo off
chcp 65001 > nul
echo ========================================
echo   AI Prompt 自动优化系统
echo ========================================
echo.

REM 尝试激活 conda 环境（避免调用到 base 环境的 streamlit/python）
set "CONDA_BAT="
for /f "delims=" %%i in ('where conda.bat 2^>nul') do set "CONDA_BAT=%%i" & goto :conda_bat_found
:conda_bat_found

if defined CONDA_BAT (
    if /I not "%CONDA_DEFAULT_ENV%"=="promptup" (
        call "%CONDA_BAT%" activate promptup >nul 2>&1
        if errorlevel 1 (
            echo [提示] 已检测到 conda，但未能自动激活 promptup。
            echo        建议使用 Anaconda Prompt 打开本目录后运行 start.bat。
            echo.
        )
    )
) else (
    where conda >nul 2>&1
    if %errorlevel%==0 (
        echo [提示] 检测到 conda，但当前终端可能未初始化 conda activate。
        echo        建议使用 Anaconda Prompt/已激活 promptup 环境中运行。
        echo.
    ) else (
        echo [提示] 未检测到 conda 命令。建议先安装 Miniconda/Anaconda，或确保已激活虚拟环境。
        echo.
    )
)

REM 检查 .env 文件
if not exist .env (
    echo [提示] 未找到 .env 文件
    if exist .env.example (
        echo 正在从 .env.example 创建 .env（可选配置）...
        copy .env.example .env > nul
        echo ✓ 已创建 .env 文件
    ) else (
        echo [警告] 未找到 .env.example，将创建一个空的 .env
        echo NVIDIA_API_KEY=>> .env
        echo OPENAI_API_KEY=>> .env
        echo ✓ 已创建空的 .env 文件
    )
    echo.
    echo [说明] 未配置 API Key 也可以启动 UI，但无法运行需要调用大模型的功能。
    echo        你可以在左侧边栏临时粘贴 API Key 后再运行优化/评估。
    echo.
)

REM 检查是否在虚拟环境中
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo [提示] 建议在虚拟环境中运行
    echo.
)

echo [检查依赖包...]
python -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 缺少依赖包，正在安装...
    python -m pip install -r requirements.txt
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
python -m streamlit run app.py

pause
