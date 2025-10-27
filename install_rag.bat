@echo off
REM Installation script for RAG Chatbot dependencies (Windows)

echo.
echo 🚀 Installing RAG Chatbot dependencies...
echo.

REM Install dependencies
echo 📦 Installing chromadb...
pip install chromadb>=0.4.0

echo.
echo 📦 Installing sentence-transformers...
pip install sentence-transformers>=2.2.0

echo.
echo ✅ Installation complete!
echo.
echo 🔄 Please restart your Streamlit app to use the RAG Chatbot.
echo.
echo To restart:
echo   1. Stop the current Streamlit app (Ctrl+C)
echo   2. Run: streamlit run app.py
echo.

pause

