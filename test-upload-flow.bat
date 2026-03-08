@echo off
REM Test script for document upload flow (Windows)
REM This script tests the complete upload and processing workflow

setlocal enabledelayedexpansion

REM Configuration
if "%API_BASE_URL%"=="" set API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
if "%API_KEY%"=="" set API_KEY=your-api-key-here
if "%TEST_FILE%"=="" set TEST_FILE=test-document.pdf
if "%SYMPTOMS%"=="" set SYMPTOMS=Fever and cough for 3 days

echo ==========================================
echo Document Upload Flow Test
echo ==========================================
echo.
echo API Base URL: %API_BASE_URL%
echo Test File: %TEST_FILE%
echo Symptoms: %SYMPTOMS%
echo.

REM Check if test file exists
if not exist "%TEST_FILE%" (
    echo Error: Test file '%TEST_FILE%' not found
    echo Please create a test file or set TEST_FILE environment variable
    exit /b 1
)

REM Determine file type
for %%i in ("%TEST_FILE%") do set FILE_EXT=%%~xi
set FILE_EXT=%FILE_EXT:~1%

if /i "%FILE_EXT%"=="pdf" set FILE_TYPE=application/pdf
if /i "%FILE_EXT%"=="png" set FILE_TYPE=image/png
if /i "%FILE_EXT%"=="jpg" set FILE_TYPE=image/jpeg
if /i "%FILE_EXT%"=="jpeg" set FILE_TYPE=image/jpeg
if /i "%FILE_EXT%"=="txt" set FILE_TYPE=text/plain

if "%FILE_TYPE%"=="" (
    echo Error: Unsupported file type: %FILE_EXT%
    exit /b 1
)

echo Step 1: Requesting upload URL...
echo ----------------------------------------

curl -s -X POST "%API_BASE_URL%/api/upload-url" ^
    -H "X-Api-Key: %API_KEY%" ^
    -H "Content-Type: application/json" ^
    -d "{\"filename\": \"%TEST_FILE%\", \"file_type\": \"%FILE_TYPE%\"}" ^
    -o upload_response.json

type upload_response.json
echo.
echo.

REM Parse JSON response (basic parsing for Windows)
for /f "tokens=2 delims=:," %%a in ('findstr "upload_url" upload_response.json') do set UPLOAD_URL=%%a
for /f "tokens=2 delims=:," %%a in ('findstr "document_url" upload_response.json') do set DOCUMENT_URL=%%a
for /f "tokens=2 delims=:," %%a in ('findstr "job_id" upload_response.json') do set JOB_ID=%%a

REM Remove quotes
set UPLOAD_URL=%UPLOAD_URL:"=%
set DOCUMENT_URL=%DOCUMENT_URL:"=%
set JOB_ID=%JOB_ID:"=%

if "%UPLOAD_URL%"=="" (
    echo Error: Failed to get upload URL
    type upload_response.json
    del upload_response.json
    exit /b 1
)

echo Upload URL: %UPLOAD_URL%
echo Document URL: %DOCUMENT_URL%
echo Job ID: %JOB_ID%
echo.

echo Step 2: Uploading file to S3...
echo ----------------------------------------

curl -s -o nul -w "HTTP Status: %%{http_code}" -X PUT "%UPLOAD_URL%" ^
    -H "Content-Type: %FILE_TYPE%" ^
    --data-binary "@%TEST_FILE%"

echo.
echo File uploaded successfully
echo.

echo Step 3: Triggering document processing...
echo ----------------------------------------

curl -s -X POST "%API_BASE_URL%/api/process-document" ^
    -H "X-Api-Key: %API_KEY%" ^
    -H "Content-Type: application/json" ^
    -d "{\"job_id\": \"%JOB_ID%\", \"document_url\": \"%DOCUMENT_URL%\", \"symptoms\": \"%SYMPTOMS%\"}" ^
    -o process_response.json

type process_response.json
echo.
echo.

REM Check status
for /f "tokens=2 delims=:," %%a in ('findstr "status" process_response.json') do set STATUS=%%a
set STATUS=%STATUS:"=%
set STATUS=%STATUS: =%

if "%STATUS%"=="completed" (
    echo Success: Processing completed successfully!
) else (
    echo Processing status: %STATUS%
    echo.
    echo You can check status later with:
    echo curl "%API_BASE_URL%/api/status/%JOB_ID%" -H "X-Api-Key: %API_KEY%"
    echo.
    echo And get results with:
    echo curl "%API_BASE_URL%/api/results/%JOB_ID%" -H "X-Api-Key: %API_KEY%"
)

REM Cleanup
del upload_response.json
del process_response.json

echo.
echo ==========================================
echo Test completed!
echo ==========================================

endlocal
