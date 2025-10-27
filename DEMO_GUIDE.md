# 🎬 CodeSensei Demo Guide

A visual walkthrough of the Streamlit application

## 🏠 Page 1: Home Page

### What You See
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar                    Main Content                    │
│  ┌───────────┐             ┌──────────────────────────┐    │
│  │ CodeSensei│             │  🎓 CodeSensei           │    │
│  │ AI-Powered│             │  Transform Any Codebase  │    │
│  │ Tutorial  │             │  into Tutorials with AI  │    │
│  │ Generator │             └──────────────────────────┘    │
│  ├───────────┤                                             │
│  │ 🏠 Home   │◄── Active   ┌──────────────────────────┐    │
│  │ ⚙️  Config│             │  🚀 What is CodeSensei?  │    │
│  │           │             │  [Description]           │    │
│  ├───────────┤             │                          │    │
│  │ 🔑 API    │             │  ✨ Key Features         │    │
│  │ Status    │             │  • AI-Powered Analysis   │    │
│  │ ✅ Gemini │             │  • Structured Tutorials  │    │
│  │ Configured│             │  • Multi-Language        │    │
│  ├───────────┤             │  • Visual Diagrams       │    │
│  │ 📚 Links  │             │                          │    │
│  │ GitHub    │             │  🎯 How It Works         │    │
│  │ Docs      │             │  1. Fetch                │    │
│  └───────────┘             │  2. Analyze              │    │
│                            │  3. Structure             │    │
│                            │  4. Generate              │    │
│                            │  5. Export                │    │
│                            │                          │    │
│                            │  [🚀 Get Started]        │    │
│                            └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements
- **Hero Section**: Eye-catching title with gradient
- **Feature Cards**: Visual feature highlights
- **How It Works**: Step-by-step process
- **Example Showcase**: Real tutorial examples
- **CTA Button**: Prominent "Get Started" button
- **Sidebar**: Always visible navigation

## ⚙️ Page 2: Configuration Page

### What You See
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar                    Main Content                    │
│  ┌───────────┐             ┌──────────────────────────┐    │
│  │ Navigation│             │  ⚙️ Configure Tutorial   │    │
│  │ 🏠 Home   │             └──────────────────────────┘    │
│  │ ⚙️  Config│◄── Active                                   │
│  ├───────────┤             📂 Source Selection              │
│  │ API Status│             ○ GitHub Repository              │
│  │ ✅ Ready  │             ● Local Directory                │
│  └───────────┘             ┌──────────────────────────┐    │
│                            │ Directory Path:          │    │
│                            │ /path/to/codebase  [...]│    │
│                            └──────────────────────────┘    │
│                                                             │
│                            🎯 Project Settings              │
│                            ┌───────────┬──────────────┐    │
│                            │ Project   │ Language     │    │
│                            │ Name:     │ ▼ English    │    │
│                            │ [Optional]│              │    │
│                            ├───────────┼──────────────┤    │
│                            │ Max       │ Enable LLM   │    │
│                            │ Abstract: │ Caching      │    │
│                            │ [====●==] │ [x] Enabled  │    │
│                            │     10    │              │    │
│                            └───────────┴──────────────┘    │
│                                                             │
│                            📝 File Patterns                 │
│                            [▼ Advanced Options...]          │
│                                                             │
│                            💾 Output Settings               │
│                            Output Directory: output         │
│                                                             │
│                            [⬅️ Back]  [ ] [🚀 Generate]    │
└─────────────────────────────────────────────────────────────┘
```

### Interactive Elements
- **Radio Buttons**: Toggle GitHub/Local
- **Text Inputs**: URL, path, project name
- **Dropdown**: Language selection (8+ options)
- **Slider**: Max abstractions (5-20)
- **Checkbox**: Enable caching
- **Expander**: Advanced file patterns
- **Text Areas**: Include/exclude patterns
- **Buttons**: Back, Generate Tutorial

### Validation
```
When URL/Path is empty:
  🚀 Generate button → Disabled (grayed out)

When URL is invalid:
  ⚠️ "Please provide a valid GitHub URL"

When directory doesn't exist:
  ⚠️ "Directory does not exist: /path"

When API key missing:
  ⚠️ "Please configure your LLM API key"
```

## ⚡ Page 3: Generation Page

### What You See (During Generation)
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar                    Main Content                    │
│  ┌───────────┐             ┌──────────────────────────┐    │
│  │ Navigation│             │  ⚡ Generating Tutorial   │    │
│  │ 🏠 Home   │             └──────────────────────────┘    │
│  │ ⚙️  Config│                                              │
│  │ 📖 Results│ New!        Progress Steps                   │
│  ├───────────┤             ┌──────────────────────────┐    │
│  │ API Status│             │ ✅📥 → 🔄🔍 → ⏳🔗      │    │
│  │ ✅ Active │             │ Fetch   Identify  Analyze │    │
│  └───────────┘             │                          │    │
│                            │ ⏳📊 → ⏳✍️ → ⏳📚      │    │
│                            │ Order   Write   Combine  │    │
│                            └──────────────────────────┘    │
│                                                             │
│                            [████████░░░░░░] 60%            │
│                                                             │
│                            📋 Progress Log                  │
│                            ┌──────────────────────────┐    │
│                            │ [10:45:32] 🚀 Starting...│    │
│                            │ [10:45:35] ✅ Fetched 50 │    │
│                            │            files          │    │
│                            │ [10:46:12] 🔍 Identifying│    │
│                            │            abstractions.. │    │
│                            │ [10:48:05] ✅ Identified │    │
│                            │            10 concepts   │    │
│                            │ [10:48:10] 🔗 Analyzing  │    │
│                            │            relationships.│    │
│                            │ [10:49:30] 🔄 Writing    │    │
│                            │            chapters (3/10)│    │
│                            │ ...                      │    │
│                            └──────────────────────────┘    │
│                                                             │
│                            Status: 🔄 Generating...         │
│                            Auto-refreshing...               │
└─────────────────────────────────────────────────────────────┘
```

### Status Indicators
```
✅ Completed Step - Green checkmark
🔄 Current Step  - Blue spinner
⏳ Pending Step  - Gray hourglass

Progress Bar:
[████████░░░░░░] 60%  ← Visual completion
```

### Live Updates
- Updates every 2 seconds automatically
- Latest 20 log entries shown
- Color-coded messages (info/success/error)
- Timestamps for each entry
- Batch progress shown (e.g., "Writing 3/10")

### On Completion
```
┌──────────────────────────────────────┐
│  ✅ Tutorial generation complete!    │
│                                      │
│  [📖 View Results] ← Clickable      │
└──────────────────────────────────────┘
```

## 📖 Page 4: Results Page

### What You See
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar                    Main Content                    │
│  ┌───────────┐             ┌──────────────────────────┐    │
│  │ Navigation│             │  📖 Tutorial Results      │    │
│  │ 🏠 Home   │             └──────────────────────────┘    │
│  │ ⚙️  Config│                                              │
│  │ 📖 Results│◄── Active   📊 Tutorial Statistics           │
│  ├───────────┤             ┌────┬────┬────┬────────┐       │
│  │ API Status│             │ 📝 │ 💾 │ 📊 │ 💻     │       │
│  │ ✅ Ready  │             │ 10 │45KB│ 8  │ 32     │       │
│  └───────────┘             │Chap│Size│Diag│Blocks  │       │
│                            └────┴────┴────┴────────┘       │
│                                                             │
│                            👁️ Tutorial Preview             │
│                            ┌──────────────────────────┐    │
│                            │ ▼ 📄 Index Page         │    │
│                            │ ┌────────────────────┐  │    │
│                            │ │ # Tutorial: Flask  │  │    │
│                            │ │ Flask is a web...  │  │    │
│                            │ │ ```mermaid         │  │    │
│                            │ │ flowchart TD...    │  │    │
│                            │ │ ```                │  │    │
│                            │ │ ## Chapters        │  │    │
│                            │ │ 1. [Core](01.md)   │  │    │
│                            │ │ 2. [Router](02.md) │  │    │
│                            │ └────────────────────┘  │    │
│                            └──────────────────────────┘    │
│                                                             │
│                            📚 Chapters                      │
│                            Select: ▼ 01_core_concept.md    │
│                            ┌──────────────────────────┐    │
│                            │ ▼ 📖 01_core_concept.md │    │
│                            │ [Chapter content...]     │    │
│                            └──────────────────────────┘    │
│                                                             │
│                            💾 Download Tutorial             │
│                            [📦 Download ZIP] [🔄 New]      │
└─────────────────────────────────────────────────────────────┘
```

### Statistics Cards
```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│   📝    │  │   💾    │  │   📊    │  │   💻    │
│   10    │  │  45KB   │  │    8    │  │   32    │
│Chapters │  │  Size   │  │Diagrams │  │  Code   │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Preview Section
- Expandable index page view
- Rendered Markdown (including Mermaid)
- Chapter selector dropdown
- Expandable chapter views
- Full content preview

### Download Options
- ZIP file contains all .md files
- One-click download
- Named: `ProjectName_tutorial.zip`
- Ready to extract and use

## 🎨 UI Elements Showcase

### Color Coding

**Success** (Green)
```
✅ Tutorial generation complete!
✅ Fetched 50 files
```

**Info** (Blue)
```
ℹ️ Starting tutorial generation...
ℹ️ Processing chapter 3/10
```

**Warning** (Yellow)
```
⚠️ No GitHub token provided
⚠️ Rate limit may apply
```

**Error** (Red)
```
❌ Error: Invalid repository URL
❌ Failed to connect to API
```

### Progress Indicators

**Step Progress**
```
✅ Completed  → Green with checkmark
🔄 Running    → Blue with spinner
⏳ Pending    → Gray with hourglass
```

**Overall Progress**
```
[████████░░░░░░] 60%
[██████████████] 100%
```

### Cards and Containers

**Metric Card**
```
┌─────────────┐
│     📝      │
│     10      │
│  Chapters   │
└─────────────┘
```

**Status Box**
```
┌───────────────────────────────┐
│ 🔄 Generation in progress...  │
│ Current: Writing Chapters     │
└───────────────────────────────┘
```

### Buttons

**Primary Action**
```
[🚀 Generate Tutorial]  ← Large, blue
```

**Secondary Action**
```
[⬅️ Back]              ← Regular, gray
```

**Download Action**
```
[📦 Download ZIP]       ← Green
```

## 🔄 User Flow Example

### Complete Workflow
```
1. Home Page
   ↓ Click "Get Started"
   
2. Configuration Page
   ↓ Enter: https://github.com/pallets/flask
   ↓ Select: Language = English
   ↓ Set: Max Abstractions = 10
   ↓ Click "Generate Tutorial"
   
3. Generation Page
   ↓ Watch progress: 0% → 100%
   ↓ See logs: Fetched → Identified → Analyzed → Ordered → Written → Combined
   ↓ Wait: ~10 minutes
   ↓ See: "✅ Complete!"
   ↓ Click "View Results"
   
4. Results Page
   ↓ See: 10 Chapters, 45KB, 8 Diagrams
   ↓ Preview index and chapters
   ↓ Click "Download ZIP"
   ↓ Extract and use!
   
5. Generate Another?
   ↓ Click "Generate Another Tutorial"
   ↓ Back to Configuration Page
```

## 📱 Responsive Design

### Desktop (Wide Screen)
```
┌─Sidebar(20%)─┬─────────Main Content(80%)────────┐
│              │                                   │
│  Navigation  │  Large content area               │
│  Status      │  Wide forms                       │
│  Links       │  Multiple columns                 │
│              │  Expanded views                   │
└──────────────┴───────────────────────────────────┘
```

### Tablet (Medium Screen)
```
┌─Side(25%)─┬──────Main Content(75%)──────┐
│           │                              │
│ Nav       │  Adjusted layout             │
│ Status    │  Stacked forms               │
│           │  2-column stats              │
└───────────┴──────────────────────────────┘
```

## 🎯 Key Features in Action

### Real-Time Updates
```
Time: 10:45:00 → [████░░░░░░] 30%
Time: 10:47:00 → [███████░░░] 60%
Time: 10:49:00 → [██████████] 100%

Automatically refreshes every 2 seconds
No page reload needed
Smooth progress updates
```

### Error Handling
```
Error Detected:
┌─────────────────────────────────┐
│ ❌ Error: API key not found     │
│                                 │
│ Please configure GEMINI_API_KEY │
│ in your .env file               │
│                                 │
│ [🔄 Try Again]                  │
└─────────────────────────────────┘
```

### Success Feedback
```
Success:
┌─────────────────────────────────┐
│ ✅ Tutorial generated!          │
│                                 │
│ 10 chapters created             │
│ 45KB total size                 │
│ Ready to download               │
│                                 │
│ [📖 View Results]               │
└─────────────────────────────────┘
```

## 🎬 Demo Script

### 5-Minute Demo
1. **Start** (0:00): Open app, show home page
2. **Configure** (0:30): Enter GitHub URL, adjust settings
3. **Generate** (1:00): Click generate, show progress
4. **Fast-forward** (1:30-4:00): Speed through generation
5. **Results** (4:00): Show statistics, preview, download
6. **Download** (4:30): Click download, show ZIP file
7. **Complete** (5:00): Summary and next steps

### 10-Minute Demo
- Add: Detailed configuration explanation
- Add: Step-by-step progress walkthrough
- Add: Preview multiple chapters
- Add: Show advanced settings
- Add: Demonstrate error handling
- Add: Compare with CLI version

---

This visual guide helps users understand what to expect at each step of the CodeSensei journey. The clean, modern interface makes AI-powered tutorial generation accessible to everyone! 🎓

