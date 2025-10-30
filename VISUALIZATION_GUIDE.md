# Visualization Guide for Code Intelligence

## How to See the Visualizations

The graphs and charts are integrated into the Code Intelligence tab. Here's how to access them:

### Step 1: Start the App
```bash
streamlit run app_new.py
```

### Step 2: Load a Codebase
- Enter a GitHub URL or local path
- Wait for the codebase to load

### Step 3: Go to Code Intelligence Tab
Click on the 🧠 Code Intelligence tab

### Step 4: Run Analyses

For each subtab, you need to click the button to run the analysis FIRST:

#### 📊 Complexity & Maintainability
1. Click "▶ Run Complexity Analysis"
2. Wait for "✅ Complete!" message
3. Scroll down past the metrics
4. You'll see "### 📊 Visualizations" section with:
   - Complexity Distribution histogram
   - Top 10 Most Complex Functions bar chart

#### 🔍 Orphan Code Detection
1. Click "▶ Detect Orphan Code"
2. Wait for "✅ Complete!" message
3. Scroll down past the metrics
4. You'll see visualizations:
   - Orphan Code Distribution pie chart
   - Top Files with Orphan Functions bar chart

#### 🔗 Code Similarity
1. Click "▶ Analyze Code Similarity"
2. Wait for model loading and analysis
3. Scroll down to see visualizations:
   - Similarity Score Distribution
   - Cluster distribution pie chart
   - Top Similar Pairs bar chart

#### 🎯 Pattern Mining
1. Click "▶ Mine Code Patterns"
2. Wait for analysis
3. Scroll down to see:
   - Classification Distribution
   - Pattern Frequency scatter plot
   - Anti-Pattern Severity pie chart
   - Anti-Pattern Types bar chart

## Troubleshooting

### Charts Not Showing?

1. **Check if analysis completed**: Look for "✅ Complete!" message
2. **Scroll down**: Charts appear AFTER the summary metrics
3. **Check data exists**: Charts only show if there's data (e.g., >0 functions)
4. **Refresh the app**: Sometimes Streamlit needs a refresh after installation

### Libraries Missing?

Run:
```bash
pip install plotly pandas numpy
```

### Still Not Working?

Check console for errors - the debug message "Rendering X functions" should appear if data is found.
