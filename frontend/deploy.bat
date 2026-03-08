@echo off
REM Deployment script for Document Policy Processor Frontend (Windows)

echo === Document Policy Processor Frontend Deployment ===
echo.

REM Check if API_BASE_URL is provided
if "%~1"=="" (
    echo Usage: deploy.bat ^<API_GATEWAY_URL^>
    echo Example: deploy.bat https://abc123.execute-api.us-east-1.amazonaws.com/prod
    exit /b 1
)

set API_BASE_URL=%~1

echo Step 1: Creating .streamlit directory...
if not exist .streamlit mkdir .streamlit

echo Step 2: Creating secrets.toml...
(
echo # Streamlit Secrets Configuration
echo API_BASE_URL = "%API_BASE_URL%"
) > .streamlit\secrets.toml

echo Step 3: Installing dependencies...
pip install -r requirements.txt

echo.
echo === Deployment Complete ===
echo.
echo To run the application locally:
echo   streamlit run app.py
echo.
echo To deploy to Streamlit Cloud:
echo   1. Push code to GitHub
echo   2. Go to share.streamlit.io
echo   3. Connect your repository
echo   4. Add API_BASE_URL to Secrets
echo   5. Deploy!
echo.
