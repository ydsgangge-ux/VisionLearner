@echo off
echo Starting Autonomous Cognitive Learning System (English)...
echo.
python main_en.py
if errorlevel 1 (
    echo.
    echo [ERROR] Program encountered an error
    echo Press any key to exit...
    pause >nul
)
