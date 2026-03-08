@echo off
REM Quick setup for public URL using ngrok

echo ========================================
echo   PUBLIC URL SETUP FOR HACKATHON
echo ========================================
echo.

echo This script will help you get a public URL for evaluators.
echo.

echo Step 1: Download ngrok
echo ----------------------------------------
echo 1. Go to: https://ngrok.com/download
echo 2. Download ngrok for Windows
echo 3. Extract ngrok.exe to this folder
echo.
pause

echo.
echo Step 2: Start Local Demo
echo ----------------------------------------
echo Opening local demo in new window...
start cmd /k "cd frontend && streamlit run app_local_demo.py"
echo.
echo Wait for Streamlit to start (you'll see: Local URL: http://localhost:8503)
echo.
pause

echo.
echo Step 3: Start ngrok
echo ----------------------------------------
echo.
if exist ngrok.exe (
    echo Starting ngrok...
    echo.
    echo COPY THE HTTPS URL THAT APPEARS BELOW!
    echo This is your public URL to share with evaluators.
    echo.
    echo Press Ctrl+C to stop ngrok when done.
    echo.
    ngrok http 8503
) else (
    echo ERROR: ngrok.exe not found in current directory!
    echo.
    echo Please:
    echo 1. Download ngrok from https://ngrok.com/download
    echo 2. Extract ngrok.exe to: %CD%
    echo 3. Run this script again
    echo.
    pause
)
