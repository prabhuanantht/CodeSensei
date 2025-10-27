# ⚡ Quick Start Guide

Get CodeSensei up and running in 5 minutes!

## 🎯 Prerequisites

- Python 3.8 or higher
- An API key (Gemini recommended, it's free!)

## 📦 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get a Gemini API Key (Free!)

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key (takes 30 seconds)
4. Copy the key

### Step 3: Configure Your API Key

Create a `.env` file:

```bash
# Copy the example
cp env_example.txt .env

# Edit with your key
nano .env  # or use any text editor
```

Add your key:
```
GEMINI_API_KEY=your_actual_key_here
```

### Step 4: Run the App

**Option A: Using the run script (Recommended)**

```bash
# On Mac/Linux
./run_app.sh

# On Windows
run_app.bat
```

**Option B: Direct command**

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 🎓 Generate Your First Tutorial

### Example 1: Analyze Flask (Easy)

1. Click **"Get Started"**
2. Select **"GitHub Repository"**
3. Enter: `https://github.com/pallets/flask`
4. Click **"Generate Tutorial"**
5. Wait 5-10 minutes ☕
6. View and download your tutorial!

### Example 2: Analyze Your Own Project

1. Click **"Get Started"**
2. Select **"Local Directory"**
3. Enter the path to your project: `/path/to/your/code`
4. Adjust settings:
   - Max Abstractions: 7-10 for small projects
   - Language: Choose your preferred language
5. Click **"Generate Tutorial"**
6. Watch the magic happen! ✨

## 🎨 What You Get

After generation, you'll have:

```
output/
└── ProjectName/
    ├── index.md              # Main page with overview
    ├── 01_concept_one.md     # First chapter
    ├── 02_concept_two.md     # Second chapter
    └── ...                   # More chapters
```

Each tutorial includes:
- 📊 Visual diagrams (Mermaid)
- 💻 Code examples
- 📝 Beginner-friendly explanations
- 🔗 Cross-references between concepts
- 🎯 Real-world analogies

## 💡 Tips for Best Results

### Choose the Right Repository

**Good Choices:**
- Small to medium libraries (< 100 files)
- Well-structured projects
- Single-purpose tools
- Your own projects!

**Avoid:**
- Very large projects (> 1000 files)
- Projects with lots of generated code
- Repos with minimal structure

### Configure Smartly

**For Small Projects (< 50 files):**
- Max Abstractions: 5-7
- Keep default patterns
- Enable caching ✅

**For Medium Projects (50-200 files):**
- Max Abstractions: 8-10
- Add exclude patterns for tests/examples
- Enable caching ✅

**For Large Projects (> 200 files):**
- Max Abstractions: 7-8
- Aggressive exclude patterns
- Reduce max file size to 50KB
- Consider analyzing specific directories only

## 🐛 Common Issues

### "No API Key Found"

**Problem:** The app can't find your API configuration

**Fix:**
```bash
# Make sure .env file exists
ls -la .env

# Check the content
cat .env

# Should show:
# GEMINI_API_KEY=your_key_here
```

### "Rate Limit Exceeded"

**Problem:** Too many API requests

**Fix:**
1. Add a GitHub token to `.env`:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```
2. Enable caching in the app
3. Try again in a few minutes

### "Generation Takes Forever"

**Problem:** The codebase is too large

**Fix:**
1. Reduce Max Abstractions to 5
2. Add more exclude patterns:
   ```
   *test*
   *tests/*
   *examples/*
   *docs/*
   *build/*
   ```
3. Reduce max file size to 50KB

### App Won't Start

**Problem:** Missing dependencies or wrong Python version

**Fix:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Streamlit cache
streamlit cache clear

# Try again
streamlit run app.py
```

## 🎯 Example Workflows

### Workflow 1: Quick Analysis
```
1. Open app
2. Paste GitHub URL
3. Click Generate
4. Download ZIP
⏱️ Time: 5-10 minutes
```

### Workflow 2: Custom Configuration
```
1. Open app
2. Configure settings:
   - Add exclude patterns
   - Choose language
   - Set abstractions
3. Generate
4. Preview in browser
5. Download
⏱️ Time: 10-15 minutes
```

### Workflow 3: Local Project
```
1. Open app
2. Select "Local Directory"
3. Enter your project path
4. Customize file patterns
5. Generate
6. Review and edit downloaded files
⏱️ Time: 10-20 minutes
```

## 📚 Next Steps

### Customize Your Tutorials

1. **Edit the generated Markdown**
   - Add your own insights
   - Fix any inaccuracies
   - Add more examples

2. **Deploy as documentation**
   - Host on GitHub Pages
   - Add to your project's docs/
   - Share with your team

3. **Generate in multiple languages**
   - Create tutorials for international teams
   - Support non-English speakers

### Advanced Usage

**Analyze specific directories:**
```
Use Local Directory option
Point to: /project/src/core
```

**Compare before/after:**
```
Generate for old version
Generate for new version
Compare the abstractions
```

**Create learning paths:**
```
Generate for multiple related projects
Combine into a learning curriculum
```

## 🆘 Getting Help

### In-App Help
- Check the **tooltips** (hover over ?)
- Watch the **progress log**
- Check **API Status** in sidebar

### Documentation
- `README.md` - Main docs
- `STREAMLIT_SETUP.md` - Detailed setup
- `FEATURES.md` - Complete feature list

### Online Resources
- [GitHub Issues](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/issues)
- [Discussions](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/discussions)
- [Original Docs](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/)

## ⭐ Example Projects to Try

### Beginner (5-10 minutes)
- `https://github.com/psf/requests` - HTTP library
- `https://github.com/pallets/click` - CLI framework

### Intermediate (10-15 minutes)
- `https://github.com/pallets/flask` - Web framework
- `https://github.com/fastapi/fastapi` - Modern API framework

### Advanced (15-20 minutes)
- Your own project!
- `https://github.com/celery/celery` - Task queue

## 🎉 Success!

You're all set! Start generating tutorials and happy learning! 🎓

---

**Need help?** Check `STREAMLIT_SETUP.md` for detailed troubleshooting.

**Want to contribute?** Visit the GitHub repository.

**Enjoying CodeSensei?** Star us on GitHub! ⭐

