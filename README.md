# 🎓 CodeSensei - AI-Powered Codebase Analysis Platform

> **Transform any codebase into interactive tutorials and analyze code quality with AI-powered insights**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

## 🌟 Overview

CodeSensei is an intelligent web-based platform that helps developers understand and document complex codebases. Using advanced AI and machine learning techniques, it automatically generates interactive tutorials, detects security vulnerabilities, analyzes code quality, and provides intelligent Q&A capabilities.

**Perfect for:** New developers onboarding to a codebase, code reviews, documentation generation, and security audits.

## ✨ Key Features

### 📚 AI-Powered Tutorial Generation
- **Automated Documentation**: Generate interactive Markdown tutorials with Mermaid diagrams in under 10 minutes
- **Smart Analysis**: AI identifies core abstractions and architectural patterns
- **Multi-language Support**: Process Python, JavaScript, TypeScript, Java, Go, and more
- **Beginner-Friendly**: Explanations with code examples and visual diagrams

### 🧠 Code Intelligence Analysis
- **Complexity Analysis**: Detect cyclomatic complexity hotspots using Radon
- **Dead Code Detection**: Identify orphan functions and unused code via NetworkX call graphs
- **Code Similarity Clustering**: Find duplicate patterns using CodeBERT embeddings and K-means clustering
- **Pattern Mining**: Extract common coding patterns using AST analysis

### 🔒 Security Scanning
- **Vulnerability Detection**: Scan for SQL injection, XSS, insecure authentication, and 15+ vulnerability types using Bandit
- **Detailed Reports**: Get exact file paths and line numbers with HTML/JSON export
- **Severity Classification**: High, Medium, Low severity categorization

### 💬 RAG-Powered Code Chatbot
- **Semantic Search**: Function-level code chunking with intelligent retrieval
- **Context-Aware Q&A**: Ask questions about codebase architecture and implementation
- **Source Tracking**: Get exact file and line references for every answer
- **Technologies**: ChromaDB (HNSW + cosine similarity) with all-MiniLM-L6-v2 embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API Key (or compatible LLM provider)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/CodeSensei_streamlit.git
cd CodeSensei_streamlit

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp env_example.txt .env
# Edit .env and add your GEMINI_API_KEY
```

### Run the Application

```bash
# Using the run script
./run_app.sh  # Unix/Mac
# or
run_app.bat   # Windows

# Or directly with Streamlit
streamlit run app.py
```

Open your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Tutorial Generation
1. Navigate to the Tutorial Generation tab
2. Enter a GitHub repository URL or local directory path
3. Configure settings (language, max abstractions)
4. Click "Generate Tutorial"
5. Wait for completion (typically 5-15 minutes)
6. Download the generated tutorial as a ZIP file

### 2. Code Intelligence Analysis
1. Load your codebase (same as tutorial generation)
2. Navigate to Code Intelligence tab
3. Run individual analyses:
   - **Complexity Analysis**: View cyclomatic complexity metrics
   - **Orphan Detection**: Find dead code
   - **Pattern Mining**: Discover common patterns
4. Review detailed results with file locations

### 3. Security Scanning
1. In the Security tab, select severity and confidence filters
2. Click "Run Security Scan"
3. Review vulnerabilities organized by severity
4. Download HTML/JSON reports

### 4. Chat with Code
1. In the Chat tab, click "Index Codebase for Chat"
2. Wait for indexing to complete
3. Ask questions about the codebase
4. Get AI-powered answers with source citations

## 🏗️ Architecture

```
CodeSensei Platform
├── Frontend (Streamlit)
│   ├── Tutorial Generation UI
│   ├── Intelligence Analysis UI
│   ├── Security Scanner UI
│   └── RAG Chatbot UI
├── Core Analyzers
│   ├── CodeIntelligenceAnalyzer (CodeBERT, NetworkX, Radon)
│   ├── SecurityAnalyzer (Bandit)
│   └── CodebaseRAG (ChromaDB, sentence-transformers)
└── Backend Integration
    └── PocketFlow Workflow Engine
```

## 🛠️ Technology Stack

### Core Technologies
- **Streamlit**: Modern web framework for Python apps
- **Python 3.8+**: Main programming language
- **Google Gemini**: LLM for content generation and Q&A

### AI/ML Libraries
- **CodeBERT** (microsoft/codebert-base): Code embeddings for similarity analysis
- **Transformers**: Hugging Face transformers library
- **NetworkX**: Graph analysis for call graphs
- **Radon**: Code complexity metrics
- **Bandit**: Security vulnerability scanning
- **scikit-learn**: Clustering and similarity analysis

### Vector Database
- **ChromaDB**: HNSW indexing with cosine similarity
- **sentence-transformers**: all-MiniLM-L6-v2 embeddings

### Additional Tools
- **ChromaDB**: Vector database for semantic search
- **Mermaid**: Diagram generation
- **Pandas**: Data manipulation and analysis

## 📊 Features Breakdown

| Module | Functionality | Technologies |
|--------|---------------|--------------|
| **Tutorial Generation** | AI-powered documentation with diagrams | Gemini, Mermaid, AST parsing |
| **Complexity Analysis** | Cyclomatic complexity & maintainability | Radon, NetworkX |
| **Orphan Detection** | Dead code identification | NetworkX, AST |
| **Pattern Mining** | Code pattern extraction | AST, NetworkX |
| **Code Similarity** | Duplicate code detection | CodeBERT, K-means, scikit-learn |
| **Security Scanning** | Vulnerability detection | Bandit, AST |
| **RAG Chatbot** | Semantic Q&A | ChromaDB, sentence-transformers, Gemini |

## 📁 Project Structure

```
CodeSensei_streamlit/
├── app_new.py              # Main Streamlit application
├── intelligence_analyzer.py # Code intelligence analysis
├── security_analyzer.py     # Security vulnerability scanning
├── rag_chatbot.py          # RAG chatbot implementation
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in repo)
├── output/                 # Generated tutorials
├── cache/                  # Cached repositories
└── logs/                   # Application logs
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Developers

- **Ananth Prabhu T**
- **Shreedhar A Sherlekar**
- **Chandan K Vasista**

**Made with ❤️ for the developer community**
