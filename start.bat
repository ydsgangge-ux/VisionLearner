@echo off
title Autonomous Cognitive Learning System - Language Selection
cls

echo ========================================================================
echo     Autonomous Cognitive Learning System
echo     自主认知学习系统
echo ========================================================================
echo.
echo Please select language / 请选择语言:
echo.
echo   [1] English
echo   [2] 中文 (Chinese)
echo.
set /p choice="Enter your choice / 请输入选择 (1-2): "

if "%choice%"=="1" (
    cls
    echo Starting English version...
    echo.
    call start_en.bat
) else if "%choice%"=="2" (
    chcp 65001 >nul
    cls
    echo 启动中文版本...
    echo.
    call start_zh.bat
) else (
    cls
    echo Invalid choice! Starting default (Chinese)...
    echo.
    call start_zh.bat
)
