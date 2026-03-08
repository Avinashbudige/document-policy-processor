@echo off
REM DynamoDB Deployment Script for Windows
REM Deploys DynamoDB tables for Document Policy Processor

echo ==========================================
echo DynamoDB Deployment Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3 and try again
    exit /b 1
)

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo Error: AWS CLI is not installed
    echo Please install AWS CLI and configure it with 'aws configure'
    exit /b 1
)

REM Check if AWS credentials are configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo Error: AWS credentials are not configured
    echo Please run 'aws configure' to set up your credentials
    exit /b 1
)

echo [OK] Prerequisites check passed
echo.

REM Install required Python packages
echo Installing required Python packages...
pip install boto3 --quiet
echo [OK] Dependencies installed
echo.

REM Run the setup script
echo Running DynamoDB setup...
python setup_dynamodb.py

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
pause
