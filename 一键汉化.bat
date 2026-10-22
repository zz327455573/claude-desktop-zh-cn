@echo off
chcp 65001 >nul
REM ============================================================
REM  Claude Desktop 简体中文汉化 — 一键安装
REM  双击这个文件就行，不需要敲任何命令。
REM ============================================================
cd /d "%~dp0"

echo.
echo ============================================
echo   Claude Desktop 简体中文汉化
echo ============================================
echo.

REM --- 1. 检查 Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [1/3] 没有检测到 Python，需要先装一个。
    echo.
    echo     Python 是运行汉化脚本必需的程序，装一次以后都能用。
    echo.
    echo     请按步骤操作：
    echo       1. 打开这个网址下载： https://www.python.org/downloads/
    echo       2. 下载页面点黄色按钮 "Download Python 3.x.x"
    echo       3. 运行下载好的安装包
    echo       4. **重要**：安装第一个界面下方有个勾选框
    echo          "Add python.exe to PATH"，一定要打上勾，再点 Install
    echo       5. 装完后关掉这个窗口，重新双击本文件
    echo.
    echo     网址已尝试帮你打开...
    start https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] Python 已就绪

REM --- 2. 检查 Claude 是否在运行 ---
tasklist /fi "imagename eq claude.exe" 2>nul | find /i "claude.exe" >nul
if not errorlevel 1 (
    echo.
    echo [注意] Claude Desktop 正在运行。
    echo.
    echo        汉化要改写程序文件，运行中改可能会失败或丢失。
    echo        请先右键点击屏幕右下角托盘区的 Claude 图标，
    echo        选择"退出"，然后再回来双击本文件。
    echo.
    echo        如果你确认已经退出，按任意键继续...
    pause >nul
)

echo [2/3] 开始汉化...
echo.

python tools\install.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo   汉化失败，请看上面的红色错误信息
    echo ============================================
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] 全部完成
echo.
echo ============================================
echo   汉化成功！现在打开 Claude Desktop，
echo   如果界面还是英文，就彻底退出
echo   ^(托盘右键 -^> 退出^) 再打开一次。
echo ============================================
echo.
pause
