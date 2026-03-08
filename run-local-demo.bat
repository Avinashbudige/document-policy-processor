@echo off
REM Quick start script for local demo

echo ========================================
echo Document Policy Processor - Local Demo
echo ========================================
echo.

echo [1/3] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo.

echo [2/3] Installing frontend dependencies...
cd frontend
pip install -q streamlit requests
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Starting Streamlit app...
echo.
echo ========================================
echo Demo will open in your browser at:
echo http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C to stop the demo
echo.

streamlit run app_local_demo.py

pause
