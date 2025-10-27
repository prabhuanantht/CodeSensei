# 🎓 CodeSensei - Streamlit Frontend

A beautiful, modern web interface for the AI Codebase Tutorial Generator. Transform any codebase into easy-to-follow tutorials with just a few clicks!

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

- **🎨 Modern UI** - Clean, intuitive interface built with Streamlit
- **📊 Real-time Progress** - Watch your tutorial being generated step-by-step
- **📝 Live File Display** - See generated files appear as they're created
- **🔍 Live Preview** - Preview generated chapters instantly
- **📈 Mermaid Diagrams** - Interactive diagrams rendered beautifully
- **💾 Easy Export** - Download tutorials as ZIP files
- **🌍 Multi-language** - Generate tutorials in any language
- **⚙️ Flexible Configuration** - Full control over file patterns and settings
- **📊 Progress Tracking** - Visual feedback for each generation step
- **🔄 Caching Support** - Speed up re-runs with intelligent caching

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- An API key for one of the supported LLM providers:
  - Google Gemini (recommended)
  - OpenAI
  - Anthropic Claude
  - Ollama (local)
  - Any OpenAI-compatible API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge
   cd PocketFlow-Tutorial-Codebase-Knowledge
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   
   Create a `.env` file in the root directory:
   
   ```bash
   # For Google Gemini (Recommended)
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # OR for other providers
   LLM_PROVIDER=XAI  # or OLLAMA, OPENAI, etc.
   XAI_MODEL=grok-beta
   XAI_BASE_URL=https://api.x.ai/v1
   XAI_API_KEY=your_api_key_here
   
   # Optional: GitHub token for private repos
   GITHUB_TOKEN=your_github_token_here
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   
   The app will automatically open at `http://localhost:8501`

## 📖 How to Use

### Step 1: Home Page
- Learn about CodeSensei's features
- See example tutorials
- Click "Get Started"

### Step 2: Configure Your Tutorial
1. **Choose Source**
   - GitHub Repository (paste URL)
   - Local Directory (provide path)

2. **Project Settings**
   - Set project name (optional)
   - Choose tutorial language
   - Set max abstractions (5-20)
   - Enable/disable caching

3. **File Patterns (Advanced)**
   - Customize include patterns
   - Customize exclude patterns
   - Set maximum file size

4. **Output Settings**
   - Choose output directory

### Step 3: Generate
- Watch real-time progress
- See which step is currently running
- View live logs
- Wait for completion (typically 5-15 minutes)

### Step 4: View Results
- See tutorial statistics
- Preview index page
- Browse individual chapters
- Download as ZIP file

## 🎯 Configuration Options

### Source Options

**GitHub Repository**
```
Repository URL: https://github.com/username/repo
GitHub Token: (optional, for private repos)
```

**Local Directory**
```
Directory Path: /path/to/your/codebase
```

### Advanced Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Project Name | Auto-detected | Custom name for your tutorial |
| Language | English | Tutorial language (English, Spanish, etc.) |
| Max Abstractions | 10 | Number of core concepts to identify (5-20) |
| Enable Caching | Yes | Cache LLM responses for faster re-runs |
| Max File Size | 100KB | Maximum file size to analyze |

### File Patterns

**Default Include Patterns:**
```
*.py, *.js, *.jsx, *.ts, *.tsx, *.go, *.java, *.c, *.cpp, *.h, *.md, *.rst
```

**Default Exclude Patterns:**
```
*test*, *tests/*, *node_modules/*, *venv/*, *build/*, *dist/*, .git/*
```

## 🔧 Troubleshooting

### API Key Not Found
```
Error: No API Key Found
```
**Solution:** Set your API key in the `.env` file or environment variables

### Rate Limit Errors
```
Error: Rate limit exceeded
```
**Solution:** 
- Add a GitHub token for repository analysis
- Use caching to reduce API calls
- Wait a few minutes and try again

### Memory Issues
```
Error: Out of memory
```
**Solution:**
- Reduce max abstractions
- Add more exclude patterns
- Reduce max file size

### Generation Stuck
**Solution:**
- Check the progress log for errors
- Verify API key is valid
- Try disabling cache and regenerating

## 🏗️ Architecture

```
CodeSensei Streamlit App
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # API keys and configuration
│
└── PocketFlow-Tutorial-Codebase-Knowledge/
    ├── flow.py           # Tutorial generation workflow
    ├── nodes.py          # Individual processing nodes
    ├── main.py           # CLI interface (legacy)
    └── utils/
        ├── call_llm.py   # LLM API integration
        ├── crawl_github_files.py
        └── crawl_local_files.py
```

## 🎨 UI Components

### Pages

1. **Home** - Introduction and features
2. **Configure** - Setup tutorial generation
3. **Generate** - Real-time progress tracking
4. **Results** - Preview and download

### Key Features

- **Responsive Design** - Works on desktop and tablet
- **Progress Visualization** - Step-by-step progress indicators
- **Live Logging** - Real-time feedback during generation
- **Interactive Preview** - Browse chapters before downloading
- **Statistics Dashboard** - View tutorial metrics

## 🌐 Multi-Language Support

CodeSensei can generate tutorials in any language:

- English (default)
- Spanish (Español)
- French (Français)
- German (Deutsch)
- Chinese (中文)
- Japanese (日本語)
- Hindi (हिन्दी)
- Portuguese (Português)
- And more!

The AI will translate:
- All explanations and text
- Chapter names and descriptions
- Code comments (where appropriate)
- Diagram labels

## 📊 Example Output

After generation, you'll get:

```
output/
└── YourProject/
    ├── index.md              # Main tutorial page
    ├── 01_core_concept.md    # Chapter 1
    ├── 02_another_concept.md # Chapter 2
    └── ...                   # More chapters
```

Each tutorial includes:
- Project overview
- Mermaid relationship diagram
- Detailed chapters with:
  - Explanations
  - Code examples
  - Sequence diagrams
  - Cross-references
  - Analogies for beginners

## 🤝 Contributing

Contributions are welcome! This is built on top of [PocketFlow](https://github.com/The-Pocket/PocketFlow).

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Credits

- Built with [Streamlit](https://streamlit.io/)
- Powered by [PocketFlow](https://github.com/The-Pocket/PocketFlow)
- Original CLI tool: [Tutorial-Codebase-Knowledge](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/discussions)
- **Documentation**: [Official Docs](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/)

---

Made with ❤️ by the PocketFlow team

