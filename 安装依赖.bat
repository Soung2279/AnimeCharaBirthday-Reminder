@echo off
title 自动安装Python依赖
echo 正在检查并安装依赖...

:: 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo 错误：未找到 requirements.txt 文件！
    pause
    exit /b 1
)

:: 检查pip是否可用
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到pip，请确保Python已正确安装并添加到PATH
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo 依赖安装成功！
) else (
    echo 依赖安装失败，请检查网络或依赖配置！
)

pause