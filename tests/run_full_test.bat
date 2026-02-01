@echo off
chcp 65001 > nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                  PromptUp UI 自动化测试套件                       ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM 激活 conda 环境
call conda activate promptup

REM 运行自动化测试
python tests\test_ui_automation.py

REM 保持窗口打开
echo.
echo 按任意键关闭窗口...
pause > nul
