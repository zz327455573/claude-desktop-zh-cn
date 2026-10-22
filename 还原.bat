@echo off
chcp 65001 >nul
REM ============================================================
REM  Claude Desktop 简体中文汉化 — 一键还原
REM  双击即用。把被汉化脚本改过的文件恢复成官方原版。
REM ============================================================
cd /d "%~dp0"

echo.
echo ============================================
REM   还原官方原版
REM ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo 没有检测到 Python，无法运行还原脚本。
    echo 请先安装 Python：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo 本操作会把以下内容恢复成官方原版：
echo   - 语言包文件（zh-Hans.json / zh-CN.json / dynamic 下的两个）
echo   - JS 里的语言白名单
echo   - Claude-3p\config.json 的 locale 设置
echo.
echo 还原后界面会变回英文。
echo.

set /p confirm=确定要还原吗？输入 Y 然后回车继续，直接回车取消:
if /i not "%confirm%"=="Y" (
    echo 已取消。
    echo.
    pause
    exit /b 0
)

echo.
python tools\restore.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo   还原失败，请看上面的错误信息
    echo ============================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   已还原成官方原版。
echo   请退出 Claude Desktop（托盘右键 -^> 退出）
echo   再打开，界面就是英文了。
echo ============================================
echo.
pause
