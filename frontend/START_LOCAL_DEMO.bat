@echo off
REM Start Local Demo - No AWS API Required

echo ==========================================
echo Document Policy Processor - LOCAL DEMO
echo ==========================================
echo.
echo This version runs entirely on your computer
echo No AWS API calls required!
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo X Python not installed
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Streamlit...
    pip install streamlit
)

python -c "import sentence_transformers" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing sentence-transformers...
    pip install sentence-transformers torch
)

echo.
echo ==========================================
echo Starting Local Demo...
echo ==========================================
echo.
echo Opening at: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo ==========================================
echo.

streamlit run app_local_demo.py

pause
