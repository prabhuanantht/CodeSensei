# 🏗️ CodeSensei Architecture

## Overview

CodeSensei Streamlit is a web-based frontend for the PocketFlow Tutorial Codebase Knowledge generator. It transforms a CLI tool into an interactive, user-friendly application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Browser                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Streamlit Frontend (app.py)               │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │   │
│  │  │  Home   │  │Configure│  │Generate │  │Results │ │   │
│  │  │  Page   │→ │  Page   │→ │  Page   │→ │  Page  │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Session State, User Interactions
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Streamlit Backend (Python)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Utility Layer (streamlit_utils.py)             │  │
│  │  • Progress Logging                                   │  │
│  │  • Flow Instrumentation                               │  │
│  │  • Validation & Stats                                 │  │
│  │  • File Management                                    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        PocketFlow Workflow (flow.py)                  │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐  │  │
│  │  │ Fetch  │→ │Identify│→ │Analyze │→ │  Order   │  │  │
│  │  │  Repo  │  │Abstract│  │Relation│  │ Chapters │  │  │
│  │  └────────┘  └────────┘  └────────┘  └──────────┘  │  │
│  │                                            │          │  │
│  │                                            ▼          │  │
│  │                              ┌──────────────────┐    │  │
│  │                              │  Write Chapters  │    │  │
│  │                              │   (BatchNode)    │    │  │
│  │                              └────────┬─────────┘    │  │
│  │                                       │              │  │
│  │                                       ▼              │  │
│  │                              ┌─────────────────┐    │  │
│  │                              │ Combine Tutorial│    │  │
│  │                              └─────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  LLM Provider │  │   GitHub     │  │  File System    │ │
│  │  (Gemini,     │  │     API      │  │  (Local/Output) │ │
│  │   OpenAI,     │  │              │  │                 │ │
│  │   Ollama...)  │  │              │  │                 │ │
│  └───────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend Layer (`app.py`)

**Responsibilities:**
- User interface rendering
- Session state management
- Page navigation
- User input collection
- Progress visualization
- Results display

**Key Components:**

```python
# Page Renderers
render_home()         # Landing page
render_configure()    # Settings page
render_generate()     # Progress tracking
render_results()      # Output viewer

# State Management
st.session_state.page              # Current page
st.session_state.tutorial_running  # Generation status
st.session_state.progress_log      # Activity log
st.session_state.output_dir        # Result location
```

**Technology:**
- Streamlit 1.28+
- Custom CSS for styling
- Session state for persistence
- Threading for non-blocking execution

### 2. Utility Layer (`streamlit_utils.py`)

**Responsibilities:**
- Progress logging and monitoring
- Flow instrumentation
- Configuration validation
- Statistics calculation
- File operations

**Key Classes:**

```python
class StreamlitProgressLogger:
    """Logs progress and forwards to Streamlit"""
    log(message, level)
    get_logs()
    clear()

# Helper Functions
monkey_patch_node_for_logging()       # Instrument regular nodes
monkey_patch_batch_node_for_logging() # Instrument batch nodes
create_instrumented_flow()            # Create monitored flow
safe_run_flow()                       # Run with error handling
validate_config()                     # Check configuration
get_tutorial_stats()                  # Calculate metrics
```

### 3. Workflow Layer (PocketFlow)

**Responsibilities:**
- Orchestrate tutorial generation
- Execute processing nodes
- Manage data flow
- Handle retries and errors

**Node Pipeline:**

```
┌──────────────┐
│  FetchRepo   │  Crawls GitHub/local files
└──────┬───────┘
       │ files list
       ▼
┌──────────────────────┐
│ IdentifyAbstractions │  AI identifies core concepts
└──────┬───────────────┘
       │ abstractions list
       ▼
┌──────────────────────┐
│ AnalyzeRelationships │  AI maps interactions
└──────┬───────────────┘
       │ relationships + summary
       ▼
┌──────────────────┐
│  OrderChapters   │  AI determines sequence
└──────┬───────────┘
       │ chapter order
       ▼
┌──────────────────┐
│ WriteChapters    │  AI writes detailed content
│  (BatchNode)     │  Parallel processing
└──────┬───────────┘
       │ chapter content
       ▼
┌──────────────────┐
│ CombineTutorial  │  Assembles final output
└──────────────────┘
```

**Data Flow:**

```python
shared = {
    # Input
    "repo_url": str,
    "local_dir": str,
    "project_name": str,
    "github_token": str,
    "language": str,
    "max_abstraction_num": int,
    
    # Processing
    "files": [(path, content)],
    "abstractions": [{name, description, files}],
    "relationships": {summary, details},
    "chapter_order": [int],
    
    # Output
    "chapters": [str],
    "final_output_dir": str
}
```

### 4. Integration Layer

**File Crawlers:**
```python
crawl_github_files()  # GitHub API integration
crawl_local_files()   # Local filesystem scanning
```

**LLM Integration:**
```python
call_llm(prompt, use_cache)  # Unified LLM interface
_call_llm_gemini()           # Google Gemini
_call_llm_provider()         # OpenAI-compatible APIs
```

## Data Flow

### Input → Output Pipeline

```
User Input
    │
    ├─ GitHub URL or Local Path
    ├─ Configuration (patterns, language, etc.)
    └─ API Credentials
    │
    ▼
File Collection
    │
    ├─ Clone/scan repository
    ├─ Filter by patterns
    └─ Read file contents
    │
    ▼
AI Analysis (LLM)
    │
    ├─ Identify core abstractions (5-20)
    ├─ Analyze relationships between them
    └─ Determine teaching order
    │
    ▼
Content Generation (LLM)
    │
    ├─ Write chapter for each abstraction
    ├─ Include code examples
    ├─ Generate diagrams
    └─ Add cross-references
    │
    ▼
Assembly & Export
    │
    ├─ Create index.md with overview
    ├─ Create chapter files (01_*.md, 02_*.md...)
    ├─ Generate Mermaid diagrams
    └─ Package as downloadable ZIP
    │
    ▼
Output
    └─ Markdown tutorial files
```

## State Management

### Session State Variables

```python
st.session_state = {
    # Navigation
    'page': str,                    # 'home' | 'configure' | 'generate' | 'results'
    
    # Execution
    'tutorial_running': bool,       # Is generation in progress?
    'tutorial_complete': bool,      # Has generation finished?
    'current_step': str,           # Current processing step
    'error_message': str | None,   # Error if any
    
    # Data
    'generation_config': dict,     # User configuration
    'progress_log': [dict],        # Activity log entries
    'output_dir': str | None,      # Result directory path
}
```

### State Transitions

```
home → configure → generate → results
  ↑                              ↓
  └──────────────────────────────┘
           (Generate Another)
```

## Threading Model

```python
# Main Thread (Streamlit)
def render_generate():
    if not running and not complete:
        # Start worker thread
        thread = threading.Thread(
            target=run_tutorial_generation,
            args=(config,)
        )
        thread.daemon = True
        thread.start()
    
    # Display progress (non-blocking)
    display_progress()
    
    # Auto-refresh while running
    if running:
        time.sleep(2)
        st.rerun()

# Worker Thread
def run_tutorial_generation(config):
    try:
        # Run the flow (blocking)
        tutorial_flow.run(shared)
        
        # Update session state
        st.session_state.tutorial_complete = True
    except Exception as e:
        st.session_state.error_message = str(e)
    finally:
        st.session_state.tutorial_running = False
```

## File System Structure

```
CodeSensei_streamlit/
├── app.py                      # Main Streamlit application
├── streamlit_utils.py          # Helper utilities
├── requirements.txt            # Dependencies
├── .env                        # Environment config (gitignored)
├── env_example.txt            # Environment template
│
├── .streamlit/                # Streamlit configuration
│   └── config.toml           # Theme and server settings
│
├── PocketFlow-Tutorial-Codebase-Knowledge/
│   ├── flow.py               # Workflow definition
│   ├── nodes.py              # Processing nodes
│   ├── main.py               # Original CLI
│   └── utils/
│       ├── call_llm.py       # LLM integration
│       ├── crawl_github_files.py
│       └── crawl_local_files.py
│
├── output/                   # Generated tutorials (auto-created)
│   └── ProjectName/
│       ├── index.md
│       └── *.md
│
├── logs/                     # LLM call logs (auto-created)
│   └── llm_calls_YYYYMMDD.log
│
└── llm_cache.json           # LLM response cache (auto-created)
```

## API Integration

### Supported LLM Providers

```python
# Configuration via environment variables

# Option 1: Google Gemini (Recommended)
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-2.5-pro-exp-03-25

# Option 2: OpenAI
LLM_PROVIDER=OPENAI
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com
OPENAI_API_KEY=xxx

# Option 3: Ollama (Local)
LLM_PROVIDER=OLLAMA
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### LLM Call Flow

```
User Action
    ↓
Configuration Validation
    ↓
Check Cache (if enabled)
    ↓
Call LLM Provider
    │
    ├─ Format prompt
    ├─ Send request
    ├─ Parse response
    ├─ Validate output
    └─ Update cache
    ↓
Return Result
```

## Error Handling

### Error Propagation

```
Node Execution Error
    ↓
Node Retry Logic (max 5 retries)
    ↓
Flow Error Handler
    ↓
StreamlitProgressLogger
    ↓
Session State (error_message)
    ↓
UI Display (st.error)
```

### Validation Points

1. **Configuration** - Before starting generation
2. **LLM Response** - After each LLM call
3. **File Operations** - During I/O
4. **State Transitions** - Between workflow steps

## Performance Optimizations

### Caching Strategy

```python
# LLM Response Cache
{
    "prompt_hash": "response_text"
}
# Stored in: llm_cache.json
# Benefits: Faster re-runs, reduced API costs

# Streamlit Cache
@st.cache_data
def expensive_operation():
    # Cached by Streamlit
    pass
```

### Non-Blocking Execution

```python
# Use threading for long operations
thread = threading.Thread(target=run_tutorial_generation)
thread.daemon = True
thread.start()

# UI remains responsive
while running:
    display_progress()
    time.sleep(2)
    st.rerun()
```

### Progress Tracking

```python
# Instrument nodes to report progress
def logged_exec(prep_res):
    logger.log(f"Starting: {step_name}")
    result = original_exec(prep_res)
    logger.log(f"Completed: {step_name}")
    return result
```

## Security Considerations

### API Key Protection

```python
# Stored in .env (gitignored)
# Accessed via os.getenv()
# Never logged or displayed
# Used only for API calls
```

### Input Validation

```python
def validate_config(config):
    # Check URL format
    # Verify directory exists
    # Validate numeric ranges
    # Sanitize file paths
```

### Data Privacy

- All processing is local
- No data sent except to LLM API
- No telemetry or tracking
- User controls all data

## Deployment Options

### Local Development

```bash
streamlit run app.py
```

### Server Deployment

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Container

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

## Extensibility

### Adding New Pages

```python
# 1. Create render function
def render_new_page():
    st.markdown("# New Page")
    # ... page content

# 2. Add navigation
if st.session_state.page == 'new_page':
    render_new_page()

# 3. Add sidebar button
if st.button("New Page"):
    st.session_state.page = 'new_page'
    st.rerun()
```

### Adding LLM Providers

```python
# 1. In call_llm.py, add provider function
def _call_llm_new_provider(prompt):
    # Provider-specific implementation
    pass

# 2. Update get_llm_provider()
def get_llm_provider():
    if os.getenv("NEW_PROVIDER_KEY"):
        return "NEW_PROVIDER"
    # ...

# 3. Update call_llm()
if provider == "NEW_PROVIDER":
    response = _call_llm_new_provider(prompt)
```

## Testing Strategy

### Unit Tests (Future)

```python
# Test utilities
test_validate_config()
test_format_file_size()
test_get_tutorial_stats()

# Test flow instrumentation
test_monkey_patch_node()
test_create_instrumented_flow()
```

### Integration Tests (Future)

```python
# Test end-to-end flow
test_generate_tutorial_from_github()
test_generate_tutorial_from_local()
test_error_handling()
```

### Manual Testing

```bash
# Test with small repository
streamlit run app.py
# Use: https://github.com/pallets/click

# Verify:
# - All pages render
# - Progress updates appear
# - Tutorial generates successfully
# - Download works
```

## Monitoring & Debugging

### Logs

```python
# Application logs
logs/llm_calls_YYYYMMDD.log

# Streamlit logs
~/.streamlit/streamlit.log

# Browser console
# (F12 in browser for frontend errors)
```

### Debug Mode

```bash
streamlit run app.py --logger.level=debug
```

---

This architecture provides a robust, scalable foundation for the CodeSensei application while maintaining simplicity and ease of use.

