# RAG Chatbot for Codebase Analysis

## 🎯 Overview

The RAG (Retrieval Augmented Generation) Chatbot is an intelligent assistant that can answer any question about your codebase by combining semantic search with AI-powered analysis.

## ✨ Features

### 1. **Code-Aware Chunking**
- **Function/Class-Based**: Chunks code at natural boundaries (functions, classes)
- **Language Support**: Python, JavaScript, TypeScript, Java, Go, Ruby, PHP
- **Context Preservation**: Maintains code context with overlapping chunks
- **Documentation Parsing**: Special handling for Markdown, README files

### 2. **Semantic Search**
- **Vector Database**: Uses ChromaDB for efficient similarity search
- **Fast Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Contextual Retrieval**: Finds most relevant code snippets
- **Source Tracking**: Shows exact file and line numbers

### 3. **AI-Powered Answers**
- **Gemini Integration**: Uses Google's Gemini 2.0 for responses
- **Context-Aware**: Answers based on actual code
- **Beginner-Friendly**: Explains complex concepts simply
- **Source Citations**: Links to specific files/lines

## 🚀 Getting Started

### Installation

```bash
# Install required dependencies
pip install chromadb sentence-transformers

# Or use requirements.txt
pip install -r requirements.txt
```

### Usage

1. **Navigate to RAG Chatbot**
   - Click "RAG Chatbot" in the sidebar

2. **Index Your Codebase**
   - Choose "Local Directory" or "GitHub Repository"
   - Enter the path/URL
   - Click "Index Codebase"
   - Wait for indexing to complete (progress shown)

3. **Start Chatting**
   - Type your question in the chat input
   - Get instant AI-powered answers
   - View source files for each answer

## 📚 What You Can Ask

### Understanding Code
```
✓ "Explain how authentication works in this codebase"
✓ "What does the UserService class do?"
✓ "How is database connection managed?"
✓ "Trace the flow of a user login request"
✓ "What design patterns are used?"
```

### Finding Issues
```
✓ "Are there any security vulnerabilities in the authentication code?"
✓ "Find potential bugs in the payment processing module"
✓ "Check for SQL injection risks"
✓ "Identify hardcoded credentials"
✓ "Find unhandled exceptions"
```

### Code Quality
```
✓ "Are there any code smells or anti-patterns?"
✓ "Suggest improvements for the API endpoints"
✓ "Is error handling done properly?"
✓ "Check for performance bottlenecks"
✓ "Review logging practices"
```

### Navigation
```
✓ "Where is the login functionality implemented?"
✓ "Show me all database query functions"
✓ "Which files handle user registration?"
✓ "Find all API endpoint definitions"
✓ "Where are environment variables used?"
```

### Best Practices
```
✓ "Does the code follow SOLID principles?"
✓ "Are there proper unit tests?"
✓ "Review the error handling strategy"
✓ "Check dependency injection patterns"
✓ "Evaluate code maintainability"
```

## 🔧 How It Works

### 1. **Chunking Algorithm**

```python
# For Python/JS/TS/Java/Go
- Detect function/class boundaries
- Create chunks at natural breakpoints
- Size: ~1500 characters per chunk
- Overlap: 200 characters for context

# For Markdown/Docs
- Split by paragraphs
- Maintain heading context
- Size: ~1500 characters

# For Other Files
- Sliding window approach
- 100 lines per chunk
- 20 line overlap
```

### 2. **Vector Search**

```python
1. User asks a question
2. Question is converted to embedding
3. ChromaDB finds 5 most similar code chunks
4. Chunks are ranked by relevance
5. Top chunks sent to Gemini with context
```

### 3. **Response Generation**

```python
Gemini receives:
- User question
- 5 relevant code chunks
- File paths and line numbers
- Special instructions for code analysis

Gemini returns:
- Detailed answer
- Code explanations
- Specific file references
- Actionable suggestions
```

## 🎨 Quick Actions

The chatbot provides three quick action buttons:

### 🔍 Find Vulnerabilities
Automatically analyzes codebase for:
- SQL injection risks
- XSS vulnerabilities
- Authentication issues
- Insecure data handling
- Hardcoded secrets

### 🐛 Find Bugs
Identifies potential issues:
- Null pointer exceptions
- Race conditions
- Memory leaks
- Logic errors
- Edge case handling

### ✨ Code Quality
Reviews code for:
- Code smells
- Anti-patterns
- Maintainability issues
- Documentation gaps
- Test coverage

## 📊 Indexing Statistics

After indexing, you'll see:
- **Total Files**: Number of files indexed
- **Total Chunks**: Number of searchable chunks
- **Indexed Files List**: Names of all indexed files

## 🎯 Advanced Usage

### Custom File Patterns

The chunker automatically handles:
- `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php` (code)
- `.md`, `.txt`, `.rst` (documentation)
- `.json`, `.yaml`, `.yml`, `.toml` (config)

### Excluded Directories

By default excludes:
- `node_modules/`
- `__pycache__/`
- `.git/`
- `venv/`, `env/`
- `build/`, `dist/`, `target/`

### Retrieval Tuning

- **n_results**: Number of chunks retrieved (default: 5)
- **chunk_size**: Size of each chunk (default: 1500)
- **overlap**: Overlap between chunks (default: 200)

## 🔒 Privacy & Security

### Local Processing
- **Vector DB**: Runs locally (ChromaDB)
- **Embeddings**: Computed on your machine
- **No Data Upload**: Code stays on your system

### API Calls
- **Only to Gemini**: For answer generation
- **Minimal Data**: Only relevant chunks sent
- **No Storage**: Google doesn't store your code

## 💡 Tips for Best Results

1. **Be Specific**: Ask about specific features/files
   ```
   ❌ "How does this work?"
   ✅ "How does user authentication work in auth.py?"
   ```

2. **Use Context**: Reference specific components
   ```
   ❌ "Fix bugs"
   ✅ "Find bugs in the payment processing flow"
   ```

3. **Ask Follow-ups**: Build on previous answers
   ```
   1. "How does login work?"
   2. "Are there security issues in that implementation?"
   3. "How can I improve it?"
   ```

4. **Check Sources**: Always review referenced files
   - Click "Sources" expander in responses
   - Verify the AI's interpretation
   - Cross-reference with actual code

## 🚫 Limitations

1. **Context Window**: Limited to 5 chunks per query
2. **Code Understanding**: May misinterpret complex logic
3. **Real-time**: Doesn't execute code, just analyzes text
4. **Indexing Time**: Large codebases take time to index
5. **Memory**: Large codebases need significant RAM

## 🐛 Troubleshooting

### "No collection created" Error
```bash
Solution: Re-index your codebase
- Click "Clear Index" in sidebar
- Index codebase again
```

### Slow Indexing
```bash
Causes:
- Large codebase (>1000 files)
- Many dependencies included

Solutions:
- Exclude unnecessary directories
- Index only specific subdirectories
- Increase chunk_size to reduce chunks
```

### Poor Answer Quality
```bash
Solutions:
- Be more specific in questions
- Increase n_results (retrieves more chunks)
- Ask follow-up questions for clarification
- Check if relevant files were indexed
```

### Out of Memory
```bash
Solutions:
- Index smaller subdirectories
- Increase chunk_size
- Exclude large files
- Close other applications
```

## 📈 Performance

### Typical Metrics
- **Small Codebase** (<100 files): 30s indexing
- **Medium Codebase** (100-500 files): 2-5 min indexing
- **Large Codebase** (500+ files): 5-15 min indexing
- **Query Response**: 2-5 seconds per question

### Optimization Tips
1. Index only relevant directories
2. Exclude test files if not needed
3. Use specific queries (faster retrieval)
4. Clear old indexes before re-indexing

## 🔮 Future Enhancements

- [ ] Code execution for verification
- [ ] Multi-repo support
- [ ] Custom embedding models
- [ ] Conversation history persistence
- [ ] Export chat transcripts
- [ ] Integration with IDEs
- [ ] Real-time code analysis
- [ ] Automated fix suggestions

## 📝 Example Session

```
User: Index this codebase
[Indexes 150 files, 1200 chunks]

User: "How does user authentication work?"
Bot: "The authentication system uses JWT tokens. Here's how it works:
     1. User submits credentials to /api/login
     2. AuthService validates against database
     3. JWT token generated if valid
     4. Token stored in HTTP-only cookie
     
     Key files:
     - auth.py (lines 45-89): Login endpoint
     - jwt_utils.py (lines 12-34): Token generation
     - middleware.py (lines 67-82): Token validation"

User: "Are there any security issues?"
Bot: "Yes, I found 2 potential security issues:
     
     1. CRITICAL: Password comparison is not constant-time
        File: auth.py, line 56
        Risk: Timing attacks possible
     
     2. MEDIUM: JWT expiry too long (30 days)
        File: config.py, line 23
        Risk: Stolen tokens valid for long time
     
     Recommendations:
     - Use secrets.compare_digest() for password comparison
     - Reduce JWT expiry to 1-2 hours
     - Implement refresh tokens"

User: "Show me the code to fix issue #1"
Bot: "Here's the fix for the timing attack vulnerability:
     
     ```python
     import secrets
     
     # Before (vulnerable):
     if password == stored_password:
         return True
     
     # After (secure):
     if secrets.compare_digest(password, stored_password):
         return True
     ```
     
     This prevents attackers from using response time to guess passwords."
```

## 🎓 Learning Resources

- [RAG Architecture](https://arxiv.org/abs/2005.11401)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Gemini API](https://ai.google.dev/docs)

---

**Ready to analyze your codebase? Start chatting! 🚀**

