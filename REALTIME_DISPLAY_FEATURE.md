# Real-time Tutorial File Display & Mermaid Diagram Rendering

## Overview
The Streamlit app now:
1. **Displays generated tutorial files in real-time** as they are being created during the tutorial generation process
2. **Renders Mermaid diagrams** embedded in markdown files as interactive, visual diagrams

## How It Works

### Architecture

1. **Background Thread for Generation**
   - Tutorial generation runs in a separate background thread
   - This prevents blocking the Streamlit UI

2. **File Monitoring Thread**
   - A dedicated monitoring thread watches the output directory
   - Detects new `.md` files as they are created
   - Reads file content and metadata

3. **Thread-Safe Communication**
   - Uses Python `queue.Queue` for thread-safe messaging
   - Background threads send messages to the main UI thread
   - Message types include: logs, files, errors, progress steps

4. **Auto-Refresh UI**
   - UI refreshes every 2 seconds while generation is running
   - Processes queued messages from background threads
   - Updates display with new files and progress logs

### Key Components

#### `monitor_output_directory_thread(output_dir, stop_event, msg_queue)`
- Monitors the output directory for new `.md` files
- Sends file information through the message queue
- Runs continuously until `stop_event` is set

#### `run_tutorial_generation_thread(config, msg_queue, stop_event)`
- Main generation logic running in background
- Starts the file monitoring thread
- Sends progress updates through the message queue
- Handles errors and completion signals

#### `process_message_queue()`
- Called from main UI thread
- Processes messages from background threads
- Updates session state with new files, logs, and status

### User Interface

The generation page now has two columns:

**Left Column - Progress Log**
- Shows timestamped log messages
- Color-coded by level (info, success, error)
- Displays last 20 entries

**Right Column - Generated Files**
- Real-time list of generated files
- Shows file name, timestamp, and size
- Expandable preview (first 800 characters)
- Updates automatically as files are created

## Benefits

1. **Transparency** - Users can see files being generated in real-time
2. **Confidence** - Visual feedback that the process is working
3. **Debugging** - Easier to spot issues during generation
4. **User Experience** - More engaging than a simple spinner

## Technical Notes

- Uses Python's `threading` module for concurrency
- `queue.Queue` ensures thread-safe communication
- Streamlit's `st.rerun()` provides UI refresh mechanism
- File monitoring checks directory every 1 second
- UI refreshes every 2 seconds to balance responsiveness and performance

## Mermaid Diagram Rendering

### How It Works

The app automatically detects and renders mermaid diagrams in markdown content:

1. **Detection** - Scans markdown for ` ```mermaid ` code blocks
2. **Parsing** - Extracts mermaid code and splits markdown content
3. **Rendering** - Uses Mermaid.js library via HTML components
4. **Display** - Shows interactive, zoomable diagrams inline with content

### Supported Diagram Types

Mermaid supports various diagram types that work in the app:
- **Flowcharts** - Process flows and decision trees
- **Sequence Diagrams** - Interaction between components
- **Class Diagrams** - Object-oriented structures
- **State Diagrams** - State machines and transitions
- **Entity Relationship** - Database schemas
- **Gantt Charts** - Project timelines
- And more!

### Example

When the LLM generates this in a markdown file:

\```mermaid
flowchart TD
    A[User Request] --> B{Route Handler}
    B --> C[Process Data]
    C --> D[Return Response]
\```

The app renders it as an interactive diagram, not just code.

### Technical Implementation

- Uses **Mermaid.js v10** from CDN
- Renders in isolated HTML iframe for security
- Unique IDs prevent conflicts with multiple diagrams
- Responsive sizing with scrolling support
- Styled containers with proper spacing

## Usage

Simply start a tutorial generation from the Configure page. The generation page will automatically:
1. Start monitoring the output directory
2. Display files as they are created
3. Show progress logs
4. **Render mermaid diagrams** as interactive visuals
5. Update in real-time until completion

In the Results page, all markdown content with mermaid diagrams will be beautifully rendered with:
- Full syntax highlighting for code
- Interactive, zoomable diagrams
- Proper formatting and spacing
- Professional appearance

No additional configuration needed!

