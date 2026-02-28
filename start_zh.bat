@echo off
chcp 65001 >nul
echo Starting Autonomous Cognitive Learning System (Chinese)...
echo.
python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Program encountered an error
    echo Press any key to exit...
    pause >nul
)
