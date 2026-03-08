@echo off
REM Start Streamlit Frontend for Document Policy Processor

echo ==========================================
echo Starting Document Policy Processor Frontend
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo + Python is installed

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Streamlit is not installed. Installing required packages...
    echo.
    pip install streamlit requests boto3
    if %ERRORLEVEL% NEQ 0 (
        echo X Failed to install packages
        pause
        exit /b 1
    )
    echo + Packages installed successfully
)

REM Check if secrets file exists
if not exist ".streamlit\secrets.toml" (
    echo.
    echo WARNING: Secrets file not found!
    echo Creating .streamlit directory...
    mkdir .streamlit 2>nul
    
    echo Creating secrets.toml with API credentials...
    (
        echo # Streamlit Secrets Configuration
        echo [api]
        echo base_url = "https://bmi41mg6uf.execute-api.us-east-1.amazonaws.com/prod"
        echo api_key = "9wx9nHe2NV5vSAOyRps9l3c7PpQ19OttaJqHw4mw"
        echo.
        echo [aws]
        echo region = "us-east-1"
        echo s3_bucket = "document-policy-processor-uploads"
    ) > .streamlit\secrets.toml
    
    echo + Secrets file created
)

echo.
echo ==========================================
echo Starting Streamlit App...
echo ==========================================
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

REM Start Streamlit
streamlit run app.py

pause
