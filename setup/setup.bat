@echo off
REM Setup script for Sanskrit RAG System (Windows)

echo Setting up Sanskrit RAG System...
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.9 or higher.
    exit /b 1
)
echo Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r code\requirements.txt --quiet
echo Dependencies installed
echo.

REM Check for model
echo Checking for model file...
if exist models\tinyllama.gguf (
    echo Model file found
) else (
    echo.
    echo WARNING: Model file NOT found!
    echo.
    echo Please download the model file:
    echo   1. Visit: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
    echo   2. Download: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
    echo   3. Rename to: tinyllama.gguf
    echo   4. Place in: models\tinyllama.gguf
    echo.
)
echo.

REM Run test
echo Running system test...
echo.
python code\main.py --test

echo.
echo Setup complete!
echo.
echo Next steps:
echo   - To use CLI: python code\main.py
echo   - To use Web UI: streamlit run app.py
echo   - For help: see README.md or SETUP.md
echo.
pause
