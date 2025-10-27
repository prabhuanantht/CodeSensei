"""
Utility functions and helpers for Streamlit-PocketFlow integration
"""
import streamlit as st
import sys
import io
from contextlib import contextmanager
from typing import Callable, Any
import traceback


class StreamlitProgressLogger:
    """
    A logger that captures print statements and node execution
    and forwards them to Streamlit session state
    """
    
    def __init__(self):
        self.logs = []
    
    def log(self, message: str, level: str = "info"):
        """Add a log entry"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "message": message,
            "level": level
        }
        self.logs.append(entry)
        
        # Also add to session state if available
        if hasattr(st, 'session_state') and 'progress_log' in st.session_state:
            st.session_state.progress_log.append(entry)
    
    def get_logs(self):
        """Get all log entries"""
        return self.logs
    
    def clear(self):
        """Clear all logs"""
        self.logs = []


@contextmanager
def capture_output():
    """
    Context manager to capture stdout/stderr
    Usage:
        with capture_output() as output:
            print("Hello")
        print(output.getvalue())
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def monkey_patch_node_for_logging(node, step_name: str, logger: StreamlitProgressLogger):
    """
    Monkey patch a PocketFlow node to add logging
    
    Args:
        node: The node to patch
        step_name: Name of the step for logging
        logger: Logger instance
    """
    original_exec = node.exec
    
    def logged_exec(prep_res):
        # Update current step in session state
        if hasattr(st, 'session_state'):
            st.session_state.current_step = step_name
        
        logger.log(f"Starting: {step_name}", "info")
        
        try:
            result = original_exec(prep_res)
            logger.log(f"✅ Completed: {step_name}", "success")
            return result
        except Exception as e:
            logger.log(f"❌ Error in {step_name}: {str(e)}", "error")
            raise
    
    node.exec = logged_exec
    return node


def monkey_patch_batch_node_for_logging(node, step_name: str, logger: StreamlitProgressLogger):
    """
    Monkey patch a PocketFlow BatchNode to add logging with item tracking
    
    Args:
        node: The batch node to patch
        step_name: Name of the step for logging
        logger: Logger instance
    """
    original_exec = node.exec
    
    # Track progress across exec calls
    node._batch_progress = {"current": 0, "total": 0}
    
    def logged_exec(item):
        # Update progress
        node._batch_progress["current"] += 1
        current = node._batch_progress["current"]
        total = node._batch_progress["total"]
        
        # Update current step in session state
        if hasattr(st, 'session_state'):
            st.session_state.current_step = f"{step_name} ({current}/{total})"
        
        logger.log(f"Processing {step_name} - Item {current}/{total}", "info")
        
        try:
            result = original_exec(item)
            return result
        except Exception as e:
            logger.log(f"❌ Error in {step_name} item {current}: {str(e)}", "error")
            raise
    
    # Also patch prep to get total count
    original_prep = node.prep
    
    def logged_prep(shared):
        logger.log(f"Starting: {step_name}", "info")
        if hasattr(st, 'session_state'):
            st.session_state.current_step = step_name
        
        try:
            result = original_prep(shared)
            # For batch nodes, prep returns an iterable
            if hasattr(result, '__len__'):
                node._batch_progress["total"] = len(result)
                logger.log(f"{step_name}: Processing {len(result)} items", "info")
            return result
        except Exception as e:
            logger.log(f"❌ Error in {step_name} prep: {str(e)}", "error")
            raise
    
    node.exec = logged_exec
    node.prep = logged_prep
    return node


def create_instrumented_flow(logger: StreamlitProgressLogger):
    """
    Create a tutorial flow with instrumentation for progress tracking
    
    Args:
        logger: Logger instance for progress updates
    
    Returns:
        Instrumented flow ready to run
    """
    from flow import create_tutorial_flow
    from nodes import BatchNode
    
    # Create the flow
    flow = create_tutorial_flow()
    
    # Define step names
    steps = [
        (flow.start, "Fetch Repository", False),
        (flow.start.next_nodes[0], "Identify Abstractions", False),
        (flow.start.next_nodes[0].next_nodes[0], "Analyze Relationships", False),
        (flow.start.next_nodes[0].next_nodes[0].next_nodes[0], "Order Chapters", False),
        (flow.start.next_nodes[0].next_nodes[0].next_nodes[0].next_nodes[0], "Write Chapters", True),
        (flow.start.next_nodes[0].next_nodes[0].next_nodes[0].next_nodes[0].next_nodes[0], "Combine Tutorial", False),
    ]
    
    # Patch each node
    for node, step_name, is_batch in steps:
        if is_batch or isinstance(node, BatchNode):
            monkey_patch_batch_node_for_logging(node, step_name, logger)
        else:
            monkey_patch_node_for_logging(node, step_name, logger)
    
    return flow


def safe_run_flow(flow, shared_dict: dict, logger: StreamlitProgressLogger):
    """
    Safely run a flow with error handling and logging
    
    Args:
        flow: The flow to run
        shared_dict: Shared dictionary for the flow
        logger: Logger instance
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        logger.log("🚀 Starting tutorial generation flow", "info")
        
        # Run the flow
        flow.run(shared_dict)
        
        logger.log("🎉 Tutorial generation completed successfully!", "success")
        return True, None
        
    except Exception as e:
        error_msg = f"Error during generation: {str(e)}"
        logger.log(f"❌ {error_msg}", "error")
        
        # Log the traceback for debugging
        tb = traceback.format_exc()
        logger.log(f"Traceback:\n{tb}", "error")
        
        return False, error_msg


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_config(config: dict) -> tuple[bool, str]:
    """
    Validate configuration before running
    
    Args:
        config: Configuration dictionary
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Check source
    if not config.get('repo_url') and not config.get('local_dir'):
        return False, "Please provide either a GitHub repository URL or a local directory path"
    
    # Check if both are provided
    if config.get('repo_url') and config.get('local_dir'):
        return False, "Please provide only one source: either GitHub URL or local directory"
    
    # Validate URL format
    if config.get('repo_url'):
        url = config['repo_url']
        if not url.startswith('http'):
            return False, "GitHub URL must start with http:// or https://"
        if 'github.com' not in url:
            return False, "Please provide a valid GitHub repository URL"
    
    # Validate local directory
    if config.get('local_dir'):
        import os
        path = config['local_dir']
        if not os.path.exists(path):
            return False, f"Directory does not exist: {path}"
        if not os.path.isdir(path):
            return False, f"Path is not a directory: {path}"
    
    # Validate abstractions count
    max_abs = config.get('max_abstractions', 10)
    if not isinstance(max_abs, int) or max_abs < 1 or max_abs > 50:
        return False, "Max abstractions must be between 1 and 50"
    
    # Validate language
    if not config.get('language'):
        return False, "Please select a language"
    
    return True, ""


def get_tutorial_stats(output_dir: str) -> dict:
    """
    Get statistics about generated tutorial
    
    Args:
        output_dir: Path to output directory
    
    Returns:
        Dictionary with stats
    """
    from pathlib import Path
    
    if not output_dir or not Path(output_dir).exists():
        return {}
    
    path = Path(output_dir)
    md_files = list(path.glob("*.md"))
    chapter_files = [f for f in md_files if f.name != "index.md"]
    
    total_size = sum(f.stat().st_size for f in md_files)
    
    # Count diagrams
    diagram_count = 0
    code_block_count = 0
    
    for file in md_files:
        content = file.read_text(encoding='utf-8')
        diagram_count += content.count('```mermaid')
        # Count code blocks (excluding mermaid)
        code_blocks = content.count('```')
        mermaid_blocks = content.count('```mermaid') * 2  # Opening and closing
        code_block_count += (code_blocks - mermaid_blocks) // 2
    
    return {
        "total_files": len(md_files),
        "chapters": len(chapter_files),
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "diagrams": diagram_count,
        "code_blocks": code_block_count,
        "project_name": path.name
    }


def create_download_zip(output_dir: str) -> io.BytesIO:
    """
    Create a ZIP file of the tutorial
    
    Args:
        output_dir: Path to output directory
    
    Returns:
        BytesIO buffer containing the ZIP file
    """
    import zipfile
    from pathlib import Path
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        path = Path(output_dir)
        for file in path.glob("*.md"):
            zip_file.write(file, file.name)
    
    zip_buffer.seek(0)
    return zip_buffer


# Streamlit component helpers

def render_log_entry(entry: dict):
    """
    Render a single log entry with appropriate styling
    
    Args:
        entry: Log entry dictionary with timestamp, message, level
    """
    timestamp = entry['timestamp']
    message = entry['message']
    level = entry['level']
    
    if level == "error":
        st.error(f"[{timestamp}] {message}")
    elif level == "success":
        st.success(f"[{timestamp}] {message}")
    elif level == "warning":
        st.warning(f"[{timestamp}] {message}")
    else:
        st.info(f"[{timestamp}] {message}")


def render_progress_steps(steps: list, current_step: str):
    """
    Render progress steps as a horizontal progress indicator
    
    Args:
        steps: List of step names
        current_step: Name of the current step
    """
    current_index = -1
    
    # Find current step index
    for i, step in enumerate(steps):
        if step == current_step or current_step.startswith(step):
            current_index = i
            break
    
    # Create columns for each step
    cols = st.columns(len(steps))
    
    for i, step in enumerate(steps):
        with cols[i]:
            if i < current_index:
                st.markdown(f"✅ **{step}**")
            elif i == current_index:
                st.markdown(f"🔄 **{step}**")
            else:
                st.markdown(f"⏳ {step}")
    
    # Progress bar
    progress = (current_index + 1) / len(steps) if current_index >= 0 else 0
    st.progress(progress)
    
    return progress


def render_stats_cards(stats: dict):
    """
    Render statistics as cards
    
    Args:
        stats: Statistics dictionary
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Chapters", stats.get("chapters", 0))
    
    with col2:
        st.metric("💾 Size", stats.get("total_size_formatted", "0 B"))
    
    with col3:
        st.metric("📊 Diagrams", stats.get("diagrams", 0))
    
    with col4:
        st.metric("💻 Code Blocks", stats.get("code_blocks", 0))

