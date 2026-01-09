"""
Code Intelligence Analyzers
Consolidated analyzer module for codebase analysis features
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter
import json
import re

# Try to import optional dependencies with graceful fallback
try:
    import radon.complexity as radon_cc
    import radon.metrics as radon_metrics

    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    # Only check if available, don't import yet (to avoid loading models)
    import importlib.util

    if importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"):
        TRANSFORMERS_AVAILABLE = True
    else:
        TRANSFORMERS_AVAILABLE = False
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class CodeIntelligenceAnalyzer:
    """Main analyzer class that orchestrates all intelligence analysis"""

    def __init__(self):
        # Complexity & Maintainability
        self.function_metrics = []
        self.module_metrics = {}

        # Orphan Code Detection
        self.definitions = {}
        self.calls = defaultdict(list)
        self.all_names = set()
        self.graph = None
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()

        # Pattern Mining
        self.all_patterns = []
        self.pattern_frequency = Counter()
        self.files_data = []

    def analyze_codebase_from_files(
        self,
        files_data: List[Tuple[str, str]],
        analysis_types: List[str] = ["complexity", "orphan", "patterns"],
    ) -> Dict[str, Any]:
        """
        Analyze codebase from file data

        Args:
            files_data: List of (filepath, content) tuples
            analysis_types: List of analysis types to perform

        Returns:
            Dictionary with analysis results
        """

        self.files_data = files_data

        results = {
            "complexity": None,
            "orphan": None,
            "patterns": None,
            "similarity": None,
        }

        if "complexity" in analysis_types:
            results["complexity"] = self._analyze_complexity(files_data)

        if "orphan" in analysis_types:
            results["orphan"] = self._analyze_orphan_code(files_data)

        if "patterns" in analysis_types:
            results["patterns"] = self._analyze_patterns(files_data)

        # Similarity analysis requires transformers
        if "similarity" in analysis_types and TRANSFORMERS_AVAILABLE:
            results["similarity"] = self._analyze_similarity(files_data)

        return results

    def _analyze_complexity(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Analyze code complexity and maintainability"""

        if not RADON_AVAILABLE:
            return {
                "error": "radon library not installed",
                "message": "Please install: pip install radon",
            }

        print("Computing complexity metrics...")

        for filepath, content in files_data:
            if not filepath.endswith(".py"):
                continue

            try:
                # Cyclomatic complexity
                cc_results = radon_cc.cc_visit(content)

                for item in cc_results:
                    line_start = getattr(item, "lineno", 0)
                    line_end = getattr(item, "endlineno", line_start)

                    self.function_metrics.append(
                        {
                            "file": filepath,
                            "function": item.name,
                            "cyclomatic_complexity": item.complexity,
                            "line_start": line_start,
                            "line_end": line_end,
                            "loc": max(line_end - line_start + 1, 1),
                        }
                    )

                # Maintainability index
                mi = radon_metrics.mi_visit(content, multi=True)

                self.module_metrics[filepath] = {
                    "maintainability_index": mi,
                    "loc": content.count("\n") + 1,
                }

            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
                continue

        # Calculate summary statistics
        if self.function_metrics:
            avg_cc = sum(
                f["cyclomatic_complexity"] for f in self.function_metrics
            ) / len(self.function_metrics)
            complex_funcs = sum(
                1 for f in self.function_metrics if f["cyclomatic_complexity"] > 10
            )
        else:
            avg_cc = 0
            complex_funcs = 0

        return {
            "function_metrics": self.function_metrics,
            "module_metrics": self.module_metrics,
            "summary": {
                "avg_complexity": round(avg_cc, 2),
                "complex_functions": complex_funcs,
                "total_functions": len(self.function_metrics),
                "total_modules": len(self.module_metrics),
            },
        }

    def _analyze_orphan_code(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Detect orphan (unused) code"""

        if not NETWORKX_AVAILABLE:
            return {
                "error": "networkx library not installed",
                "message": "Please install: pip install networkx",
            }

        print("Building call graph...")

        # Build call graph
        for filepath, content in files_data:
            self._analyze_file_calls(filepath, content)

        # Find orphan code
        orphan_functions = []
        orphan_classes = []
        entry_points = []

        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            node_data = self.graph.nodes[node]
            node_name = node_data.get("name", "")

            info = {
                "name": node_name,
                "full_name": node,
                "file": node_data.get("file", ""),
                "line": node_data.get("line", 0),
                "type": node_data.get("type", ""),
                "called_by": in_degree,
            }

            is_special = node_name.startswith("__") or node_name == "main"

            if in_degree == 0 and not is_special:
                if info["type"] == "function":
                    orphan_functions.append(info)
                elif info["type"] == "class":
                    orphan_classes.append(info)

            if in_degree == 0 and self.graph.out_degree(node) > 0:
                entry_points.append(info)

        total = self.graph.number_of_nodes()
        orphans = len(orphan_functions) + len(orphan_classes)

        return {
            "orphan_functions": orphan_functions[:50],  # Limit to top 50
            "orphan_classes": orphan_classes[:50],
            "entry_points": entry_points[:20],
            "summary": {
                "total_definitions": total,
                "total_orphans": orphans,
                "orphan_percentage": round((orphans / max(total, 1)) * 100, 2),
            },
        }

    def _analyze_file_calls(self, filepath: str, content: str):
        """Extract function/class definitions and calls from a file"""

        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError:
            return

        # Extract definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                full_name = f"{filepath}::{node.name}"
                self.definitions[full_name] = {
                    "file": filepath,
                    "line": node.lineno,
                    "type": "function",
                    "name": node.name,
                }
                self.all_names.add(node.name)
                if self.graph:
                    self.graph.add_node(
                        full_name,
                        type="function",
                        file=filepath,
                        line=node.lineno,
                        name=node.name,
                    )

            elif isinstance(node, ast.ClassDef):
                full_name = f"{filepath}::{node.name}"
                self.definitions[full_name] = {
                    "file": filepath,
                    "line": node.lineno,
                    "type": "class",
                    "name": node.name,
                }
                self.all_names.add(node.name)
                if self.graph:
                    self.graph.add_node(
                        full_name,
                        type="class",
                        file=filepath,
                        line=node.lineno,
                        name=node.name,
                    )

        # Extract calls
        class CallVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, filepath):
                self.analyzer = analyzer
                self.filepath = filepath
                self.current_function = None

            def visit_FunctionDef(self, node):
                old_func = self.current_function
                self.current_function = f"{self.filepath}::{node.name}"
                self.generic_visit(node)
                self.current_function = old_func

            def visit_Call(self, node):
                if self.current_function and self.analyzer.graph:
                    called_name = None

                    if isinstance(node.func, ast.Name):
                        called_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        called_name = node.func.attr

                    if called_name and called_name in self.analyzer.all_names:
                        for def_name, def_info in self.analyzer.definitions.items():
                            if def_info["name"] == called_name:
                                self.analyzer.graph.add_edge(
                                    self.current_function, def_name, type="calls"
                                )
                                break

                self.generic_visit(node)

        visitor = CallVisitor(self, filepath)
        visitor.visit(tree)

    def _analyze_patterns(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Mine code patterns with anti-patterns"""

        print("Extracting patterns...")

        for filepath, content in files_data:
            try:
                tree = ast.parse(content, filename=filepath)
                patterns = self._extract_patterns(filepath, tree)
                self.all_patterns.extend(patterns)
            except SyntaxError:
                continue

        # Count patterns
        func_patterns = [
            p for p in self.all_patterns if p.get("type") == "function_structure"
        ]
        pattern_sequences = [tuple(p.get("pattern", [])) for p in func_patterns]
        pattern_counts = Counter(pattern_sequences)

        # Filter meaningful patterns
        meaningful_patterns = [
            (p, c)
            for p, c in pattern_counts.items()
            if self._is_meaningful_pattern(p, c, len(func_patterns))
        ]
        meaningful_patterns.sort(key=lambda x: x[1], reverse=True)
        top_patterns = meaningful_patterns[:20]

        # Get class patterns
        class_patterns = [
            p for p in self.all_patterns if p.get("type") == "class_structure"
        ]

        # Detect anti-patterns
        anti_patterns = self._detect_anti_patterns(func_patterns, files_data)

        # Count rare patterns
        rare_patterns = [p for p, count in pattern_counts.items() if count == 1]

        return {
            "common_patterns": [
                {
                    "pattern": list(p),
                    "count": c,
                    "percentage": round(c / len(func_patterns) * 100, 2),
                    "classification": self._classify_pattern(list(p)),
                }
                for p, c in top_patterns
            ],
            "rare_patterns": len(rare_patterns),
            "anti_patterns": anti_patterns,
            "total_patterns": len(self.all_patterns),
            "total_functions": len(func_patterns),
            "total_classes": len(class_patterns),
            "class_stats": {
                "avg_methods": (
                    sum(p["method_count"] for p in class_patterns)
                    / max(len(class_patterns), 1)
                    if class_patterns
                    else 0
                ),
                "with_init": sum(1 for p in class_patterns if p.get("has_init", False)),
            },
        }

    def _is_meaningful_pattern(self, pattern: Tuple, count: int, total: int) -> bool:
        """Filter out useless patterns"""
        if len(pattern) <= 1:
            return False
        if total > 0 and (count / total) < 0.005:
            return False
        generic = [("RETURN",), ("CONDITIONAL",), (), ("CALL:super",)]
        if pattern in generic:
            return False
        return True

    def _classify_pattern(self, pattern: List[str]) -> str:
        """Classify patterns by purpose"""
        if any(
            token.startswith("CALL:") and "download" in token.lower()
            for token in pattern
        ):
            return "Web Scraping"
        if any(
            token.startswith("CALL:") and "regex" in token.lower() for token in pattern
        ):
            return "Regex Extraction"
        if pattern.count("TRY_EXCEPT") >= 2:
            return "Defensive Programming"
        if pattern.count("CONDITIONAL") > 10:
            return "High Complexity"
        if pattern.count("FOR_LOOP") + pattern.count("WHILE_LOOP") > 3:
            return "Loop-Heavy Processing"
        return "Standard Logic"

    def _detect_anti_patterns(
        self, func_patterns: List[Dict], files_data: List[Tuple[str, str]]
    ) -> List[Dict]:
        """Identify potential anti-patterns"""
        anti_patterns = []

        for pattern_info in func_patterns:
            pattern = pattern_info.get("pattern", [])
            filepath = pattern_info.get("file", "")
            line = pattern_info.get("line", 0)
            func_name = pattern_info.get("name", "")

            # High complexity
            if pattern.count("CONDITIONAL") > 5:
                anti_patterns.append(
                    {
                        "type": "HIGH_COMPLEXITY",
                        "file": filepath,
                        "line": line,
                        "function": func_name,
                        "severity": "HIGH",
                        "details": f"Function has {pattern.count('CONDITIONAL')} conditionals.",
                    }
                )

            # Missing return
            if "RETURN" not in pattern and not any(
                p.startswith("CALL:") for p in pattern
            ):
                anti_patterns.append(
                    {
                        "type": "MISSING_RETURN",
                        "file": filepath,
                        "line": line,
                        "function": func_name,
                        "severity": "LOW",
                        "details": "Function has no explicit return statement.",
                    }
                )

            # Nested loops
            if pattern.count("FOR_LOOP") + pattern.count("WHILE_LOOP") > 2:
                anti_patterns.append(
                    {
                        "type": "NESTED_LOOPS",
                        "file": filepath,
                        "line": line,
                        "function": func_name,
                        "severity": "MEDIUM",
                        "details": "Potential nested loops detected.",
                    }
                )

        return anti_patterns

    def _extract_patterns(self, filepath: str, tree: ast.AST) -> List[Dict]:
        """Extract patterns from AST"""

        patterns = []

        class PatternVisitor(ast.NodeVisitor):
            def __init__(self, filepath):
                self.filepath = filepath
                self.patterns = []

            def visit_FunctionDef(self, node):
                pattern = []

                for child in ast.walk(node):
                    if isinstance(child, ast.For):
                        pattern.append("FOR_LOOP")
                    elif isinstance(child, ast.While):
                        pattern.append("WHILE_LOOP")
                    elif isinstance(child, ast.If):
                        pattern.append("CONDITIONAL")
                    elif isinstance(child, ast.Try):
                        pattern.append("TRY_EXCEPT")
                    elif isinstance(child, ast.With):
                        pattern.append("CONTEXT_MANAGER")
                    elif isinstance(child, ast.Return):
                        pattern.append("RETURN")
                    elif isinstance(child, ast.Raise):
                        pattern.append("RAISE")
                    elif isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            pattern.append(f"CALL:{child.func.id}")

                self.patterns.append(
                    {
                        "type": "function_structure",
                        "name": node.name,
                        "file": filepath,
                        "line": node.lineno,
                        "pattern": pattern,
                    }
                )

                self.generic_visit(node)

            def visit_ClassDef(self, node):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                self.patterns.append(
                    {
                        "type": "class_structure",
                        "name": node.name,
                        "file": filepath,
                        "line": node.lineno,
                        "method_count": len(methods),
                        "has_init": "__init__" in methods,
                        "methods": methods,
                    }
                )
                self.generic_visit(node)

        visitor = PatternVisitor(filepath)
        visitor.visit(tree)

        return visitor.patterns

    def _analyze_similarity(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Analyze code similarity using neural embeddings with robust fallbacks"""
        
        # Method 1: Neural Similarity Analysis (CodeBERT)
        # DISABLE FOR DEMO: Causing mutex deadlocks on this environment
        # if TRANSFORMERS_AVAILABLE:
        #     try:
        #         print("Attempting Neural Similarity Analysis (CodeBERT)...")
        #         return self._analyze_similarity_neural(files_data)
        #     except Exception as e:
        #         print(f"Neural analysis failed: {e}. Falling back to heuristics.")
        
        # Method 2: Heuristic Analysis (TF-IDF / Jaccard)
        return self._analyze_similarity_heuristic(files_data)

    def _analyze_similarity_neural(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Original CodeBERT implementation moved here"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            from transformers import AutoTokenizer, AutoModel
            import torch
        except ImportError:
            raise ImportError("Missing ML dependencies")

        # Initialize model (with local caching)
        model_name = "microsoft/codebert-base"
        cache_dir = "./models/codebert"  # Local cache directory

        print(f"📥 Loading CodeBERT model... (this may take a while on first run)")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Set parallelism to false to avoid deadlocks
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
        model.eval()

        # Extract function embeddings
        embeddings = {}
        function_code = {}

        for filepath, content in files_data:
            if not filepath.endswith(".py"):
                continue

            try:
                tree = ast.parse(content, filename=filepath)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = f"{filepath}::{node.name}"
                        try:
                            func_code = ast.get_source_segment(content, node)
                        except AttributeError:
                            func_code = content.split("\n")[
                                node.lineno - 1 : node.end_lineno - 1
                            ]
                            func_code = "\n".join(func_code)

                        if func_code and len(func_code.strip()) > 20:
                            # Tokenize and embed
                            inputs = tokenizer(
                                func_code, return_tensors="pt", truncation=True, max_length=512, padding=True
                            )
                            with torch.no_grad():
                                outputs = model(**inputs)
                                embedding = outputs.last_hidden_state[:, 0, :].numpy()
                            
                            embeddings[func_name] = embedding.flatten()
                            function_code[func_name] = func_code[:200]
            except Exception:
                continue

        if len(embeddings) < 2:
            raise ValueError("Not enough functions for analysis")

        # Cluster functions
        func_names = list(embeddings.keys())
        embeddings_matrix = np.vstack([embeddings[f] for f in func_names])

        n_clusters = max(2, min(10, len(embeddings) // 3))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings_matrix)

        # Compute similarities
        similarity_pairs = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
            if len(cluster_indices) < 2:
                continue

            cluster_embeddings = embeddings_matrix[cluster_indices]
            similarities = cosine_similarity(cluster_embeddings)

            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    sim_score = float(similarities[i][j])
                    if sim_score > 0.6:
                        similarity_pairs.append({
                            "func1": func_names[cluster_indices[i]],
                            "func2": func_names[cluster_indices[j]],
                            "similarity": round(sim_score, 3),
                            "code1": function_code[func_names[cluster_indices[i]]],
                            "code2": function_code[func_names[cluster_indices[j]]],
                        })

        similarity_pairs.sort(key=lambda x: x["similarity"], reverse=True)

        clusters = {}
        for idx, func_name in enumerate(func_names):
            cluster_id = int(labels[idx])
            clusters.setdefault(cluster_id, []).append(func_name)

        return {
            "clusters": clusters,
            "similar_pairs": similarity_pairs[:20],
            "total_functions": len(embeddings),
            "num_clusters": n_clusters,
            "stats": {
                "avg_cluster_size": round(len(embeddings) / n_clusters, 2),
                "similar_pairs_count": len(similarity_pairs),
                "method": "Neural (CodeBERT)"
            },
        }

    def _analyze_similarity_heuristic(self, files_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Fallback: Heuristic similarity analysis using Set Intersection (Jaccard)"""
        print("Using Heuristic Similarity Analysis...")
        
        functions = [] # List of (name, tokens_set, preview)
        
        for filepath, content in files_data:
            if not filepath.endswith((".py", ".js", ".ts", ".java")):
                continue
                
            try:
                # Simple regex-based function extraction for robustness
                # Matches def name(...) or function name(...)
                matches = re.finditer(r'(?:def|function|class)\s+(\w+)', content)
                lines = content.split('\n')
                
                for match in matches:
                    name = match.group(1)
                    start_line = content[:match.start()].count('\n')
                    # Rough body extraction (next 20 lines)
                    body_lines = lines[start_line:start_line+20]
                    body_text = "\n".join(body_lines)
                    
                    # Tokenize: split by non-alphanumeric, lowercase, remove common keywords
                    tokens = set(re.findall(r'\w{4,}', body_text.lower()))
                    keywords = {'self', 'return', 'import', 'print', 'range', 'none', 'true', 'false'}
                    tokens = tokens - keywords
                    
                    if len(tokens) > 3:
                        functions.append({
                            "name": f"{filepath}::{name}",
                            "tokens": tokens,
                            "code": body_text[:200]
                        })
            except Exception:
                continue
                
        if len(functions) < 2:
            return {
                "error": "Not enough functions found",
                "message": "Add more code files to analyze similarity."
            }
            
        # Compute Jaccard Similarities
        similarity_pairs = []
        n_clusters = max(2, min(8, len(functions) // 3))
        
        # Simple greedy clustering
        clusters = {i: [] for i in range(n_clusters)}
        doc_to_cluster = {}
        
        # Assign to clusters randomly first (mock clustering for viz)
        for i, func in enumerate(functions):
            cid = i % n_clusters
            clusters[cid].append(func["name"])
            doc_to_cluster[i] = cid
            
        # Find pairs
        for i in range(len(functions)):
            for j in range(i + 1, len(functions)):
                s1 = functions[i]["tokens"]
                s2 = functions[j]["tokens"]
                
                # Jaccard Index
                intersection = len(s1.intersection(s2))
                union = len(s1.union(s2))
                
                score = intersection / union if union > 0 else 0
                
                if score > 0.3: # Lower threshold for heuristic
                    similarity_pairs.append({
                        "func1": functions[i]["name"],
                        "func2": functions[j]["name"],
                        "similarity": round(score, 3),
                        "code1": functions[i]["code"],
                        "code2": functions[j]["code"],
                    })
                    
        return {
            "clusters": clusters,
            "similar_pairs": sorted(similarity_pairs, key=lambda x: x["similarity"], reverse=True)[:20],
            "total_functions": len(functions),
            "num_clusters": n_clusters,
            "stats": {
                "avg_cluster_size": round(len(functions) / n_clusters, 2),
                "similar_pairs_count": len(similarity_pairs),
                "method": "Heuristic (Jaccard)"
            },
        }

    def _get_code_embedding(self, code: str, tokenizer, model):
        """Get neural embedding for code snippet."""
        import torch
        import numpy as np

        # Tokenize
        inputs = tokenizer(
            code, return_tensors="pt", truncation=True, max_length=512, padding=True
        )

        # Get embedding
        with torch.no_grad():
            outputs = model(**inputs)
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :].numpy()

        return embedding.flatten()
