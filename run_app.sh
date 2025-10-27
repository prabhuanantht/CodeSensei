#!/bin/bash

# CodeSensei Streamlit App Runner
# This script helps you quickly start the Streamlit app

echo "🎓 CodeSensei - Starting Streamlit App..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create a .env file with your API keys."
    echo "   You can copy from env_example.txt:"
    echo "   cp env_example.txt .env"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Load .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ] && [ -z "$LLM_PROVIDER" ] && [ -z "$GEMINI_PROJECT_ID" ]; then
    echo "⚠️  Warning: No API key detected in environment!"
    echo "   Make sure to configure your API key in the .env file"
    echo ""
fi

# Run the app
echo "🚀 Starting Streamlit app..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py

