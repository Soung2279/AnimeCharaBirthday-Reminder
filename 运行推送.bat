@echo off
title 自动运行推送服务-pushmain_cloud.py
echo 正在运行Python脚本...

:: 设置Python路径（如果python命令不在系统PATH中，可以指定完整路径）
set PYTHON_PATH=python

:: 设置脚本路径
set SCRIPT_PATH="pushmain_cloud.py"

:: 检查Python是否可用
%PYTHON_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python或Python未添加到系统PATH
    pause
    exit /b 1
)

:: 检查脚本文件是否存在
if not exist %SCRIPT_PATH% (
    echo 错误：脚本文件不存在 - %SCRIPT_PATH%
    pause
    exit /b 1
)

:: 运行脚本
echo 正在执行: %PYTHON_PATH% %SCRIPT_PATH%
%PYTHON_PATH% %SCRIPT_PATH%

:: 根据脚本退出代码处理
if %errorlevel% equ 0 (
    echo 脚本执行成功！
) else (
    echo 脚本执行失败，错误代码: %errorlevel%
)

pause