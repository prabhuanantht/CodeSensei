# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue: "Waiting for process to start..." - Generation Won't Start

**Symptoms:**
- Progress page shows "Waiting for process to start..."
- Terminal shows "missing ScriptRunContext" errors
- Generation never begins

**Cause:**
This was caused by trying to use threading with Streamlit, which doesn't work well with Streamlit's session state.

**Solution:**
✅ **FIXED in latest version** - The app now runs generation synchronously (no threading).

**What Changed:**
- Removed `threading.Thread` usage
- Generation now runs directly in Streamlit's main execution context
- Progress updates are shown via `st.spinner()` and logged after each step
- Trade-off: UI shows spinner during generation instead of real-time updates

**Note:** Generation will take 5-15 minutes and the UI will appear to "hang" with a spinner. This is normal - the process is running in the background.

---

### Issue: Config Option Warning (CORS/XSRF)

**Symptoms:**
```
Warning: the config option 'server.enableCORS=false' is not compatible 
with 'server.enableXsrfProtection=true'.
```

**Cause:**
Conflicting security settings in `.streamlit/config.toml`

**Solution:**
This is just a warning and can be ignored. Streamlit automatically resolves it by overriding the CORS setting. If you want to remove the warning:

```toml
# Edit .streamlit/config.toml
[server]
# Either remove enableCORS or set it to true
enableCORS = true
enableXsrfProtection = true
```

---

### Issue: Pydantic Warnings

**Symptoms:**
```
UserWarning: Field name "name" shadows an attribute in parent "Operation"
```

**Cause:**
Pydantic model compatibility warnings from google-genai library

**Solution:**
These are harmless warnings from the Gemini SDK. You can ignore them or suppress with:

```python
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
```

Add this to the top of `app.py` if desired.

---

### Issue: API Key Not Found

**Symptoms:**
```
❌ No API Key Found
```

**Cause:**
Environment variables not loaded

**Solution:**
1. Ensure `.env` file exists in the root directory
2. Check file contents:
   ```bash
   cat .env
   ```
3. Should contain:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
4. Restart Streamlit after creating/editing `.env`:
   ```bash
   streamlit run app.py
   ```

---

### Issue: Generation Takes Too Long

**Symptoms:**
- Spinner runs for 20+ minutes
- No progress updates

**Cause:**
Large codebase or slow LLM response

**Solution:**
1. **Reduce scope:**
   - Add more exclude patterns
   - Reduce max file size to 50KB
   - Lower max abstractions to 5-7

2. **Check logs:**
   ```bash
   tail -f logs/llm_calls_*.log
   ```

3. **Verify API is responding:**
   ```bash
   python PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py
   ```

---

### Issue: Rate Limit Exceeded

**Symptoms:**
```
❌ Error: Rate limit exceeded
```

**Cause:**
Too many API requests without authentication

**Solution:**
1. **Add GitHub token** (for GitHub repos):
   ```bash
   # In .env file
   GITHUB_TOKEN=ghp_your_token_here
   ```

2. **Enable caching:**
   - Check "Enable LLM Caching" in configuration
   - This reduces repeated API calls

3. **Wait and retry:**
   - Wait 5-10 minutes
   - Try again with a smaller repository

---

### Issue: Import Error - Can't Find PocketFlow Modules

**Symptoms:**
```
ModuleNotFoundError: No module named 'flow'
```

**Cause:**
Python can't find the PocketFlow directory

**Solution:**
1. Verify directory structure:
   ```bash
   ls -la PocketFlow-Tutorial-Codebase-Knowledge/
   ```

2. Ensure you're running from the correct directory:
   ```bash
   pwd  # Should show: .../CodeSensei_streamlit
   ```

3. Run from project root:
   ```bash
   cd /path/to/CodeSensei_streamlit
   streamlit run app.py
   ```

---

### Issue: Tutorial Generation Fails Silently

**Symptoms:**
- Generation "completes" but no output
- No error message shown

**Cause:**
Exception caught but not properly displayed

**Solution:**
1. **Check terminal output** for stack traces
2. **Check logs directory:**
   ```bash
   cat logs/llm_calls_*.log | tail -100
   ```
3. **Enable debug mode:**
   ```bash
   streamlit run app.py --logger.level=debug
   ```

---

### Issue: Download Button Not Working

**Symptoms:**
- Click "Download ZIP" but nothing happens
- Browser blocks download

**Cause:**
Browser security settings or popup blocker

**Solution:**
1. Check browser console (F12) for errors
2. Allow popups/downloads for localhost
3. Try different browser (Chrome usually works best)
4. Alternative: Manually zip the output folder:
   ```bash
   cd output
   zip -r tutorial.zip ProjectName/
   ```

---

### Issue: Markdown Not Rendering Properly

**Symptoms:**
- Preview shows raw markdown
- Mermaid diagrams don't display

**Cause:**
Streamlit markdown limitations

**Solution:**
1. **For previews**: This is expected - Streamlit has limited Mermaid support
2. **For final output**: 
   - Download the ZIP
   - View in a proper Markdown viewer (VS Code, GitHub, etc.)
   - Use a Markdown preview tool with Mermaid support

---

### Issue: Memory Error During Generation

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Cause:**
Codebase too large or too many files

**Solution:**
1. **Reduce file size limit:**
   ```
   Max File Size: 30000 (30KB instead of 100KB)
   ```

2. **Add aggressive exclude patterns:**
   ```
   *test*
   *tests/*
   *node_modules/*
   *venv/*
   *build/*
   *dist/*
   *examples/*
   *docs/*
   *.min.js
   *.min.css
   ```

3. **Analyze specific subdirectories:**
   - Instead of entire repo
   - Point to `/path/to/repo/src/core`

4. **Reduce max abstractions:**
   - Set to 5 instead of 10

---

### Issue: Permission Denied Writing Output

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'output/...'
```

**Cause:**
No write permissions for output directory

**Solution:**
1. **Change output directory:**
   ```
   Output Directory: ~/Documents/tutorials
   ```

2. **Fix permissions:**
   ```bash
   chmod -R 755 output/
   ```

3. **Use absolute path:**
   ```
   /Users/username/Desktop/tutorials
   ```

---

## Performance Tips

### For Faster Generation

1. ✅ **Enable caching** (default)
2. 🎯 **Use focused repositories** (< 100 files)
3. ⚡ **Use Gemini 2.5 Pro** (fastest and most capable)
4. 📊 **Reduce max abstractions** to 5-7
5. 🎯 **Exclude test files** and documentation
6. 📦 **Use smaller max file size** (50KB)

### For Better Results

1. 📚 **Choose well-structured projects**
2. 🎯 **Single-purpose libraries** work best
3. 📝 **Clean, documented code** produces better tutorials
4. 🔍 **Smaller scope** = more detailed tutorials

---

## Debug Checklist

When something goes wrong, check these in order:

### 1. Environment
- [ ] `.env` file exists and has API key
- [ ] Python 3.8+ (`python --version`)
- [ ] Dependencies installed (`pip list | grep streamlit`)

### 2. API Configuration
- [ ] API key is valid
- [ ] API key has sufficient quota
- [ ] Network connection works
- [ ] Can reach API endpoint

### 3. Input Validation
- [ ] GitHub URL is correct (or directory exists)
- [ ] Project has supported file types
- [ ] Repository is accessible (public or have token)

### 4. Logs
- [ ] Check terminal output
- [ ] Check `logs/` directory
- [ ] Look for stack traces
- [ ] Review LLM API responses

### 5. Output
- [ ] Output directory has write permissions
- [ ] Sufficient disk space available
- [ ] No conflicting files exist

---

## Getting More Help

### Enable Verbose Logging

```bash
# Run with debug output
streamlit run app.py --logger.level=debug

# Check LLM calls
cat logs/llm_calls_$(date +%Y%m%d).log
```

### Test Components Individually

```bash
# Test LLM connection
python PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py

# Test file crawling
python PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_local_files.py

# Test CLI directly
cd PocketFlow-Tutorial-Codebase-Knowledge
python main.py --dir /path/to/test --max-abstractions 3
```

### Report Issues

If none of these solutions work:

1. **Gather information:**
   - Streamlit version: `streamlit version`
   - Python version: `python --version`
   - OS: `uname -a` (Mac/Linux) or `ver` (Windows)
   - Error messages from terminal
   - Relevant log files

2. **Create GitHub issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error logs

3. **Check existing issues:**
   - [GitHub Issues](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/issues)
   - [Discussions](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/discussions)

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Won't start | ✅ Fixed - update app.py |
| CORS warning | Ignore it |
| Pydantic warnings | Ignore them |
| No API key | Create `.env` file |
| Too slow | Reduce abstractions, add excludes |
| Rate limited | Add GitHub token, enable cache |
| Import error | Run from project root |
| No output | Check logs, try debug mode |
| Download fails | Use different browser |
| Memory error | Reduce file size, add excludes |

---

**Still stuck?** Check the other documentation files:
- `QUICKSTART.md` - Basic setup
- `STREAMLIT_SETUP.md` - Detailed configuration
- `README.md` - General usage

**Happy tutorial generating!** 🎓

