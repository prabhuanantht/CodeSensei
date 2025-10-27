@echo off
REM CodeSensei Streamlit App Runner for Windows

echo 🎓 CodeSensei - Starting Streamlit App...
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  Warning: .env file not found!
    echo 📝 Please create a .env file with your API keys.
    echo    You can copy from env_example.txt
    echo.
    set /p continue="Do you want to continue anyway? (y/n) "
    if /i not "%continue%"=="y" exit /b
)

REM Check if streamlit is installed
where streamlit >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Streamlit is not installed!
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Run the app
echo 🚀 Starting Streamlit app...
echo 📱 The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

