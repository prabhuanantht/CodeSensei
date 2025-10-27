# Testing Guide - Mermaid Rendering Feature

## Quick Test

### 1. Restart Streamlit App

**Important:** Stop the current Streamlit app and restart it to load the new code.

```bash
# Stop the app with Ctrl+C, then restart:
streamlit run app.py
```

### 2. Test with Existing Generated Tutorials

If you already have tutorials in the `output/` directory:

1. Navigate to **Results** page from sidebar
2. Open any chapter or the index page
3. Look for rendered diagrams (they should appear as visual graphics, not code blocks)

### 3. Test with New Generation

Generate a new tutorial to test real-time rendering:

1. Go to **Configure** page
2. Enter a repository URL (or use local directory)
   - Example: `https://github.com/tiangolo/fastapi`
3. Click **Generate Tutorial**
4. Watch the **Generated Files** column on the right
5. Click on any generated file to see preview with rendered diagrams

### 4. Verify Diagram Rendering

**What to look for:**
- ✅ Diagrams appear as graphics, not code
- ✅ Diagrams are interactive (hoverable)
- ✅ Clean styling with white background
- ✅ Diagrams are centered and properly sized
- ✅ Multiple diagrams render correctly

**What should NOT happen:**
- ❌ Raw mermaid code showing as text
- ❌ Blank spaces where diagrams should be
- ❌ JavaScript errors in browser console
- ❌ Diagrams overlapping with text

## Expected Behavior

### In Generation Page

**Generated Files Panel (Right Column):**
- Files appear one by one as created
- File expanders show content preview
- If preview includes mermaid code, it should render as diagram
- Diagram height: ~450px with scroll if needed

### In Results Page

**Index Page:**
- Mermaid diagram showing project architecture
- Rendered as flowchart with nodes and edges
- Clean, professional appearance

**Chapter Pages:**
- Mermaid diagrams showing:
  - Sequence diagrams for interactions
  - Flowcharts for processes
  - Class diagrams for structures
- All rendered visually, not as code

## Troubleshooting

### Issue: Diagrams not rendering

**Check:**
1. Browser console for errors (F12 → Console tab)
2. Internet connection (needs CDN access)
3. Markdown syntax is correct (` ```mermaid ` not ` ```diagram `)

**Solution:**
- Refresh the page
- Clear browser cache
- Try different browser

### Issue: "Failed to load module script"

**Cause:** Browser blocking module imports

**Solution:**
- Check if browser extensions are blocking scripts
- Try in incognito/private mode
- Use different browser

### Issue: Diagram too small/large

**Expected:** Diagrams auto-size to content
**Workaround:** Use scroll within diagram container

### Issue: Diagram shows code instead

**Cause:** Markdown not being parsed correctly

**Check:**
1. Verify code block syntax: ` ```mermaid ` (with newline after)
2. Check closing ` ``` ` (on its own line)
3. Ensure proper indentation

## Sample Test Cases

### Test Case 1: Simple Flowchart

Create a test markdown file with:

```markdown
# Test Chapter

Here's a simple flowchart:

\```mermaid
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]
\```

Some text after the diagram.
```

**Expected:** Diagram renders as 3 boxes with arrows

### Test Case 2: Sequence Diagram

```markdown
## Test Sequence

\```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi!
\```
```

**Expected:** Diagram shows interaction between Alice and Bob

### Test Case 3: Multiple Diagrams

```markdown
# Multiple Diagrams

First diagram:

\```mermaid
flowchart TD
    A --> B
\```

Second diagram:

\```mermaid
sequenceDiagram
    X->>Y: Message
\```
```

**Expected:** Both diagrams render correctly, one after another

## Performance Testing

### Metrics to Monitor

1. **Load Time** - Diagrams should render within 1-2 seconds
2. **Memory Usage** - Should not increase significantly with multiple diagrams
3. **CPU Usage** - Brief spike during rendering, then normal
4. **Responsiveness** - UI should remain responsive during rendering

### Stress Test

Generate a tutorial with many chapters to test:
- Multiple files with diagrams
- Real-time rendering performance
- Memory management with many diagrams

## Browser Compatibility

Test in multiple browsers:

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 90+     | ✅ Should work |
| Firefox | 88+     | ✅ Should work |
| Safari  | 14+     | ✅ Should work |
| Edge    | 90+     | ✅ Should work |

## Success Criteria

✅ All mermaid code blocks render as diagrams
✅ No JavaScript errors in console
✅ Diagrams are interactive and properly styled
✅ Performance remains acceptable with multiple diagrams
✅ Real-time preview shows diagrams as files are generated
✅ Results page displays all diagrams correctly
✅ Works across major browsers

## Reporting Issues

If you encounter issues, please note:
1. Browser and version
2. Error messages (from console)
3. Screenshot of the issue
4. Steps to reproduce
5. Sample markdown that doesn't render

---

**Happy Testing! 🎉**

The mermaid rendering feature should make the generated tutorials much more visual and engaging!

