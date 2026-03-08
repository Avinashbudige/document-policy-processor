@echo off
REM Quick test for local demo setup

echo ========================================
echo Testing Local Demo Setup
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
)
echo OK
echo.

echo [2/4] Checking required packages...
python -c "import streamlit; print('streamlit:', streamlit.__version__)"
if errorlevel 1 (
    echo ERROR: streamlit not installed
    echo Run: pip install streamlit
    exit /b 1
)
echo.

python -c "import sentence_transformers; print('sentence-transformers: OK')"
if errorlevel 1 (
    echo ERROR: sentence-transformers not installed
    echo Run: pip install sentence-transformers
    exit /b 1
)
echo.

python -c "import torch; print('torch:', torch.__version__)"
if errorlevel 1 (
    echo ERROR: torch not installed
    echo Run: pip install torch
    exit /b 1
)
echo.

echo [3/4] Checking source modules...
python -c "import sys; sys.path.insert(0, 'src'); from text_extractor import TextExtractor; print('text_extractor: OK')"
if errorlevel 1 (
    echo ERROR: text_extractor module not found
    exit /b 1
)
echo.

python -c "import sys; sys.path.insert(0, 'src'); from policy_matcher import PolicyMatcher; print('policy_matcher: OK')"
if errorlevel 1 (
    echo ERROR: policy_matcher module not found
    exit /b 1
)
echo.

python -c "import sys; sys.path.insert(0, 'src'); from recommendation_engine import RecommendationEngine; print('recommendation_engine: OK')"
if errorlevel 1 (
    echo ERROR: recommendation_engine module not found
    exit /b 1
)
echo.

echo [4/4] Checking demo files...
if not exist "frontend\app_local_demo.py" (
    echo ERROR: frontend\app_local_demo.py not found
    exit /b 1
)
echo frontend\app_local_demo.py: OK
echo.

if not exist "demo\sample_documents" (
    echo ERROR: demo\sample_documents folder not found
    exit /b 1
)
echo demo\sample_documents: OK
echo.

echo ========================================
echo All checks passed!
echo ========================================
echo.
echo You're ready to run the local demo:
echo   run-local-demo.bat
echo.
echo Or manually:
echo   cd frontend
echo   streamlit run app_local_demo.py
echo.

pause
