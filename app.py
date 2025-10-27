import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import shutil
import zipfile
import io
import traceback
import threading
import queue
import re
import streamlit.components.v1 as components
from dotenv import load_dotenv
from contextlib import redirect_stdout, redirect_stderr

# Load environment variables from .env file
load_dotenv()

# Add the PocketFlow directory to the path
sys.path.insert(0, str(Path(__file__).parent / "PocketFlow-Tutorial-Codebase-Knowledge"))

from flow import create_tutorial_flow
from main import DEFAULT_INCLUDE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS

# Page configuration
st.set_page_config(
    page_title="CodeSensei - AI Codebase Tutorial Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Unicode icons mapping (using clean, monochrome symbols)
ICONS = {
    'book-open': '◈',
    'info': 'ⓘ',
    'sparkles': '✦',
    'cpu': '◉',
    'layers': '▦',
    'globe': '◎',
    'workflow': '⚡',
    'github': '⎇',
    'folder': '▣',
    'download': '↓',
    'search': '⌕',
    'list-ordered': '≡',
    'file-text': '▤',
    'package': '▦',
    'book': '▥',
    'code': '⟨⟩',
    'settings': '⚙',
    'folder-input': '▣',
    'sliders': '⚙',
    'file-code': '⟨/⟩',
    'save': '◫',
    'loader': '⟳',
    'check': '✓',
    'loader-2': '⟳',
    'git-branch': '⎇',
    'edit': '✎',
    'terminal': '▶',
    'files': '▥',
    'check-circle': '✓',
    'bar-chart': '▥',
    'hard-drive': '◫',
    'eye': '◉',
    'graduation-cap': '◆',
    'navigation': '⌘',
    'home': '⌂',
    'key': '◈',
}

def icon(name, size=20):
    """Helper function to create professional unicode icons"""
    symbol = ICONS.get(name, '•')
    return f'<span style="font-size: {size}px; display: inline-block; vertical-align: middle; margin-right: 4px;">{symbol}</span>'

# Custom CSS for better UI (dark mode optimized)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        opacity: 0.8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(250, 250, 250, 0.1);
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
    .file-count {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid rgba(250, 250, 250, 0.1);
    }
    .icon-inline {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    .settings-section {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(250, 250, 250, 0.1);
        margin: 0.5rem 0;
    }
    .nav-button {
        margin-bottom: 0.5rem;
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .section-header i {
        opacity: 0.8;
    }
    /* Style for icon spans */
    .section-header span {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'tutorial_running' not in st.session_state:
    st.session_state.tutorial_running = False
if 'tutorial_complete' not in st.session_state:
    st.session_state.tutorial_complete = False
if 'progress_log' not in st.session_state:
    st.session_state.progress_log = []
if 'output_dir' not in st.session_state:
    st.session_state.output_dir = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []
if 'expected_output_dir' not in st.session_state:
    st.session_state.expected_output_dir = None
if 'known_files' not in st.session_state:
    st.session_state.known_files = set()
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = queue.Queue()
if 'generation_thread' not in st.session_state:
    st.session_state.generation_thread = None
if 'console_output' not in st.session_state:
    st.session_state.console_output = []

# Custom console output capture
class ConsoleCapture(io.StringIO):
    """Capture console output and send to message queue"""
    def __init__(self, msg_queue):
        super().__init__()
        self.msg_queue = msg_queue
        self.buffer = ""
    
    def write(self, text):
        if text and text.strip():
            self.buffer += text
            if '\n' in text:
                lines = self.buffer.split('\n')
                for line in lines[:-1]:
                    if line.strip():
                        self.msg_queue.put({
                            "type": "console",
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "message": line.strip()
                        })
                self.buffer = lines[-1]
        return len(text)
    
    def flush(self):
        pass

def render_markdown_with_mermaid(markdown_content):
    """Render markdown content with mermaid diagrams"""
    # Find all mermaid code blocks
    mermaid_pattern = r'```mermaid\n(.*?)```'
    mermaid_blocks = re.findall(mermaid_pattern, markdown_content, re.DOTALL)
    
    if not mermaid_blocks:
        # No mermaid blocks, just render as regular markdown
        st.markdown(markdown_content, unsafe_allow_html=True)
        return
    
    # Split content by mermaid blocks
    parts = re.split(mermaid_pattern, markdown_content, flags=re.DOTALL)
    
    # Render alternating markdown and mermaid blocks
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular markdown content
            if part.strip():
                st.markdown(part, unsafe_allow_html=True)
        else:
            # Mermaid diagram
            mermaid_code = part.strip()
            # Create unique ID for each diagram using timestamp and random
            diagram_id = f"mermaid-{abs(hash(mermaid_code + str(time.time()))) % 100000}"
            
            # Create HTML with mermaid rendering
            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        background: #f8f9fa;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    }}
                    .mermaid-container {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        overflow-x: auto;
                    }}
                    .mermaid {{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                </style>
            </head>
            <body>
                <div class="mermaid-container">
                    <div class="mermaid" id="{diagram_id}">
{mermaid_code}
                    </div>
                </div>
                <script>
                    mermaid.initialize({{ 
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose',
                        flowchart: {{
                            useMaxWidth: true,
                            htmlLabels: true,
                            curve: 'basis'
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            components.html(html_code, height=450, scrolling=True)

def add_progress_log(message, level="info", use_queue=False):
    """Add a message to the progress log
    
    Args:
        message: The log message
        level: The log level (info, success, error)
        use_queue: If True, use thread-safe queue (for background threads)
    """
    if use_queue:
        # Use queue for thread-safe communication from background threads
        st.session_state.message_queue.put({
            "type": "log",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "level": level
        })
    else:
        # Direct access (main thread only)
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.progress_log.append({
            "timestamp": timestamp,
            "message": message,
            "level": level
        })

def add_generated_file_to_queue(file_info):
    """Thread-safe way to communicate generated files from background thread"""
    st.session_state.message_queue.put({
        "type": "file",
        "file_info": file_info
    })

def process_message_queue():
    """Process messages from the queue (call from main thread)"""
    try:
        while True:
            msg = st.session_state.message_queue.get_nowait()
            if msg["type"] == "log":
                st.session_state.progress_log.append({
                    "timestamp": msg["timestamp"],
                    "message": msg["message"],
                    "level": msg["level"]
                })
            elif msg["type"] == "console":
                st.session_state.console_output.append({
                    "timestamp": msg["timestamp"],
                    "message": msg["message"]
                })
                # Also add to progress log
                st.session_state.progress_log.append({
                    "timestamp": msg["timestamp"],
                    "message": msg["message"],
                    "level": "info"
                })
            elif msg["type"] == "file":
                st.session_state.generated_files.append(msg["file_info"])
            elif msg["type"] == "output_dir":
                st.session_state.output_dir = msg["path"]
                if not st.session_state.expected_output_dir:
                    st.session_state.expected_output_dir = msg["path"]
            elif msg["type"] == "step":
                st.session_state.current_step = msg["step"]
            elif msg["type"] == "error":
                st.session_state.error_message = msg["message"]
            elif msg["type"] == "complete":
                st.session_state.tutorial_running = False
                st.session_state.tutorial_complete = msg["success"]
    except queue.Empty:
        pass

def monitor_output_directory_thread(output_dir, stop_event, msg_queue):
    """Monitor output directory for new files in a background thread"""
    known_files = set()
    
    while not stop_event.is_set():
        try:
            if os.path.exists(output_dir):
                current_files = set()
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            current_files.add(file_path)
                
                # Check for new files
                new_files = current_files - known_files
                for file_path in sorted(new_files):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_info = {
                            'path': file_path,
                            'filename': os.path.basename(file_path),
                            'content': content,
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'size': len(content)
                        }
                        msg_queue.put({
                            "type": "file",
                            "file_info": file_info
                        })
                        msg_queue.put({
                            "type": "log",
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "message": f"Generated: {file_info['filename']}",
                            "level": "success"
                        })
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
                
                known_files = current_files
        except Exception as e:
            print(f"Error monitoring directory: {e}")
        
        time.sleep(1)  # Check every second

def check_output_directory(output_dir):
    """Check output directory for files and return list (called from main thread)"""
    files_found = []
    
    try:
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in sorted(files):
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            file_info = {
                                'path': file_path,
                                'filename': os.path.basename(file_path),
                                'content': content,
                                'timestamp': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%H:%M:%S"),
                                'size': len(content)
                            }
                            files_found.append(file_info)
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
    except Exception as e:
        print(f"Error checking directory: {e}")
    
    return files_found

def run_tutorial_generation_thread(config, msg_queue, stop_event):
    """Run the tutorial generation in a background thread"""
    # Capture stdout and stderr
    console_capture = ConsoleCapture(msg_queue)
    
    try:
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"), 
                       "message": "Starting tutorial generation...", "level": "info"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Source: {config.get('repo_url') or config.get('local_dir')}", "level": "info"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Language: {config.get('language', 'English').capitalize()}", "level": "info"})
        
        # Initialize the shared dictionary
        shared = {
            "repo_url": config.get("repo_url"),
            "local_dir": config.get("local_dir"),
            "project_name": config.get("project_name"),
            "github_token": config.get("github_token"),
            "output_dir": config.get("output_dir", "output"),
            "include_patterns": config.get("include_patterns", DEFAULT_INCLUDE_PATTERNS),
            "exclude_patterns": config.get("exclude_patterns", DEFAULT_EXCLUDE_PATTERNS),
            "max_file_size": config.get("max_file_size", 100000),
            "language": config.get("language", "english"),
            "use_cache": config.get("use_cache", True),
            "max_abstraction_num": config.get("max_abstractions", 10),
            "files": [],
            "abstractions": [],
            "relationships": {},
            "chapter_order": [],
            "chapters": [],
            "final_output_dir": None
        }
        
        # Determine output directory path
        project_name = config.get("project_name")
        if not project_name:
            if config.get("repo_url"):
                project_name = config.get("repo_url").split("/")[-1].replace(".git", "")
            else:
                project_name = os.path.basename(os.path.abspath(config.get("local_dir")))
        
        expected_output_dir = os.path.join(config.get("output_dir", "output"), project_name)
        msg_queue.put({"type": "output_dir", "path": expected_output_dir})
        
        # Start file monitoring
        monitor_thread = threading.Thread(
            target=monitor_output_directory_thread,
            args=(expected_output_dir, stop_event, msg_queue),
            daemon=True
        )
        monitor_thread.start()
        
        # Create and run the flow
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Initializing workflow...", "level": "info"})
        msg_queue.put({"type": "step", "step": "Initializing"})
        
        tutorial_flow = create_tutorial_flow()
        
        # Run the flow - it will handle all the steps internally
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Running tutorial generation workflow...", "level": "info"})
        msg_queue.put({"type": "step", "step": "Running Workflow"})
        
        # Redirect stdout and stderr to capture console output
        with redirect_stdout(console_capture), redirect_stderr(console_capture):
            tutorial_flow.run(shared)
        
        # Stop monitoring
        stop_event.set()
        monitor_thread.join(timeout=2)
        
        # Signal completion
        msg_queue.put({"type": "output_dir", "path": shared.get("final_output_dir")})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Tutorial generation complete!", "level": "success"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Output saved to: {shared.get('final_output_dir')}", "level": "success"})
        msg_queue.put({"type": "complete", "success": True})
        
    except Exception as e:
        error_msg = str(e)
        msg_queue.put({"type": "error", "message": error_msg})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Error: {error_msg}", "level": "error"})
        # Log full traceback for debugging
        tb = traceback.format_exc()
        print(f"Error traceback:\n{tb}")
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Check the terminal for detailed error information", "level": "info"})
        msg_queue.put({"type": "complete", "success": False})
    finally:
        if stop_event:
            stop_event.set()

def render_home():
    """Render the home page"""
    st.markdown('<h1 class="main-header">◈ CodeSensei</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform Any Codebase into Easy-to-Follow Tutorials with AI</p>', unsafe_allow_html=True)
    
    # Hero section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="section-header">
            {icon("info")}
            <h3 style="margin: 0;">What is CodeSensei?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        CodeSensei is an AI-powered tool that analyzes codebases and automatically generates 
        beginner-friendly tutorials. It identifies core concepts, explains relationships, 
        and creates structured learning materials with examples and diagrams.
        """)
        
        st.markdown(f"""
        <div class="section-header">
            {icon("sparkles")}
            <h3 style="margin: 0;">Key Features</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        - {icon("cpu", 18)} **AI-Powered Analysis** - Uses advanced LLMs to understand code structure
        - {icon("layers", 18)} **Structured Tutorials** - Generates organized chapters with examples
        - {icon("globe", 18)} **Multi-Language Support** - Create tutorials in any language
        - {icon("workflow", 18)} **Visual Diagrams** - Includes Mermaid diagrams for clarity
        - {icon("github", 18)} **GitHub Integration** - Analyze any public or private repository
        - {icon("folder", 18)} **Local Support** - Works with local codebases too
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="section-header">
            {icon("zap")}
            <h3 style="margin: 0;">How It Works</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        1. {icon("download", 18)} **Fetch** - Clone or scan the codebase
        2. {icon("search", 18)} **Analyze** - AI identifies core abstractions and concepts
        3. {icon("list-ordered", 18)} **Structure** - Determines the best teaching order
        4. {icon("file-text", 18)} **Generate** - Creates detailed tutorial chapters
        5. {icon("package", 18)} **Export** - Download as Markdown files
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Get Started", type="primary", use_container_width=True):
            st.session_state.page = 'configure'
            st.rerun()
    
    # Examples section
    st.markdown("---")
    st.markdown(f"""
    <div class="section-header">
        {icon("book")}
        <h3 style="margin: 0;">Example Tutorials Generated by AI</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"{icon('code', 18)} **FastAPI** - API Framework", unsafe_allow_html=True)
        st.markdown("Tutorial for building modern APIs")
    with col2:
        st.markdown(f"{icon('code', 18)} **Flask** - Web Framework", unsafe_allow_html=True)
        st.markdown("Tutorial for web development")
    with col3:
        st.markdown(f"{icon('code', 18)} **CrewAI** - Multi-Agent AI", unsafe_allow_html=True)
        st.markdown("Tutorial for AI agent systems")

def render_configure():
    """Render the configuration page"""
    st.markdown('<h1 class="main-header">⚙ Tutorial Generation</h1>', unsafe_allow_html=True)
    
    # Source selection
    st.markdown(f"""
    <div class="section-header">
        {icon("folder-input")}
        <h3 style="margin: 0;">Source Selection</h3>
    </div>
    """, unsafe_allow_html=True)
    
    source_type = st.radio(
        "Choose your source:",
        ["GitHub Repository", "Local Directory"],
        horizontal=True
    )
    
    config = {}
    
    if source_type == "GitHub Repository":
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/username/repo",
            help="Enter the URL of the GitHub repository you want to analyze"
        )
        config['repo_url'] = repo_url
        
        # GitHub Token section
        env_token = os.environ.get('GITHUB_TOKEN')
        if env_token:
            st.success("Using GitHub token from environment")
            if st.checkbox("Override with different token", key="override_token"):
                custom_token = st.text_input(
                    "Custom GitHub Token",
                    type="password",
                    help="Enter a different token to override the environment token"
                )
                config['github_token'] = custom_token if custom_token else env_token
            else:
                config['github_token'] = env_token
        else:
            st.info("No GitHub token found in environment")
            custom_token = st.text_input(
                "GitHub Token (Optional)",
                type="password",
                help="Required for private repositories or to avoid rate limits"
            )
            config['github_token'] = custom_token if custom_token else None
    else:
        local_dir = st.text_input(
            "Local Directory Path",
            placeholder="/path/to/your/codebase",
            help="Enter the full path to your local codebase"
        )
        config['local_dir'] = local_dir
    
    # Project settings
    st.markdown(f"""
    <div class="section-header">
        {icon("sliders")}
        <h3 style="margin: 0;">Project Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input(
            "Project Name (Optional)",
            placeholder="Auto-detected from URL/path",
            help="Leave empty to auto-detect from repository/directory name"
        )
        if project_name:
            config['project_name'] = project_name
        
        language = st.selectbox(
            "Tutorial Language",
            ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Hindi", "Portuguese"],
            help="Language for the generated tutorial"
        )
        config['language'] = language.lower()
    
    with col2:
        max_abstractions = st.slider(
            "Max Abstractions",
            min_value=5,
            max_value=20,
            value=10,
            help="Maximum number of core concepts to identify"
        )
        config['max_abstractions'] = max_abstractions
        
        use_cache = st.checkbox(
            "Enable LLM Caching",
            value=True,
            help="Cache LLM responses to speed up re-runs"
        )
        config['use_cache'] = use_cache
    
    # File patterns
    st.markdown(f"""
    <div class="section-header">
        {icon("file-code")}
        <h3 style="margin: 0;">File Patterns</h3>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("Advanced: File Include/Exclude Patterns"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_patterns_str = st.text_area(
                "Include Patterns (one per line)",
                value="\n".join(DEFAULT_INCLUDE_PATTERNS),
                height=150,
                help="File patterns to include in analysis"
            )
            config['include_patterns'] = set(include_patterns_str.strip().split('\n'))
        
        with col2:
            exclude_patterns_str = st.text_area(
                "Exclude Patterns (one per line)",
                value="\n".join(DEFAULT_EXCLUDE_PATTERNS),
                height=150,
                help="File patterns to exclude from analysis"
            )
            config['exclude_patterns'] = set(exclude_patterns_str.strip().split('\n'))
        
        max_file_size = st.number_input(
            "Maximum File Size (bytes)",
            min_value=10000,
            max_value=1000000,
            value=100000,
            step=10000,
            help="Maximum file size to include in analysis"
        )
        config['max_file_size'] = max_file_size
    
    # Output settings
    st.markdown(f"""
    <div class="section-header">
        {icon("save")}
        <h3 style="margin: 0;">Output Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    output_dir = st.text_input(
        "Output Directory",
        value="output",
        help="Directory where tutorial files will be saved"
    )
    config['output_dir'] = output_dir
    
    # Validation and generation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Back", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    with col3:
        can_generate = (config.get('repo_url') or config.get('local_dir'))
        
        if st.button("Generate Tutorial", type="primary", disabled=not can_generate, use_container_width=True):
            # Check if API key is configured
            if not (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_PROJECT_ID") or os.getenv("LLM_PROVIDER")):
                st.error("Please configure your LLM API key in environment variables (GEMINI_API_KEY or set LLM_PROVIDER)")
            else:
                st.session_state.page = 'generate'
                st.session_state.generation_config = config
                st.rerun()

def render_generate():
    """Render the generation progress page"""
    st.markdown('<h1 class="main-header">⟳ Tutorial Generation</h1>', unsafe_allow_html=True)
    
    # Process messages from the background thread
    process_message_queue()
    
    # Start generation if not already running or complete
    if not st.session_state.tutorial_running and not st.session_state.tutorial_complete:
        st.session_state.tutorial_running = True
        st.session_state.progress_log = []
        st.session_state.generated_files = []
        st.session_state.known_files = set()
        st.session_state.error_message = None
        
        # Create stop event for the threads
        stop_event = threading.Event()
        
        # Start generation in background thread
        config = st.session_state.generation_config.copy()
        generation_thread = threading.Thread(
            target=run_tutorial_generation_thread,
            args=(config, st.session_state.message_queue, stop_event),
            daemon=True
        )
        generation_thread.start()
        st.session_state.generation_thread = generation_thread
    
    # Progress overview
    steps = [
        ("Fetch", "Fetch Repository", "download"),
        ("Identify", "Identify Abstractions", "search"),
        ("Analyze", "Analyze Relationships", "git-branch"),
        ("Order", "Order Chapters", "list-ordered"),
        ("Write", "Write Chapters", "edit"),
        ("Combine", "Combine Tutorial", "package")
    ]
    
    current_step_index = -1
    if st.session_state.current_step:
        for i, (_, step_name, _) in enumerate(steps):
            if st.session_state.current_step and step_name in st.session_state.current_step:
                current_step_index = i
                break
    
    # Display progress steps
    cols = st.columns(len(steps))
    for i, (label, step_name, icon_name) in enumerate(steps):
        with cols[i]:
            if i < current_step_index:
                st.markdown(f"{icon(icon_name, 16)} **{label}** {icon('check', 16)}", unsafe_allow_html=True)
            elif i == current_step_index:
                st.markdown(f"{icon(icon_name, 16)} **{label}** {icon('loader-2', 16)}", unsafe_allow_html=True)
            else:
                st.markdown(f"{icon(icon_name, 16)} {label}", unsafe_allow_html=True)
    
    st.progress((current_step_index + 1) / len(steps) if current_step_index >= 0 else 0)
    
    # Create two columns for log and generated files
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Live log
        st.markdown(f"""
        <div class="section-header">
            {icon("terminal")}
            <h3 style="margin: 0;">Progress Log</h3>
        </div>
        """, unsafe_allow_html=True)
        log_container = st.container()
        
        with log_container:
            if st.session_state.progress_log:
                # Show all logs in chronological order (oldest first)
                log_display = st.container()
                with log_display:
                    # Create a scrollable text area for logs
                    log_text = ""
                    for entry in st.session_state.progress_log:
                        timestamp = entry['timestamp']
                        message = entry['message']
                        log_text += f"[{timestamp}] {message}\n"
                    
                    st.text_area(
                        "Console Output",
                        value=log_text,
                        height=400,
                        disabled=True,
                        label_visibility="collapsed"
                    )
            else:
                st.info("Starting generation process...")
    
    with col2:
        # Generated files display
        st.markdown(f"""
        <div class="section-header">
            {icon("files")}
            <h3 style="margin: 0;">Generated Files</h3>
        </div>
        """, unsafe_allow_html=True)
        files_container = st.container()
        
        with files_container:
            if st.session_state.generated_files:
                st.markdown(f'<div class="file-count">{icon("check-circle", 16)} {len(st.session_state.generated_files)} file(s) generated</div>', unsafe_allow_html=True)
                
                # Show files in reverse order (most recent first)
                for file_info in reversed(st.session_state.generated_files[-10:]):
                    with st.expander(f"{file_info['filename']} - {file_info['timestamp']}", expanded=False):
                        st.markdown(f"**Size:** {file_info['size']} characters")
                        st.markdown("---")
                        # Show a preview of the content (first 800 chars)
                        preview = file_info['content'][:800]
                        if len(file_info['content']) > 800:
                            preview += "\n\n... *(click 'View Full Results' when complete to see full content)*"
                        render_markdown_with_mermaid(preview)
            else:
                st.info("No files generated yet. Files will appear here as they are created...")
    
    # Handle completion - Show results inline
    if st.session_state.tutorial_complete and st.session_state.output_dir:
        st.markdown("---")
        st.success("✓ Tutorial generation complete!")
        
        output_dir = st.session_state.output_dir
        
        # Statistics
        st.markdown(f"""
        <div class="section-header">
            {icon("bar-chart")}
            <h3 style="margin: 0;">Tutorial Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Count files
        md_files = list(Path(output_dir).glob("*.md"))
        chapter_files = [f for f in md_files if f.name != "index.md"]
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                {icon("book-open", 24)}
                <h3>{len(chapter_files)}</h3>
                <p>Chapters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_size = sum(f.stat().st_size for f in md_files)
            st.markdown(f"""
            <div class="metric-card">
                {icon("hard-drive", 24)}
                <h3>{total_size // 1024}KB</h3>
                <p>Total Size</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                {icon("file-text", 24)}
                <h3>{len(md_files)}</h3>
                <p>Total Files</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            project_name = Path(output_dir).name
            st.markdown(f"""
            <div class="metric-card">
                {icon("folder", 24)}
                <h3>{project_name}</h3>
                <p>Project</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Download section
        st.markdown(f"""
        <div class="section-header">
            {icon("download")}
            <h3 style="margin: 0;">Download Tutorial</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in md_files:
                    zip_file.write(file, file.name)
            
            zip_buffer.seek(0)
            st.download_button(
                label="↓ Download as ZIP",
                data=zip_buffer,
                file_name=f"{project_name}_tutorial.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        with col2:
            # Create combined markdown file
            combined_md = io.StringIO()
            
            # Read index first
            index_path = Path(output_dir) / "index.md"
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    combined_md.write(f.read())
                    combined_md.write("\n\n---\n\n")
            
            # Add all chapter files
            for chapter_file in sorted(chapter_files):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    combined_md.write(f.read())
                    combined_md.write("\n\n---\n\n")
            
            st.download_button(
                label="↓ Download Combined MD",
                data=combined_md.getvalue(),
                file_name=f"{project_name}_tutorial_combined.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col3:
            st.download_button(
                label="↓ Download as PDF",
                data=b"",  # Placeholder - will implement PDF generation
                file_name=f"{project_name}_tutorial.pdf",
                mime="application/pdf",
                use_container_width=True,
                disabled=True,
                help="PDF export coming soon - requires additional dependencies"
            )
        
        # Tutorial preview
        st.markdown(f"""
        <div class="section-header">
            {icon("eye")}
            <h3 style="margin: 0;">Tutorial Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Read index.md
        index_path = Path(output_dir) / "index.md"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            with st.expander("Index Page", expanded=True):
                render_markdown_with_mermaid(index_content)
        
        # List chapters
        if chapter_files:
            st.markdown(f"""
            <div class="section-header">
                {icon("book")}
                <h3 style="margin: 0;">Chapters</h3>
            </div>
            """, unsafe_allow_html=True)
            
            selected_chapter = st.selectbox(
                "Select a chapter to preview:",
                options=[f.name for f in sorted(chapter_files)],
                format_func=lambda x: x.replace('.md', '').replace('_', ' ').title()
            )
            
            if selected_chapter:
                chapter_path = Path(output_dir) / selected_chapter
                with open(chapter_path, 'r', encoding='utf-8') as f:
                    chapter_content = f.read()
                
                with st.expander(f"{selected_chapter}", expanded=True):
                    render_markdown_with_mermaid(chapter_content)
        
        # Option to generate another tutorial
        st.markdown("---")
        if st.button("⟳ Generate Another Tutorial", use_container_width=True):
            st.session_state.page = 'configure'
            st.session_state.tutorial_complete = False
            st.session_state.tutorial_running = False
            st.session_state.output_dir = None
            st.session_state.progress_log = []
            st.session_state.generated_files = []
            st.session_state.console_output = []
            st.rerun()
    
    # Handle errors
    if st.session_state.error_message:
        st.error(f"Error occurred: {st.session_state.error_message}")
        if st.button("Try Again"):
            st.session_state.tutorial_running = False
            st.session_state.tutorial_complete = False
            st.session_state.error_message = None
            st.session_state.page = 'configure'
            st.rerun()
    
    # Auto-refresh while generation is running to show real-time updates
    if st.session_state.tutorial_running and not st.session_state.tutorial_complete:
        time.sleep(2)  # Wait 2 seconds before rerunning to check for updates
        st.rerun()

def render_results():
    """Render the results page"""
    st.markdown('<h1 class="main-header">✓ Tutorial Results</h1>', unsafe_allow_html=True)
    
    if not st.session_state.output_dir or not os.path.exists(st.session_state.output_dir):
        st.error("No tutorial found. Please generate a tutorial first.")
        if st.button("Go Back"):
            st.session_state.page = 'home'
            st.rerun()
        return
    
    output_dir = st.session_state.output_dir
    
    # Statistics
    st.markdown(f"""
    <div class="section-header">
        {icon("bar-chart")}
        <h3 style="margin: 0;">Tutorial Statistics</h3>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    # Count files
    md_files = list(Path(output_dir).glob("*.md"))
    chapter_files = [f for f in md_files if f.name != "index.md"]
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            {icon("book-open", 24)}
            <h3>{len(chapter_files)}</h3>
            <p>Chapters</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_size = sum(f.stat().st_size for f in md_files)
        st.markdown(f"""
        <div class="metric-card">
            {icon("hard-drive", 24)}
            <h3>{total_size // 1024}KB</h3>
            <p>Total Size</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            {icon("file-text", 24)}
            <h3>{len(md_files)}</h3>
            <p>Total Files</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        project_name = Path(output_dir).name
        st.markdown(f"""
        <div class="metric-card">
            {icon("folder", 24)}
            <h3>{project_name}</h3>
            <p>Project</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Preview
    st.markdown(f"""
    <div class="section-header">
        {icon("eye")}
        <h3 style="margin: 0;">Tutorial Preview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Read index.md
    index_path = Path(output_dir) / "index.md"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        with st.expander("Index Page", expanded=True):
            render_markdown_with_mermaid(index_content)
    
    # List chapters
    if chapter_files:
        st.markdown(f"""
        <div class="section-header">
            {icon("book")}
            <h3 style="margin: 0;">Chapters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        selected_chapter = st.selectbox(
            "Select a chapter to preview:",
            options=[f.name for f in sorted(chapter_files)],
            format_func=lambda x: x.replace('.md', '').replace('_', ' ').title()
        )
        
        if selected_chapter:
            chapter_path = Path(output_dir) / selected_chapter
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
            
            with st.expander(f"{selected_chapter}", expanded=True):
                render_markdown_with_mermaid(chapter_content)
    
    # Download section
    st.markdown(f"""
    <div class="section-header">
        {icon("download")}
        <h3 style="margin: 0;">Download Tutorial</h3>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in md_files:
                zip_file.write(file, file.name)
        
        zip_buffer.seek(0)
        st.download_button(
            label="Download as ZIP",
            data=zip_buffer,
            file_name=f"{project_name}_tutorial.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    with col2:
        if st.button("Generate Another Tutorial", use_container_width=True):
            st.session_state.page = 'configure'
            st.session_state.tutorial_complete = False
            st.session_state.output_dir = None
            st.rerun()

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ◆ CodeSensei", unsafe_allow_html=False)
        st.markdown("AI-Powered Tutorial Generator")
        st.markdown("---")
        
        # Navigation
        st.markdown("**Navigation**")
        
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("Tutorial Generation", use_container_width=True, key="nav_config"):
            st.session_state.page = 'configure'
            st.rerun()
        
        if st.session_state.output_dir:
            if st.button("Results", use_container_width=True, key="nav_results"):
                st.session_state.page = 'results'
                st.rerun()
        
        st.markdown("---")
        
        # Settings Panel with API Configuration
        with st.expander("Settings", expanded=False):
            st.markdown("**API Configuration**")
            
            # Current API Status
            if os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_PROJECT_ID"):
                st.success("Gemini API Configured")
            elif os.getenv("LLM_PROVIDER"):
                st.success(f"{os.getenv('LLM_PROVIDER')} Configured")
            else:
                st.error("No API Key Found")
                st.caption("Set GEMINI_API_KEY or configure LLM_PROVIDER in environment")
            
            # GitHub Token Status
            st.markdown("**GitHub Token**")
            if os.getenv("GITHUB_TOKEN"):
                st.success("GitHub Token Loaded")
            else:
                st.info("No GitHub Token")
                st.caption("Set GITHUB_TOKEN in environment for private repos")
            
            st.markdown("---")
            st.caption("Configure API keys via environment variables or .env file")
    
    # Main content routing
    if st.session_state.page == 'home':
        render_home()
    elif st.session_state.page == 'configure':
        render_configure()
    elif st.session_state.page == 'generate':
        render_generate()
    elif st.session_state.page == 'results':
        render_results()

if __name__ == "__main__":
    main()

