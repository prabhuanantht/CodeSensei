"""
Code Intelligence Tab Implementation
Handles rendering of the Code Intelligence tab with all four sub-features
"""

import streamlit as st
from pathlib import Path


def render_intelligence_tab():
    """Render the Code Intelligence tab"""

    from intelligence_analyzer import CodeIntelligenceAnalyzer

    # Check if available
    try:
        analyzer = CodeIntelligenceAnalyzer()
    except Exception as e:
        st.error("🧠 Intelligence analyzer not available")
        st.code(f"Error: {str(e)}", language="bash")
        st.markdown("Please install: `pip install radon networkx`")
        return

    st.markdown("## 🧠 Code Intelligence")
    st.markdown("Deep analysis of your codebase structure and quality.")
    st.markdown("---")

    # Get codebase source
    if not st.session_state.get("codebase_source"):
        st.warning("⚠️ Please enter a codebase source first")
        return

    # Get files from codebase
    files_data = _get_files_from_codebase()

    if not files_data:
        st.error("❌ No Python files found in the codebase")
        return

    st.info(f"📂 Found {len(files_data)} Python files to analyze")

    intel_tab1, intel_tab2, intel_tab3, intel_tab4 = st.tabs(
        [
            "📊 Complexity & Maintainability",
            "🔍 Orphan Code Detection",
            "🔗 Code Similarity",
            "🎯 Pattern Mining",
        ]
    )

    with intel_tab1:
        _render_complexity_tab(analyzer, files_data)

    with intel_tab2:
        _render_orphan_tab(analyzer, files_data)

    with intel_tab3:
        _render_similarity_tab()

    with intel_tab4:
        _render_pattern_tab(analyzer, files_data)


def _get_files_from_codebase():
    """Get Python files from the codebase"""
    files_data = []

    if st.session_state.codebase_type == "github":
        # Use cached directory if available
        project_name = st.session_state.codebase_source.split("/")[-1].replace(
            ".git", ""
        )
        cache_dir = Path("./cache") / project_name
        if cache_dir.exists():
            for py_file in cache_dir.rglob("*.py"):
                if any(
                    skip in str(py_file)
                    for skip in proving["test", "example", "__pycache__"]
                ):
                    continue
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        files_data.append(
                            (str(py_file.relative_to(cache_dir)), f.read())
                        )
                except Exception:
                    continue
    else:
        # Local directory
        source_path = Path(st.session_state.codebase_source)
        if source_path.exists():
            for py_file in source_path.rglob("*.py"):
                if any(
                    skip in str(py_file) for skip in ["test", "example", "__pycache__"]
                ):
                    continue
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        files_data.append(
                            (str(py_file.relative_to(source_path)), f.read())
                        )
                except Exception:
                    continue

    return files_data


def _render_complexity_tab(analyzer, files_data):
    """Render complexity analysis tab"""
    st.markdown("### Code Complexity & Maintainability Analysis")
    st.info("Analyze cyclomatic complexity, maintainability index, and code metrics")

    if st.button("▶ Run Complexity Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing code complexity..."):
            results = analyzer.analyze_codebase_from_files(files_data, ["complexity"])

            if "complexity" in results and results["complexity"]:
                if "error" in results["complexity"]:
                    st.error(f"❌ {results['complexity']['error']}")
                else:
                    st.session_state.complexity_results = results["complexity"]
                    st.success("✅ Analysis complete!")

    if st.session_state.get("complexity_results"):
        _display_complexity_results(st.session_state.complexity_results)


def _display_complexity_results(complexity):
    """Display complexity analysis results"""
    st.markdown("---")
    st.markdown("### Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Functions", complexity["summary"]["total_functions"])
    with col2:
        st.metric("Avg Complexity", complexity["summary"]["avg_complexity"])
    with col3:
        st.metric("Complex Functions", complexity["summary"]["complex_functions"])
    with col4:
        st.metric("Total Modules", complexity["summary"]["total_modules"])

    st.markdown("---")
    st.markdown("### Most Complex Functions")

    sorted_funcs = sorted(
        complexity["function_metrics"],
        key=lambda x: x["cyclomatic_complexity"],
        reverse=True,
    )[:20]

    for func in sorted_funcs:
        with st.expander(
            f"{func['function']} (CC: {func['cyclomatic_complexity']})", expanded=False
        ):
            st.markdown(f"**File:** `{func['file']}`")
            st.markdown(f"**Lines:** {func['line_start']}-{func['line_end']}")
            st.markdown(f"**Complexity:** {func['cyclomatic_complexity']}")
            st.markdown(f"**LOC:** {func['loc']}")


def _render_orphan_tab(analyzer, files_data):
    """Render orphan code detection tab"""
    st.markdown("### Orphan Code Detection")
    st.info("Find unused functions, classes, and modules that can be safely removed")

    if st.button("▶ Detect Orphan Code", type="primary", use_container_width=True):
        with st.spinner("Detecting orphan code..."):
            results = analyzer.analyze_codebase_from_files(files_data, ["orphan"])

            if "orphan" in results and results["orphan"]:
                if "error" in results["orphan"]:
                    st.error(f"❌ {results['orphan']['error']}")
                else:
                    st.session_state.orphan_results = results["orphan"]
                    st.success("✅ Analysis complete!")

    if st.session_state.get("orphan_results"):
        _display_贾
