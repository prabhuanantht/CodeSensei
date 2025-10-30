import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import shutil
import zipfile
import io
import json
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

# Try to import RAG Chatbot - optional feature
try:
    from rag_chatbot import CodebaseRAG
    RAG_AVAILABLE = True
    RAG_IMPORT_ERROR = None
except ImportError as e:
    RAG_AVAILABLE = False
    RAG_IMPORT_ERROR = str(e)

# Try to import Security Analyzer - optional feature
try:
    from security_analyzer import SecurityAnalyzer
    SECURITY_AVAILABLE = True
    SECURITY_IMPORT_ERROR = None
except ImportError as e:
    SECURITY_AVAILABLE = False
    SECURITY_IMPORT_ERROR = str(e)

# Try to import Intelligence Analyzer - optional feature
try:
    from intelligence_analyzer import CodeIntelligenceAnalyzer
    INTELLIGENCE_AVAILABLE = True
    INTELLIGENCE_IMPORT_ERROR = None
except ImportError as e:
    INTELLIGENCE_AVAILABLE = False
    INTELLIGENCE_IMPORT_ERROR = str(e)

# Page config
st.set_page_config(
    page_title="CodeSensei",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Unicode Icons Mapping
ICONS = {
    'book-open': '◈', 'info': 'ⓘ', 'sparkles': '✦', 'cpu': '◉', 'layers': '▦',
    'globe': '◎', 'workflow': '⚡', 'github': '⎇', 'folder': '▣', 'download': '↓',
    'search': '⌕', 'list-ordered': '≡', 'file-text': '▤', 'package': '▦', 'book': '▥',
    'code': '⟨⟩', 'settings': '⚙', 'folder-input': '▣', 'sliders': '⚙', 'file-code': '⟨/⟩',
    'save': '◫', 'loader': '⟳', 'check': '✓', 'loader-2': '⟳', 'git-branch': '⎇',
    'edit': '✎', 'terminal': '▶', 'files': '▥', 'check-circle': '✓', 'bar-chart': '▥',
    'hard-drive': '◫', 'eye': '◉', 'graduation-cap': '◆', 'navigation': '⌘',
    'home': '⌂', 'key': '◈',
}

def icon(name, size=16):
    """Return a unicode icon"""
    return f'<span style="font-size: {size}px;">{ICONS.get(name, "●")}</span>'

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #b0b0b0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }
    .metric-card h3 {
        font-size: 2rem;
        margin: 0.5rem 0;
        color: #ffffff;
    }
    .metric-card p {
        color: #b0b0b0;
        margin: 0;
    }
    .file-count {
        padding: 0.5rem;
        background: rgba(0, 255, 0, 0.1);
        border-radius: 4px;
        margin-bottom: 1rem;
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
    .section-header span {
        opacity: 0.9;
    }
    
    /* Enhanced tab styling */
    [data-testid="stTabs"] > div > div > div > button {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding: 0.75rem 2rem !important;
        margin: 0 0.5rem !important;
        flex: 1 !important;
        min-width: auto !important;
        max-width: none !important;
        text-align: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stTabs"] > div > div > div {
        display: flex !important;
        justify-content: space-between !important;
        gap: 1rem !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
# Core codebase state
if 'codebase_source' not in st.session_state:
    st.session_state.codebase_source = None
if 'codebase_type' not in st.session_state:
    st.session_state.codebase_type = None
if 'codebase_loaded' not in st.session_state:
    st.session_state.codebase_loaded = False

# Tutorial Generation state
if 'tutorial_running' not in st.session_state:
    st.session_state.tutorial_running = False
if 'tutorial_complete' not in st.session_state:
    st.session_state.tutorial_complete = False
if 'tutorial_progress_log' not in st.session_state:
    st.session_state.tutorial_progress_log = []
if 'tutorial_output_dir' not in st.session_state:
    st.session_state.tutorial_output_dir = None
if 'tutorial_error' not in st.session_state:
    st.session_state.tutorial_error = None
if 'tutorial_files' not in st.session_state:
    st.session_state.tutorial_files = []
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = queue.Queue()
if 'generation_thread' not in st.session_state:
    st.session_state.generation_thread = None
if 'console_output' not in st.session_state:
    st.session_state.console_output = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = None
if 'tutorial_preview_chapter' not in st.session_state:
    st.session_state.tutorial_preview_chapter = None

# Code Intelligence state
if 'complexity_analysis' not in st.session_state:
    st.session_state.complexity_analysis = None
if 'orphan_code_detection' not in st.session_state:
    st.session_state.orphan_code_detection = None
if 'code_similarity' not in st.session_state:
    st.session_state.code_similarity = None
if 'code_patterns' not in st.session_state:
    st.session_state.code_patterns = None
# Results from analysis
if 'complexity_results' not in st.session_state:
    st.session_state.complexity_results = None
if 'orphan_results' not in st.session_state:
    st.session_state.orphan_results = None
if 'similarity_results' not in st.session_state:
    st.session_state.similarity_results = None
if 'pattern_results' not in st.session_state:
    st.session_state.pattern_results = None

# Code Security state
if 'vulnerability_scan' not in st.session_state:
    st.session_state.vulnerability_scan = None
if 'security_running' not in st.session_state:
    st.session_state.security_running = False

# RAG Chatbot state
if 'rag_chatbot' not in st.session_state:
    st.session_state.rag_chatbot = None
if 'rag_indexed' not in st.session_state:
    st.session_state.rag_indexed = False
if 'rag_stats' not in st.session_state:
    st.session_state.rag_stats = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Helper Functions
class ConsoleCapture:
    """Capture console output and send to message queue while also printing"""
    def __init__(self, msg_queue, original_stdout):
        self.msg_queue = msg_queue
        self.original_stdout = original_stdout
        self.buffer = ""
    
    def write(self, text):
        # Write to original stdout (console)
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # Also send to message queue for UI
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
        self.original_stdout.flush()

def process_message_queue():
    """Process messages from the queue (call from main thread)"""
    try:
        while True:
            msg = st.session_state.message_queue.get_nowait()
            if msg["type"] == "log":
                st.session_state.tutorial_progress_log.append({
                    "timestamp": msg["timestamp"],
                    "message": msg["message"],
                    "level": msg["level"]
                })
            elif msg["type"] == "console":
                timestamp = msg.get("timestamp", "")
                message = msg.get("message", "")
                log_line = f"[{timestamp}] {message}" if timestamp else message
                st.session_state.console_output.append(log_line)
                
                st.session_state.tutorial_progress_log.append({
                    "timestamp": timestamp,
                    "message": message,
                    "level": "info"
                })
            elif msg["type"] == "file":
                st.session_state.tutorial_files.append(msg["file_info"])
            elif msg["type"] == "output_dir":
                st.session_state.tutorial_output_dir = msg["path"]
            elif msg["type"] == "step":
                st.session_state.current_step = msg["step"]
            elif msg["type"] == "error":
                st.session_state.tutorial_error = msg["message"]
            elif msg["type"] == "complete":
                st.session_state.tutorial_running = False
                st.session_state.tutorial_complete = msg["success"]
    except queue.Empty:
        pass

def run_tutorial_generation_thread(config, msg_queue):
    """Run the tutorial generation in a background thread"""
    console_capture_stdout = ConsoleCapture(msg_queue, sys.stdout)
    console_capture_stderr = ConsoleCapture(msg_queue, sys.stderr)
    
    try:
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"), 
                       "message": "Starting tutorial generation...", "level": "info"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Source: {config['source']}", "level": "info"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Language: {config.get('language', 'English')}", "level": "info"})
        
        # Determine output directory and project name
        if config['source_type'] == 'github':
            project_name = config['source'].rstrip('/').split('/')[-1].replace('.git', '')
        else:
            project_name = Path(config['source']).name
        
        expected_output_dir = os.path.join("./output", project_name)
        msg_queue.put({"type": "output_dir", "path": expected_output_dir})
        
        # Create shared dictionary for tutorial flow
        # Handle repo_url - add @ prefix if not already present
        repo_url = config['source'] if config['source_type'] == 'github' else None
        if repo_url and not repo_url.startswith('@'):
            repo_url = f"{repo_url}"
        
        shared = {
            "repo_url": repo_url,
            "local_dir": config['source'] if config['source_type'] == 'local' else None,
            "project_name": project_name,
            "github_token": os.getenv('GITHUB_TOKEN'),
            "output_dir": "./output",
            "include_patterns": config.get('include_patterns', DEFAULT_INCLUDE_PATTERNS),
            "exclude_patterns": config.get('exclude_patterns', DEFAULT_EXCLUDE_PATTERNS),
            "max_file_size": 100000,
            "language": config.get('language', 'english').lower(),
            "use_cache": config.get('use_cache', True),
            "max_abstraction_num": 10,
            "files": [],
            "abstractions": [],
            "relationships": {},
            "chapter_order": [],
            "chapters": [],
            "final_output_dir": None
        }
        
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Initializing workflow...", "level": "info"})
        
        # Check if GitHub token is needed
        if config['source_type'] == 'github' and not os.getenv('GITHUB_TOKEN'):
            msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                           "message": "⚠️ Warning: No GITHUB_TOKEN found. Private repos may fail.", "level": "warning"})
        
        tutorial_flow = create_tutorial_flow()
        
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Running tutorial generation workflow...", "level": "info"})
        
        # Cache downloaded files for chatbot use (if GitHub repo)
        cache_dir = None
        if config['source_type'] == 'github':
            cache_base = Path("./cache")
            cache_dir = cache_base / project_name
            cache_dir.mkdir(parents=True, exist_ok=True)
            msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                           "message": f"Caching files to: {cache_dir}", "level": "info"})
        
        # Redirect stdout and stderr to capture console output
        with redirect_stdout(console_capture_stdout), redirect_stderr(console_capture_stderr):
            tutorial_flow.run(shared)
        
        # Save fetched files to cache directory
        if cache_dir and shared.get("files"):
            msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                           "message": f"Saving {len(shared['files'])} files to cache...", "level": "info"})
            for file_path, content in shared["files"]:
                try:
                    cached_file = cache_dir / file_path
                    cached_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(cached_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                                   "message": f"Error caching file {file_path}: {str(e)}", "level": "warning"})
            
            msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                           "message": f"✅ Files cached successfully at: {cache_dir}", "level": "success"})
        
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": "Tutorial generation complete!", "level": "success"})
        msg_queue.put({"type": "output_dir", "path": shared.get("final_output_dir", expected_output_dir)})
        msg_queue.put({"type": "complete", "success": True})
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Error: {str(e)}", "level": "error"})
        msg_queue.put({"type": "log", "timestamp": datetime.now().strftime("%H:%M:%S"),
                       "message": f"Traceback: {error_trace}", "level": "error"})
        msg_queue.put({"type": "error", "message": f"{str(e)}\n\n{error_trace}"})
        msg_queue.put({"type": "complete", "success": False})

def render_markdown_with_mermaid(markdown_content):
    """Render markdown content with mermaid diagram support"""
    # Check if there are mermaid diagrams
    if '```mermaid' in markdown_content:
        # Split content by mermaid blocks
        parts = re.split(r'```mermaid\n(.*?)\n```', markdown_content, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular markdown
                if part.strip():
                    st.markdown(part)
            else:
                # Mermaid diagram
                mermaid_code = part.strip()
                mermaid_html = f"""
                <div class="mermaid">
                {mermaid_code}
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                </script>
                """
                components.html(mermaid_html, height=400, scrolling=True)
    else:
        st.markdown(markdown_content)

# Tab Render Functions
def render_tutorial_tab():
    """Render the Tutorial Generation tab"""
    st.markdown("## 📚 Tutorial Generation")
    st.markdown("Generate comprehensive, structured tutorials from your codebase.")
    st.markdown("---")
    
    # Configuration section
    if not st.session_state.tutorial_complete and not st.session_state.tutorial_running:
        st.markdown("### ⚙ Configuration")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            language = st.selectbox(
                "Tutorial Language",
                ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
                help="Select the language for the generated tutorial"
            )
        with col2:    
            detail_level = st.select_slider(
                "Detail Level",
                options=["Basic", "Intermediate", "Advanced", "Expert"],
                value="Intermediate",
                help="Select how detailed the tutorial should be"
            )
        with col3:
            max_chapters = st.number_input(
                "Maximum Chapters",
                min_value=3,
                max_value=15,
                value=8,
                help="Maximum number of chapters to generate"
            )
        with col4:
            use_cache = st.checkbox(
                "Enable LLM Caching",
                value=True,
                help="Cache LLM responses to speed up re-runs"
            )
        
        
        # Advanced file patterns
        with st.expander("🔧 Advanced: File Patterns", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Include File Patterns**")
                include_patterns_str = st.text_area(
                    "Include patterns (one per line):",
                    value="\n".join(["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.md"]),
                    height=150,
                    help="Files matching these patterns will be included",
                    key="tut_include_patterns"
                )
            
            with col2:
                st.markdown("**Exclude File Patterns**")
                exclude_patterns_str = st.text_area(
                    "Exclude patterns (one per line):",
                    value="\n".join(["node_modules", "__pycache__", ".git", "venv", "tests"]),
                    height=150,
                    help="Files/directories matching these patterns will be excluded",
                    key="tut_exclude_patterns"
                )
        
        st.markdown("---")
        
        # Generate button
        if st.button("🚀 Generate Tutorial", type="primary", use_container_width=True):
            # Start tutorial generation
            st.session_state.tutorial_running = True
            st.session_state.tutorial_complete = False
            st.session_state.tutorial_error = None
            st.session_state.console_output = []
            st.session_state.tutorial_progress_log = []
            
            # Prepare configuration
            config = {
                "source": st.session_state.codebase_source,
                "source_type": st.session_state.codebase_type,
                "language": language,
                "detail_level": detail_level,
                "max_chapters": max_chapters,
                "use_cache": use_cache,
                "include_patterns": set(line.strip() for line in include_patterns_str.strip().split('\n') if line.strip()),
                "exclude_patterns": set(line.strip() for line in exclude_patterns_str.strip().split('\n') if line.strip())
            }
            
            # Start background thread
            st.session_state.generation_thread = threading.Thread(
                target=run_tutorial_generation_thread,
                args=(config, st.session_state.message_queue),
                daemon=True
            )
            st.session_state.generation_thread.start()
            st.rerun()
    
    # Show progress if running
    if st.session_state.tutorial_running:
        st.markdown("### ⟳ Generating Tutorial...")
        
        # Process message queue
        process_message_queue()
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Estimate progress based on console output
        total_lines = len(st.session_state.console_output)
        progress = min(total_lines / 50, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Processing... ({int(progress * 100)}% estimated)")
        
        # Show console output
        st.markdown("#### 📋 Progress Log")
        if st.session_state.console_output:
            console_text = "\n".join(st.session_state.console_output[-100:])
            st.text_area(
                "Console Output",
                value=console_text,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # Auto-refresh every 2 seconds
        time.sleep(2)
        st.rerun()
    
    # Show results if complete
    if st.session_state.tutorial_complete and st.session_state.tutorial_output_dir:
        st.success("✅ Tutorial Generated Successfully!")
        
        output_path = Path(st.session_state.tutorial_output_dir)
        if output_path.exists():
            md_files = sorted(output_path.glob("*.md"))
            
            # Separate index.md and other chapters
            index_file = None
            chapter_files = []
            
            for f in md_files:
                if f.name == "index.md":
                    index_file = f
                else:
                    chapter_files.append(f)
            
            # Ensure index.md is first in the list for ordering
            if index_file:
                md_files_sorted = [index_file] + sorted(chapter_files)
            else:
                md_files_sorted = sorted(chapter_files)
            
            if md_files:
                st.markdown("### 📄 Generated Tutorial")
                
                # Preview section with navigation
                # Set default selected chapter
                default_index = 0
                if st.session_state.tutorial_preview_chapter:
                    try:
                        default_index = [f.name for f in md_files_sorted].index(st.session_state.tutorial_preview_chapter)
                    except ValueError:
                        pass  # If chapter not found, use default
                
                selected_chapter = st.selectbox(
                    "Select Chapter to Preview",
                    options=[f.name for f in md_files_sorted],
                    index=default_index,
                    format_func=lambda x: "🏠 " + x.replace('.md', '').replace('_', ' ').title() if x == "index.md" else "📄 " + x.replace('.md', '').replace('_', ' ').title()
                )
                
                if selected_chapter:
                    chapter_file = output_path / selected_chapter
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        chapter_content = f.read()
                    
                    # Add an anchor at the top for navigation
                    chapter_title = selected_chapter.replace('.md', '').replace('_', ' ').title()
                    
                    # Track chapter changes
                    if 'last_chapter' not in st.session_state:
                        st.session_state.last_chapter = selected_chapter
                    
                    # If chapter changed, scroll to top using JavaScript
                    if st.session_state.last_chapter != selected_chapter:
                        st.session_state.last_chapter = selected_chapter
                        # Scroll to the beginning - try multiple times with increasing delays
                        st.components.v1.html("""
                        <script>
                            function scrollToTop() {
                                try {
                                    // Try scrolling the iframe content
                                    const iframe = parent.document.querySelector('iframe[title*="streamlit"]');
                                    if (iframe && iframe.contentWindow) {
                                        iframe.contentWindow.scrollTo({top: 0, behavior: 'smooth'});
                                    }
                                    // Scroll the parent window
                                    parent.scrollTo({top: 0, behavior: 'smooth'});
                                    // Scroll current window
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                    // Try scrolling the iframe container
                                    if (iframe) {
                                        iframe.scrollIntoView({block: 'start', behavior: 'smooth'});
                                    }
                                } catch(e) {
                                    // Fallback - immediate scroll
                                    window.scrollTo(0, 0);
                                    parent.scrollTo(0, 0);
                                }
                            }
                            // Run multiple times with delays to ensure scroll completes
                            scrollToTop();
                            setTimeout(scrollToTop, 50);
                            setTimeout(scrollToTop, 150);
                            setTimeout(scrollToTop, 300);
                            setTimeout(scrollToTop, 500);
                        </script>
                        """, height=0)
                    
                    # Display the chapter content with title
                    st.markdown(f"### 📖 {chapter_title}")
                    st.markdown("---")
                    render_markdown_with_mermaid(chapter_content)
                    
                    # Navigation buttons
                    st.markdown("---")
                    current_index = [f.name for f in md_files_sorted].index(selected_chapter)
                    
                    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
                    
                    with nav_col1:
                        if current_index > 0:
                            prev_chapter = md_files_sorted[current_index - 1].name
                            if st.button("⬅ Previous Chapter", use_container_width=True, key=f"prev_{current_index}"):
                                st.session_state.tutorial_preview_chapter = prev_chapter
                                st.rerun()
                        else:
                            st.empty()  # Empty space when no previous button
                    
                    with nav_col2:
                        # Chapter indicator (centered)
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <strong>Chapter {current_index + 1} of {len(md_files_sorted)}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with nav_col3:
                        if current_index < len(md_files_sorted) - 1:
                            next_chapter = md_files_sorted[current_index + 1].name
                            if st.button("Next Chapter ➡", use_container_width=True, key=f"next_{current_index}"):
                                st.session_state.tutorial_preview_chapter = next_chapter
                                st.rerun()
                        else:
                            st.empty()  # Empty space when no next button
                
                # Download section
                st.markdown("### 📥 Download Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    # ZIP download
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for file in md_files:
                            zip_file.write(file, file.name)
                    
                    zip_buffer.seek(0)
                    st.download_button(
                        label="📦 Download as ZIP",
                        data=zip_buffer,
                        file_name=f"tutorial_{Path(st.session_state.codebase_source).name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                with col2:
                    # PDF download (combined markdown)
                    combined_md = io.StringIO()
                    
                    # Write all files in order (index first, then chapters)
                    for file in md_files_sorted:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            combined_md.write(content)
                            combined_md.write("\n\n---\n\n")  # Page break separator
                    
                    combined_content = combined_md.getvalue()
                    st.download_button(
                        label="📄 Download as Combined Markdown",
                        data=combined_content,
                        file_name=f"tutorial_{Path(st.session_state.codebase_source).name}_combined.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
        
        # Generate another tutorial
        st.markdown("---")
        if st.button("🔄 Generate Another Tutorial", use_container_width=True):
            st.session_state.tutorial_complete = False
            st.session_state.tutorial_running = False
            st.session_state.tutorial_output_dir = None
            st.session_state.console_output = []
            st.rerun()
    
    # Show error if any
    if st.session_state.tutorial_error:
        st.error(f"❌ Error occurred: {st.session_state.tutorial_error}")
        if st.button("🔄 Try Again"):
            st.session_state.tutorial_running = False
            st.session_state.tutorial_complete = False
            st.session_state.tutorial_error = None
            st.rerun()

def render_intelligence_tab():
    """Render the Code Intelligence tab"""
    
    if not INTELLIGENCE_AVAILABLE:
        st.error("🧠 Intelligence analyzer not available")
        st.code("Please install: pip install radon networkx", language="bash")
        return
    
    st.markdown("## 🧠 Code Intelligence")
    st.markdown("Deep analysis of your codebase structure and quality.")
    st.markdown("---")
    
    # Get codebase source
    if not st.session_state.get('codebase_source'):
        st.warning("⚠️ Please enter a codebase source first")
        return
    
    # Get files
    files_data = []
    if st.session_state.codebase_type == "github":
        project_name = st.session_state.codebase_source.split("/")[-1].replace(".git", "")
        cache_dir = Path("./cache") / project_name
        if cache_dir.exists():
            for py_file in cache_dir.rglob("*.py"):
                if any(skip in str(py_file) for skip in ['test', 'example', '__pycache__']):
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        files_data.append((str(py_file.relative_to(cache_dir)), f.read()))
                except:
                    pass
    else:
        source_path = Path(st.session_state.codebase_source)
        if source_path.exists():
            for py_file in source_path.rglob("*.py"):
                if any(skip in str(py_file) for skip in ['test', 'example', '__pycache__']):
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        files_data.append((str(py_file.relative_to(source_path)), f.read()))
                except:
                    pass
    
    if not files_data:
        st.error("❌ No Python files found")
        return
    
    st.info(f"📂 Found {len(files_data)} files")
    
    intel_tab1, intel_tab2, intel_tab3, intel_tab4 = st.tabs([
        "📊 Complexity & Maintainability",
        "🔍 Orphan Code Detection",
        "🔗 Code Similarity",
        "🎯 Pattern Mining"
    ])
    
    analyzer = CodeIntelligenceAnalyzer()
    
    with intel_tab1:
        st.markdown("### Code Complexity & Maintainability Analysis")
        st.info("Analyze cyclomatic complexity, maintainability index, and code metrics")
        
        if st.button("▶ Run Complexity Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing complexity..."):
                results = analyzer.analyze_codebase_from_files(files_data, ['complexity'])
                if 'complexity' in results and results['complexity']:
                    if 'error' in results['complexity']:
                        st.error(f"❌ {results['complexity']['error']}")
                    else:
                        st.session_state.complexity_results = results['complexity']
                        st.success("✅ Complete!")
        
        if st.session_state.get('complexity_results'):
            c = st.session_state.complexity_results
            st.markdown("### Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Functions", c['summary']['total_functions'])
            with col2: st.metric("Avg CC", c['summary']['avg_complexity'])
            with col3: st.metric("Complex", c['summary']['complex_functions'])
            with col4: st.metric("Modules", c['summary']['total_modules'])
            st.markdown("### Most Complex Functions")
            for func in sorted(c['function_metrics'], key=lambda x: x['cyclomatic_complexity'], reverse=True)[:15]:
                with st.expander(f"{func['function']} (CC: {func['cyclomatic_complexity']})"):
                    st.text(f"File: {func['file']}")
                    st.text(f"Lines: {func['line_start']}-{func['line_end']}")
    
    with intel_tab2:
        st.markdown("### Orphan Code Detection")
        st.info("Find unused functions, classes, and modules that can be safely removed")
        
        if st.button("▶ Detect Orphan Code", type="primary", use_container_width=True):
            with st.spinner("Detecting orphan code..."):
                results = analyzer.analyze_codebase_from_files(files_data, ['orphan'])
                if 'orphan' in results and results['orphan']:
                    if 'error' in results['orphan']:
                        st.error(f"❌ {results['orphan']['error']}")
                    else:
                        st.session_state.orphan_results = results['orphan']
                        st.success("✅ Complete!")
        
        if st.session_state.get('orphan_results'):
            o = st.session_state.orphan_results
            st.markdown("### Summary")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Definitions", o['summary']['total_definitions'])
            with col2: st.metric("Orphan Code", o['summary']['total_orphans'])
            with col3: st.metric("Orphan %", f"{o['summary']['orphan_percentage']}%")
            
            if o['orphan_functions']:
                st.markdown("### Orphan Functions")
                for func in o['orphan_functions'][:30]:
                    st.text(f"- {func['name']} in {func['file']}:{func['line']}")
            
            if o['orphan_classes']:
                st.markdown("### Orphan Classes")
                for cls in o['orphan_classes'][:20]:
                    st.text(f"- {cls['name']} in {cls['file']}:{cls['line']}")
    
    with intel_tab3:
        st.markdown("### Code Similarity Clustering")
        st.info("Identify similar functions using neural embeddings (CodeBERT)")
        
        if st.button("▶ Analyze Code Similarity", type="primary", use_container_width=True):
            with st.spinner("🔮 Analyzing code similarity with neural embeddings... (this may take a while)"):
                results = analyzer.analyze_codebase_from_files(files_data, ['similarity'])
                if 'similarity' in results and results['similarity']:
                    if 'error' in results['similarity']:
                        st.error(f"❌ {results['similarity']['error']}")
                        st.info(results['similarity'].get('message', ''))
                    else:
                        st.session_state.similarity_results = results['similarity']
                        st.success("✅ Complete!")
        
        if st.session_state.get('similarity_results'):
            s = st.session_state.similarity_results
            st.markdown("### Summary")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Functions", s['total_functions'])
            with col2: st.metric("Clusters", s['num_clusters'])
            with col3: st.metric("Similar Pairs", s['stats']['similar_pairs_count'])
            
            if s.get('similar_pairs'):
                st.markdown("### Similar Function Pairs")
                st.info(f"Found {len(s['similar_pairs'])} similar function pairs (similarity > 60%)")
                
                for pair in s['similar_pairs']:
                    with st.expander(f"{pair['func1'].split('::')[-1]} ↔ {pair['func2'].split('::')[-1]} (Similarity: {pair['similarity']})"):
                        st.markdown(f"**Files:** {pair['func1'].split('::')[0]} ↔ {pair['func2'].split('::')[0]}")
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.markdown("**Function 1:**")
                            st.code(pair['code1'], language='python')
                        with col_right:
                            st.markdown("**Function 2:**")
                            st.code(pair['code2'], language='python')
            
            if s.get('clusters'):
                st.markdown("### Code Clusters")
                st.info(f"Functions grouped into {len(s['clusters'])} clusters based on semantic similarity")
                
                for cluster_id, functions in list(s['clusters'].items())[:10]:
                    with st.expander(f"Cluster {cluster_id} ({len(functions)} functions)"):
                        for func in functions[:10]:
                            st.text(f"• {func}")
                        if len(functions) > 10:
                            st.caption(f"... and {len(functions) - 10} more")
    
    with intel_tab4:
        st.markdown("### Code Pattern Mining")
        st.info("Discover common patterns, anti-patterns, and architectural insights")
        
        if st.button("▶ Mine Code Patterns", type="primary", use_container_width=True):
            with st.spinner("Mining patterns and detecting anti-patterns..."):
                results = analyzer.analyze_codebase_from_files(files_data, ['patterns'])
                if 'patterns' in results and results['patterns']:
                    if 'error' in results['patterns']:
                        st.error(f"❌ {results['patterns']['error']}")
                    else:
                        st.session_state.pattern_results = results['patterns']
                        st.success("✅ Complete!")
        
        if st.session_state.get('pattern_results'):
            p = st.session_state.pattern_results
            
            # Overview Stats
            st.markdown("### 📊 Codebase Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Functions", p['total_functions'])
            with col2: st.metric("Total Classes", p.get('total_classes', 0))
            with col3: st.metric("Meaningful Patterns", len(p['common_patterns']))
            with col4: st.metric("Rare Patterns", p.get('rare_patterns', 0))
            
            # Class Statistics
            if p.get('class_stats'):
                st.markdown("### 📦 Class Statistics")
                col1, col2 = st.columns(2)
                with col1: st.metric("Avg Methods/Class", f"{p['class_stats']['avg_methods']:.2f}")
                with col2: st.metric("Classes with __init__", p['class_stats']['with_init'])
            
            # Top Patterns by Classification
            if p.get('common_patterns'):
                st.markdown("### 🎯 Top Architectural Patterns")
                pattern_types = {}
                for pattern in p['common_patterns']:
                    classification = pattern.get('classification', 'Standard Logic')
                    pattern_types[classification] = pattern_types.get(classification, 0) + pattern['count']
                
                cols = st.columns(min(3, len(pattern_types)))
                for i, (ptype, count) in enumerate(sorted(pattern_types.items(), key=lambda x: x[1], reverse=True)[:3]):
                    with cols[i % len(cols)]:
                        st.metric(ptype, count)
            
            # Common Patterns
            st.markdown("### 📋 Top Common Patterns")
            for i, pattern in enumerate(p['common_patterns'][:10], 1):
                pattern_str = ' → '.join(pattern['pattern'][:4]) if pattern['pattern'] else "Empty"
                classification = pattern.get('classification', 'Standard Logic')
                with st.expander(f"Pattern {i}: {pattern_str} ({pattern['count']} occurrences) [{classification}]"):
                    st.markdown(f"**Classification:** {classification}")
                    st.markdown(f"**Frequency:** {pattern['count']} times ({pattern['percentage']}%)")
                    st.markdown(f"**Full Pattern:** {' → '.join(pattern['pattern'])}")
            
            # Anti-Patterns
            if p.get('anti_patterns'):
                st.markdown("### ⚠️ Code Quality Concerns")
                severity_counts = {}
                for ap in p['anti_patterns']:
                    severity = ap.get('severity', 'MEDIUM')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("🔴 High Severity", severity_counts.get('HIGH', 0))
                with col2: st.metric("🟡 Medium Severity", severity_counts.get('MEDIUM', 0))
                with col3: st.metric("🟢 Low Severity", severity_counts.get('LOW', 0))
                
                st.markdown("#### Top Anti-Pattern Examples")
                for ap in p['anti_patterns'][:15]:
                    severity_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(ap['severity'], '⚪')
                    with st.expander(f"{severity_emoji} {ap['function']} - {ap['type']} ({ap['file']}:{ap['line']})"):
                        st.markdown(f"**Function:** `{ap['function']}`")
                        st.markdown(f"**File:** `{ap['file']}`")
                        st.markdown(f"**Line:** {ap['line']}")
                        st.markdown(f"**Issue:** {ap['details']}")
                        st.markdown(f"**Severity:** {ap['severity']}")

def render_security_tab():
    """Render the Code Security tab"""
    
    # Check if security analyzer is available
    if not SECURITY_AVAILABLE:
        st.error("🔒 Security tab is not available")
        st.markdown("### Installation Required")
        st.markdown(SECURITY_IMPORT_ERROR if SECURITY_IMPORT_ERROR else "Security analyzer module not found.")
        st.markdown("Please install the required dependencies:")
        st.code("pip install bandit[toml]", language="bash")
        return
    
    st.markdown("## 🔒 Code Security Analysis")
    st.markdown("Identify potential security vulnerabilities in your codebase using Bandit.")
    st.markdown("---")
    
    # Initialize analyzer
    analyzer = SecurityAnalyzer()
    
    # Check if Bandit is installed
    if not analyzer.check_bandit_available():
        st.warning("⚠️ Bandit is not installed")
        st.markdown(analyzer.install_bandit_instructions())
        return
    
    st.markdown("### Vulnerability Scan Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.selectbox(
            "Severity Level",
            options=["LOW", "MEDIUM", "HIGH"],
            index=1,  # Default to MEDIUM
            help="Show vulnerabilities at or above this severity level"
        )
    with col2:
        confidence_filter = st.selectbox(
            "Confidence Level",
            options=["LOW", "MEDIUM", "HIGH"],
            index=1,  # Default to MEDIUM
            help="Show vulnerabilities at or above this confidence level"
        )
    
    with col3:
        scan_categories = st.multiselect(
            "Scan Categories",
            options=[
                "B101",  # assert_used
                "B102",  # exec_used
                "B103",  # set_bad_file_permissions
                "B104",  # hardcoded_bind_all_interfaces
                "B105",  # hardcoded_password_string
                "B106",  # hardcoded_password_funcarg
                "B107",  # hardcoded_password_default
                "B108",  # hardcoded_tmp_directory
                "B110",  # try_except_pass
                "B112",  # try_except_continue
                "B201",  # flask_debug_true
                "B301",  # pickle
                "B302",  # marshal
                "B303",  # md5
                "B304",  # cipher_without_iv
                "B305",  # cipher_mode
                "B306",  # mktemp
                "B307",  # eval
                "B308",  # mark_safe
                "B309",  # httpsconnection_cert_verify
                "B310",  # urllib_urlopen
                "B311",  # random_generator
                "B312",  # telnet
                "B313",  # xml_bad_cElementTree
                "B314",  # xml_bad_ElementTree
                "B315",  # xml_bad_expatreader
                "B316",  # xml_bad_expatbuilder
                "B317",  # xml_bad_sax
                "B318",  # xml_bad_minidom
                "B319",  # xml_bad_pulldom
                "B320",  # xml_bad_etree
                "B321",  # ftplib
                "B322",  # hash
                "B323",  # unverified_context
                "B324",  # request_with_no_cert_validation
                "B401",  # import_telnetlib
                "B402",  # import_ftplib
                "B403",  # import_pickle
                "B404",  # import_subprocess
                "B405",  # import_xml_etree
                "B406",  # import_xml_sax
                "B407",  # import_xml_dom_minidom
                "B408",  # import_xml_dom_pulldom
                "B409",  # import_xml_expat
                "B501",  # request_with_no_verification
                "B502",  # flask_debug
                "B503",  # ssl_with_bad_version
                "B504",  # ssl_with_bad_defaults
                "B505",  # weak_cryptographic_key
                "B506",  # yaml_load
                "B507",  # ssh_no_host_key_verification
                "B508",  # snmp_insecure_version
                "B509",  # dnspython_insecure
                "B510",  # blacklist_calls
                "B601",  # shell_injection_subprocess
                "B602",  # shell_injection_win_registry
                "B603",  # sql_injection_risk
                "B604",  # shell_injection_tarfile
                "B605",  # start_process_with_a_shell
                "B606",  # start_process_with_no_shell
                "B607",  # start_process_with_partial_path
                "B608",  # hardcoded_sql_expressions
                "B610",  # django_extra_used
                "B611",  # django_rawsql_used
                "B701",  # jinja2_autoescape_false
            ],
            default=[],  # Empty means scan all categories
            help="Select specific vulnerability categories to scan (leave empty to scan all)"
        )
    
    st.markdown("---")
    
    # Get codebase source
    if not st.session_state.codebase_source:
        st.warning("⚠️ Please enter a codebase source first")
        return
    
    # Determine the directory to scan
    scan_directory = None
    if st.session_state.codebase_type == "github":
        # Use cached directory if available
        if st.session_state.codebase_source in st.session_state.get('cache_dirs', {}):
            scan_directory = st.session_state.cache_dirs[st.session_state.codebase_source]
        else:
            # Extract project name from GitHub URL
            project_name = st.session_state.codebase_source.split("/")[-1].replace(".git", "")
            cache_dir = Path("./cache") / project_name
            if cache_dir.exists():
                scan_directory = str(cache_dir)
    else:
        scan_directory = st.session_state.codebase_source
    
    if not scan_directory or not Path(scan_directory).exists():
        st.error(f"❌ Could not find codebase directory to scan: {scan_directory}")
        st.info("💡 Make sure you've generated a tutorial first for GitHub repositories, or verify the local path is correct.")
        return
    
    st.info(f"📂 Scanning directory: `{scan_directory}`")
    
    if st.button("🔍 Run Security Scan", type="primary", use_container_width=True):
        with st.spinner("Scanning codebase for security vulnerabilities..."):
            results, error = analyzer.scan_directory(
                directory=scan_directory,
                severity_filter=severity_filter,
                confidence_filter=confidence_filter,
                categories=scan_categories if scan_categories else None,
                exclude_patterns=DEFAULT_EXCLUDE_PATTERNS
            )
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                st.session_state.security_scan_results = results
                st.success("✅ Security scan completed!")
    
    # Display results if available
    if st.session_state.get('security_scan_results'):
        results = st.session_state.security_scan_results
        st.markdown("---")
        st.markdown("## 📊 Security Scan Results")
        
        summary = results['summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🔴 High Severity",
                value=summary['high_severity'],
                help="Critical security issues that need immediate attention"
            )
        
        with col2:
            st.metric(
                label="🟡 Medium Severity",
                value=summary['medium_severity'],
                help="Important security issues that should be addressed"
            )
        
        with col3:
            st.metric(
                label="🟢 Low Severity",
                value=summary['low_severity'],
                help="Minor security issues or recommendations"
            )
        
        with col4:
            st.metric(
                label="📄 Files with Issues",
                value=summary['files_with_issues'],
                help="Number of files containing security vulnerabilities"
            )
        
        st.markdown("---")
        
        # Display vulnerabilities
        if len(results['vulnerabilities']) == 0:
            st.success("🎉 **No security vulnerabilities found!** Your code appears to be secure.")
        else:
            st.markdown(f"### Found {summary['total_issues']} Security Issues")
            
            # Quick table of all issues with locations
            with st.expander("🧭 Issues by File and Line", expanded=False):
                import pandas as _pd
                _rows = [
                    {
                        'Severity': v['issue_severity'],
                        'File': v.get('relative_path') or v['file_path'],
                        'Line': v['line_number'],
                        'Rule': v['test_name'],
                        'Message': v['issue_text']
                    }
                    for v in results['vulnerabilities']
                ]
                if _rows:
                    _df = _pd.DataFrame(_rows)
                    st.dataframe(_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No issues to display.")
            
            # Filter tabs by severity
            severity_tabs = st.tabs(["🔴 High", "🟡 Medium", "🟢 Low"])
            
            for severity_idx, severity in enumerate(["HIGH", "MEDIUM", "LOW"]):
                with severity_tabs[severity_idx]:
                    vulns_by_severity = [v for v in results['vulnerabilities'] if v['issue_severity'] == severity]
                    
                    if len(vulns_by_severity) == 0:
                        st.info(f"No {severity.lower()} severity issues found.")
                    else:
                        st.write(f"Found {len(vulns_by_severity)} {severity.lower()} severity issue(s):")
                        
                        for idx, vuln in enumerate(vulns_by_severity, 1):
                            emoji = analyzer.get_severity_emoji(vuln['issue_severity'])
                            color = analyzer.get_severity_color(vuln['issue_severity'])
                            
                            with st.expander(f"{emoji} {vuln['test_name']}", expanded=False):
                                file_disp = vuln.get('relative_path') or vuln['file_path']
                                st.markdown(f"**File:** `{file_disp}:{vuln['line_number']}`")
                                st.markdown(f"**Confidence:** {analyzer.get_confidence_badge(vuln['issue_confidence'])}")
                                st.markdown(f"**Issue:** {vuln['issue_text']}")
                                
                                if vuln['code']:
                                    st.code(vuln['code'], language='python')
                                
                                if vuln['more_info']:
                                    st.markdown(f"**More Info:** [{vuln['more_info']}]({vuln['more_info']})")
        
        # Download options
        st.markdown("---")
        st.markdown("### 📥 Download Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_data = json.dumps(results, indent=2)
            st.download_button(
                label="📄 Download JSON Report",
                data=json_data,
                file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # HTML download
            html_report = analyzer.generate_html_report(results)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )

def render_chat_tab():
    """Render the Chat with Code tab"""
    st.markdown("## 💬 Chat with Code")
    st.markdown("Ask questions about your codebase using AI-powered analysis.")
    st.markdown("---")
    
    if not RAG_AVAILABLE:
        st.error("⚠️ RAG Chatbot dependencies not installed")
        st.markdown("""
        ### Installation Required
        
        ```bash
        pip install chromadb sentence-transformers
        ```
        
        After installation, **restart the Streamlit app**.
        """)
        return
    
    # Index the codebase librarians not already indexed
    if not st.session_state.rag_indexed:
        st.info("ℹ️ Codebase needs to be indexed before chatting")
        
        # Check if tutorial has cached files
        cache_dir = None
        if st.session_state.codebase_type == 'github' and st.session_state.tutorial_complete:
            # Look for cached files from tutorial generation
            cache_base = Path("./cache")
            project_name = Path(st.session_state.codebase_source).name
            cache_dir = cache_base / project_name
            if cache_dir.exists():
                st.info(f"📂 Found cached files from tutorial generation at: {cache_dir}")
        
        if st.button("🔄 Index Codebase for Chat", type="primary", use_container_width=True):
            with st.spinner("Indexing codebase... This may take 1-3 minutes..."):
                try:
                    if not st.session_state.rag_chatbot:
                        st.session_state.rag_chatbot = CodebaseRAG()
                        st.session_state.rag_chatbot.create_collection("codebase")
                    
                    # Use cached directory if available, otherwise use original source
                    index_source = str(cache_dir) if cache_dir and cache_dir.exists() else st.session_state.codebase_source
                    stats = st.session_state.rag_chatbot.index_codebase(index_source)
                    
                    st.session_state.rag_indexed = True
                    st.session_state.rag_stats = stats
                    
                    st.success(f"✅ Indexed {stats['total_files']} files ({stats['total_chunks']} chunks)")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error indexing codebase: {str(e)}")
        
        st.markdown("""
        ### 🎯 Example Questions:
        - "How does authentication work in this codebase?"
        - "Where are database queries defined?"
        - "Explain the payment processing flow"
        - "Find all API endpoints"
        - "Are there any security vulnerabilities?"
        - "What design patterns are used?"
        """)
        return
    
    # Show indexed stats
    with st.expander("ℹ️ Indexed Codebase Info"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files Indexed", st.session_state.rag_stats.get('total_files', 0))
        with col2:
            st.metric("Code Chunks", st.session_state.rag_stats.get('total_chunks', 0))
    
    # Quick action buttons
    if not st.session_state.chat_history:
        
        st.markdown("---")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant"):
                st.markdown(message['content'])
                
                if 'sources' in message:
                    with st.expander("📄 Sources"):
                        for source in set(message['sources']):
                            st.markdown(f"- `{source}`")
    
    # Chat input
    user_query = st.chat_input("Ask me anything about the codebase...")
    
    if user_query:
        # Add user message to history first
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })
        
        # Show the user message immediately
        with st.chat_message("user"):
            st.markdown(user_query)
        
        # Generate and show assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing code and generating response..."):
                try:
                    # Use adaptive retrieval (defaults to 20 results, filtered by similarity)
                    result = st.session_state.rag_chatbot.answer_query(user_query, n_results=20)
                    
                    # Display the answer
                    st.markdown(result['answer'])
                    
                    # Show sources if available
                    if result.get('sources'):
                        with st.expander("📄 Sources"):
                            for source in set(result['sources']):
                                st.markdown(f"- `{source}`")
                    
                    # Add assistant response to history after displaying
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': result['answer'],
                        'sources': result.get('sources', [])
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    # Add error to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': error_msg
                    })
        
        # Don't rerun - let user see the conversation naturally
        st.stop()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

def render_codebase_input():
    """Render the initial codebase input page"""
    st.markdown('<h1 class="main-header">◈ CodeSensei</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Code Analysis & Tutorial Generation Platform")
    
    st.markdown("---")
    
    st.markdown("""
    Welcome to CodeSensei! This platform provides comprehensive code analysis and documentation tools.
    
    **Get started by loading your codebase:**
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📂 Select Codebase Source")
        
        source_type = st.radio(
            "Choose source type:",
            ["GitHub Repository", "Local Directory"],
            horizontal=True,
            key="source_type_selector"
        )
        
        if source_type == "GitHub Repository":
            codebase_input = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/username/repository",
                help="Enter the full GitHub repository URL"
            )
            input_type = "github"
        else:
            codebase_input = st.text_input(
                "Local Directory Path",
                placeholder="/path/to/your/codebase",
                help="Enter the absolute path to your local codebase"
            )
            input_type = "local"
        
        if st.button("▶ Load Codebase", type="primary", use_container_width=True):
            if not codebase_input:
                st.error("⚠️ Please provide a codebase source")
            else:
                # Validate input
                if input_type == "local":
                    if not Path(codebase_input).exists():
                        st.error(f"❌ Path does not exist: {codebase_input}")
                        return
                    if not Path(codebase_input).is_dir():
                        st.error(f"❌ Path is not a directory: {codebase_input}")
                        return
                
                # Save to session state
                st.session_state.codebase_source = codebase_input
                st.session_state.codebase_type = input_type
                st.session_state.codebase_loaded = True
                st.success(f"✅ Codebase loaded: {codebase_input}")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Features")
        st.markdown("""
        Once loaded, you'll have access to:
        
        - **Tutorial Generation**  
          Generate comprehensive tutorials
        
        - **Code Intelligence**  
          Complexity, orphan detection, clustering, patterns
        
        - **Code Security**  
          Vulnerability detection
        
        - **Chat with Code**  
          Interactive Q&A about your codebase
        """)
    
    # Show platform features
    st.markdown("---")
    st.markdown("## 🚀 Platform Capabilities")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Tutorial Generation",
        "🧠 Code Intelligence", 
        "🔒 Code Security",
        "💬 Chat with Code"
    ])
    
    with tab1:
        st.markdown("""
        ### Tutorial Generation
        Automatically generate comprehensive, structured tutorials from any codebase.
        
        **Features:**
        - Multi-chapter tutorials with clear structure
        - Code examples and explanations
        - Mermaid diagrams for architecture visualization
        - Download as ZIP or PDF
        """)
    
    with tab2:
        st.markdown("""
        ### Code Intelligence
        Deep analysis of your codebase structure and quality.
        
        **Analysis Types:**
        - **Code Complexity & Maintainability**: Cyclomatic complexity, maintainability index
        - **Orphan Code Detection**: Find unused functions, classes, and modules
        - **Code Similarity Clustering**: Identify duplicate or similar code patterns
        - **Code Pattern Mining**: Discover design patterns and anti-patterns
        """)
    
    with tab3:
        st.markdown("""
        ### Code Security
        Identify potential security vulnerabilities in your code.
        
        **Detects:**
        - SQL injection vulnerabilities
        - XSS (Cross-Site Scripting) risks
        - Insecure authentication patterns
        - Hardcoded secrets and credentials
        - Unsafe file operations
        """)
    
    with tab4:
        st.markdown("""
        ### Chat with Code
        Ask questions about your codebase using AI-powered RAG (Retrieval-Augmented Generation).
        
        **Examples:**
        - "How does authentication work?"
        - "Where are database queries defined?"
        - "Explain the payment processing flow"
        - "Find all API endpoints"
        """)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ◆ CodeSensei")
        st.markdown("AI Code Analysis Platform")
        st.markdown("---")
        
        # Show loaded codebase info
        if st.session_state.codebase_loaded:
            st.success("✅ Codebase Loaded")
            st.caption(f"**Source:** {st.session_state.codebase_type.title()}")
            st.caption(f"**Path:** {st.session_state.codebase_source}")
            
            if st.button("🔄 Change Codebase", use_container_width=True):
                # Clear all state
                st.session_state.codebase_loaded = False
                st.session_state.codebase_source = None
                st.session_state.codebase_type = None
                st.session_state.tutorial_complete = False
                st.session_state.rag_indexed = False
                st.session_state.chat_history = []
                st.rerun()
            
            st.markdown("---")
        
        # Settings Panel
        with st.expander("⚙ Settings", expanded=False):
            st.markdown("**API Configuration**")
            
            # Current API Status
            if os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_PROJECT_ID"):
                st.success("✓ Gemini API Configured")
            elif os.getenv("LLM_PROVIDER"):
                st.success(f"✓ {os.getenv('LLM_PROVIDER')} Configured")
            else:
                st.error("✗ No API Key Found")
                st.caption("Set GEMINI_API_KEY in .env")
            
            # GitHub Token Status
            st.markdown("**GitHub Token**")
            if os.getenv("GITHUB_TOKEN"):
                st.success("✓ Token Loaded")
            else:
                st.info("ⓘ No GitHub Token")
                st.caption("Set GITHUB_TOKEN for private repos")
        
        # Developer Team
        st.markdown("---")
        st.markdown("**Developer Team**")
        st.caption("Ananth Prabhu T")
        st.caption("Shreedhar A Sherlekar")
        st.caption("Chandan K Vasista")
    
    # Main content
    if not st.session_state.codebase_loaded:
        render_codebase_input()
    else:
        # Show tabs for different features
        st.markdown(f'<h1 class="main-header">◈ CodeSensei</h1>', unsafe_allow_html=True)
        st.caption(f"Analyzing: {st.session_state.codebase_source}")
        st.markdown("---")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📚 Tutorial Generation",
            "🧠 Code Intelligence",
            "🔒 Code Security",
            "💬 Chat with Code"
        ])
        
        with tab1:
            render_tutorial_tab()
        
        with tab2:
            render_intelligence_tab()
        
        with tab3:
            render_security_tab()
        
        with tab4:
            render_chat_tab()

if __name__ == "__main__":
    main()

