# 🚀 CodeSensei Streamlit Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file in the root directory:

```bash
# For Gemini (Easiest)
GEMINI_API_KEY=your_api_key_here

# OR for other providers
LLM_PROVIDER=OLLAMA
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

You can copy from the example:
```bash
cp env_example.txt .env
# Then edit .env with your actual keys
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 📋 Detailed Setup

### Get a Gemini API Key (Recommended)

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key to your `.env` file

**Why Gemini?**
- Free tier available
- Excellent code understanding
- Fast response times
- Good for beginners

### Alternative: Use Ollama (Local, Free)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
3. Configure in `.env`:
   ```
   LLM_PROVIDER=OLLAMA
   OLLAMA_MODEL=llama3
   OLLAMA_BASE_URL=http://localhost:11434
   ```

### Alternative: Use OpenAI

```env
LLM_PROVIDER=OPENAI
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com
OPENAI_API_KEY=your_openai_key
```

## 🎯 First Tutorial

1. **Run the app**: `streamlit run app.py`
2. **Click "Get Started"**
3. **Enter a GitHub URL**: 
   - Try: `https://github.com/pallets/flask`
   - Or any small repository (<100 files works best)
4. **Click "Generate Tutorial"**
5. **Wait 5-10 minutes** (watch the progress)
6. **View and download** your tutorial!

## 🛠️ Troubleshooting

### "No API Key Found"
**Problem**: The app can't find your API configuration

**Solution**:
1. Check your `.env` file exists in the root directory
2. Verify the API key is correct (no extra spaces)
3. Restart the Streamlit app after changing `.env`

### "Rate Limit Exceeded"
**Problem**: Too many API requests

**Solution**:
1. Add a GitHub token to `.env`:
   ```
   GITHUB_TOKEN=your_github_token
   ```
2. Enable caching in the app settings
3. Try a smaller repository

### App Won't Start
**Problem**: Missing dependencies or Python version

**Solution**:
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Clear Streamlit cache
streamlit cache clear
```

### Generation Takes Too Long
**Problem**: Large codebase or slow LLM

**Solution**:
1. Use a smaller repository (< 50 files)
2. Add more exclude patterns
3. Reduce "Max Abstractions" to 5-7
4. Use a faster LLM (Gemini Pro)

### Preview Not Showing
**Problem**: Markdown rendering issues

**Solution**:
- Refresh the page
- Download the ZIP and view locally
- Check browser console for errors

## 📁 File Structure

```
CodeSensei_streamlit/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
├── STREAMLIT_SETUP.md             # This file
├── env_example.txt                # Environment template
│
├── PocketFlow-Tutorial-Codebase-Knowledge/
│   ├── flow.py                    # Tutorial generation workflow
│   ├── nodes.py                   # Processing nodes
│   ├── main.py                    # Original CLI (still works)
│   └── utils/
│       ├── call_llm.py           # LLM integration
│       ├── crawl_github_files.py # GitHub crawler
│       └── crawl_local_files.py  # Local file crawler
│
└── output/                        # Generated tutorials (created automatically)
    └── YourProject/
        ├── index.md
        └── *.md
```

## 🎨 Customization

### Change App Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Modify Default Settings

Edit `app.py`:

```python
# Line 285: Change default abstractions
max_abstractions = st.slider(
    "Max Abstractions",
    min_value=5,
    max_value=20,
    value=8,  # Change default here
    ...
)
```

### Add Custom File Patterns

Edit the configuration page in `app.py` or modify `main.py`:

```python
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.tsx",
    "*.your_extension",  # Add custom extensions
}
```

## 🚀 Advanced Usage

### Run on a Server

```bash
# Run on specific port
streamlit run app.py --server.port 8080

# Allow external connections
streamlit run app.py --server.address 0.0.0.0

# Run in background
nohup streamlit run app.py &
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```bash
docker build -t codesensei .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key codesensei
```

### Environment Variables

You can also set environment variables directly:

```bash
export GEMINI_API_KEY=your_key
export GITHUB_TOKEN=your_token
streamlit run app.py
```

## 📊 Performance Tips

### For Large Codebases

1. **Exclude more patterns**:
   ```
   *test*, *tests/*, *examples/*, *docs/*, *dist/*
   ```

2. **Reduce max file size**:
   - Default: 100KB
   - For large repos: 50KB

3. **Limit abstractions**:
   - Default: 10
   - For large repos: 5-7

### For Faster Generation

1. **Enable caching** ✅ (default)
2. **Use Gemini 2.5 Pro** (fastest)
3. **Pre-filter files** before analysis
4. **Use local directory** instead of GitHub (faster crawling)

## 🔒 Security Notes

1. **Never commit `.env`** - Already in `.gitignore`
2. **Rotate API keys** regularly
3. **Use read-only GitHub tokens**
4. **Run locally** for sensitive code
5. **Review generated content** before sharing

## 📞 Getting Help

1. **Check the logs**: Look at `logs/` directory
2. **Enable debug mode**: 
   ```bash
   streamlit run app.py --logger.level=debug
   ```
3. **GitHub Issues**: Report bugs or request features
4. **Discussions**: Ask questions in GitHub Discussions

## 🎓 Tutorial Quality Tips

### Best Results

1. **Choose focused repositories**
   - Single purpose
   - Well-structured
   - Good documentation

2. **Configure thoughtfully**
   - Exclude test files
   - Include only source code
   - Set appropriate abstraction count

3. **Review and edit**
   - AI-generated content may need refinement
   - Add your own insights
   - Fix any inaccuracies

### Example Good Repositories

- Small frameworks (Flask, FastAPI)
- Libraries (Requests, Click)
- Tools (Black, Pytest)
- Your own projects!

### Example Challenging Repositories

- Very large projects (Linux kernel)
- Multi-language projects
- Projects with minimal structure
- Auto-generated code

## 🎉 Success Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API key
- [ ] Streamlit app runs (`streamlit run app.py`)
- [ ] API status shows green ✅
- [ ] First tutorial generated successfully
- [ ] Tutorial downloaded and reviewed

---

**Ready to generate tutorials?**

```bash
streamlit run app.py
```

Happy learning! 🎓

