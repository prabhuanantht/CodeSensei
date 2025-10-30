"""
Code Security Analysis Module
Uses Bandit for Python security vulnerability scanning
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SecurityAnalyzer:
    """Analyze code for security vulnerabilities using Bandit"""
    
    def __init__(self):
        self.severity_levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3
        }
        self.confidence_levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3
        }
    
    def check_bandit_available(self) -> bool:
        """Check if Bandit is installed"""
        try:
            result = subprocess.run(
                ['bandit', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_bandit_instructions(self) -> str:
        """Return installation instructions for Bandit"""
        return """
### Bandit Installation Required

To enable code security analysis, please install Bandit:

**Mac/Linux:**
```bash
pip install bandit[toml]
```

**Windows:**
```bash
pip install bandit[toml]
```

After installation, refresh this page.
        """
    
    def scan_directory(
        self,
        directory: str,
        severity_filter: str = 'MEDIUM',
        confidence_filter: str = 'MEDIUM',
        categories: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> Tuple[Dict, str]:
        """
        Scan a directory for security vulnerabilities
        
        Args:
            directory: Path to directory to scan
            severity_filter: Minimum severity level (LOW, MEDIUM, HIGH)
            confidence_filter: Minimum confidence level (LOW, MEDIUM, HIGH)
            categories: List of vulnerability categories to check
            exclude_patterns: List of file patterns to exclude
            
        Returns:
            Tuple of (results_dict, error_message)
        """
        
        if not self.check_bandit_available():
            return {}, "Bandit is not installed. Please install it using: pip install bandit[toml]"
        
        # Create a temporary file for the JSON report
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        try:
            # Build bandit command
            cmd = [
                'bandit',
                '-r',  # recursive
                '-f', 'json',  # JSON format
                '-o', temp_file.name,  # output file
                '--severity-level', severity_filter.lower(),
                '--confidence-level', confidence_filter.lower(),
            ]
            
            # Add category filtering if specified
            if categories and len(categories) > 0:
                cmd.extend(['-t', ','.join(categories)])
            
            # Add exclude patterns
            if exclude_patterns and len(exclude_patterns) > 0:
                for pattern in exclude_patterns:
                    cmd.extend(['-x', pattern])
            
            # Add directory to scan
            cmd.append(directory)
            
            # Run bandit
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Read the JSON report
            with open(temp_file.name, 'r') as f:
                report = json.load(f)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            # Parse results
            parsed_results = self._parse_bandit_report(report, directory)
            
            return parsed_results, ""
            
        except subprocess.TimeoutExpired:
            os.unlink(temp_file.name)
            return {}, "Security scan timed out after 5 minutes"
        except json.JSONDecodeError as e:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return {}, f"Failed to parse Bandit report: {str(e)}"
        except Exception as e:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return {}, f"Error during security scan: {str(e)}"
    
    def _parse_bandit_report(self, report: Dict, directory: str) -> Dict:
        """
        Parse Bandit JSON report into a structured format
        
        Args:
            report: Raw Bandit report dictionary
            directory: Base directory being scanned
            
        Returns:
            Parsed results dictionary
        """
        
        results = {
            'summary': {
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0,
                'total_issues': 0,
                'files_scanned': 0,
                'files_with_issues': 0,
            },
            'vulnerabilities': [],
            'metadata': {
                'scanned_directory': directory,
                'scan_time': datetime.now().isoformat(),
                'bandit_version': report.get('version', 'unknown')
            }
        }
        
        # Count issues by severity
        metrics = report.get('metrics', {})
        summary = metrics.get('_totals', {})
        
        results['summary']['high_severity'] = summary.get('SEVERITY.HIGH', 0)
        results['summary']['medium_severity'] = summary.get('SEVERITY.MEDIUM', 0)
        results['summary']['low_severity'] = summary.get('SEVERITY.LOW', 0)
        results['summary']['total_issues'] = (
            results['summary']['high_severity'] +
            results['summary']['medium_severity'] +
            results['summary']['low_severity']
        )
        results['summary']['files_scanned'] = summary.get('loc', 0)
        
        # Extract vulnerabilities
        files_with_issues = {}
        
        for file_result in report.get('results', []):
            file_path = file_result.get('filename', 'unknown')
            # Prefer relative path for readability when possible
            try:
                relative_path = os.path.relpath(file_path, directory)
            except Exception:
                relative_path = file_path
            
            # Count unique files with issues
            if file_path not in files_with_issues:
                files_with_issues[file_path] = True
            
            # Create vulnerability entry
            vulnerability = {
                'file_path': file_path,
                'relative_path': relative_path,
                'line_number': file_result.get('line_number', 0),
                'issue_severity': file_result.get('issue_severity', 'UNKNOWN'),
                'issue_confidence': file_result.get('issue_confidence', 'UNKNOWN'),
                'test_name': file_result.get('test_name', 'Unknown Test'),
                'issue_text': file_result.get('issue_text', ''),
                'code': file_result.get('code', ''),
                'more_info': file_result.get('more_info', ''),
            }
            
            results['vulnerabilities'].append(vulnerability)
        
        results['summary']['files_with_issues'] = len(files_with_issues)
        
        # Sort vulnerabilities by severity (HIGH first)
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2, 'UNKNOWN': 3}
        results['vulnerabilities'].sort(
            key=lambda x: severity_order.get(x['issue_severity'], 99)
        )
        
        return results
    
    def get_severity_color(self, severity: str) -> str:
        """Get color code for severity level"""
        colors = {
            'HIGH': '#ef4444',      # red
            'MEDIUM': '#f59e0b',    # amber
            'LOW': '#10b981',       # green
            'UNKNOWN': '#6b7280'    # gray
        }
        return colors.get(severity, '#6b7280')
    
    def get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level"""
        emojis = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }
        return emojis.get(severity, '⚪')
    
    def get_confidence_badge(self, confidence: str) -> str:
        """Get badge text for confidence level"""
        badges = {
            'HIGH': 'High Confidence',
            'MEDIUM': 'Medium Confidence',
            'LOW': 'Low Confidence',
            'UNKNOWN': 'Unknown'
        }
        return badges.get(confidence, 'Unknown')
    
    def generate_html_report(self, results: Dict) -> str:
        """
        Generate an HTML report from security scan results
        
        Args:
            results: Parsed results dictionary
            
        Returns:
            HTML string
        """
        
        if not results or 'summary' not in results:
            return "<p>No security scan results available.</p>"
        
        summary = results['summary']
        vulnerabilities = results['vulnerabilities']
        metadata = results.get('metadata', {})
        
        html = f"""
        <html>
        <head>
            <title>Security Analysis Report</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9fafb;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .summary {{
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                }}
                .metric {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    flex: 1;
                    min-width: 200px;
                }}
                .metric.high {{ border-left: 4px solid #ef4444; }}
                .metric.medium {{ border-left: 4px solid #f59e0b; }}
                .metric.low {{ border-left: 4px solid #10b981; }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .vulnerability {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 15px;
                    border-left: 4px solid #ef4444;
                }}
                .vuln-header {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 10px;
                }}
                .severity-high {{ color: #ef4444; }}
                .severity-medium {{ color: #f59e0b; }}
                .severity-low {{ color: #10b981; }}
                .file-path {{
                    font-family: 'Courier New', monospace;
                    color: #6366f1;
                    font-size: 14px;
                }}
                .code-block {{
                    background: #1e293b;
                    color: #e2e8f0;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 10px 0;
                    overflow-x: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Security Analysis Report</h1>
                <p>Scanned: {metadata.get('scanned_directory', 'Unknown')}</p>
                <p>Time: {metadata.get('scan_time', 'Unknown')}</p>
            </div>
            
            <div class="summary">
                <div class="metric high">
                    <div>🔴 High Severity</div>
                    <div class="metric-value">{summary['high_severity']}</div>
                </div>
                <div class="metric medium">
                    <div>🟡 Medium Severity</div>
                    <div class="metric-value">{summary['medium_severity']}</div>
                </div>
                <div class="metric low">
                    <div>🟢 Low Severity</div>
                    <div class="metric-value">{summary['low_severity']}</div>
                </div>
                <div class="metric">
                    <div>📄 Files with Issues</div>
                    <div class="metric-value">{summary['files_with_issues']}</div>
                </div>
            </div>
            
            <h2>Vulnerabilities</h2>
        """
        
        if len(vulnerabilities) == 0:
            html += """
            <div style="background: white; padding: 40px; text-align: center; border-radius: 8px; color: #10b981;">
                <h2>✅ No Security Issues Found!</h2>
                <p>Your code passed all security checks.</p>
            </div>
            """
        else:
            for vuln in vulnerabilities:
                severity = vuln['issue_severity']
                emoji = self.get_severity_emoji(severity)
                color = self.get_severity_color(severity)
                
                html += f"""
                <div class="vulnerability">
                    <div class="vuln-header">
                        <span style="font-size: 24px;">{emoji}</span>
                        <h3 class="severity-{severity.lower()}">{severity} Severity: {vuln['test_name']}</h3>
                    </div>
                    <div class="file-path">📍 {vuln['file_path']}:{vuln['line_number']}</div>
                    <p><strong>Issue:</strong> {vuln['issue_text']}</p>
                    <p><strong>Confidence:</strong> {self.get_confidence_badge(vuln['issue_confidence'])}</p>
                    <div class="code-block">{vuln['code']}</div>
                    {f"<p><strong>More Info:</strong> <a href='{vuln['more_info']}' target='_blank'>{vuln['more_info']}</a></p>" if vuln['more_info'] else ''}
                </div>
                """
        
        html += """
        </body>
        </html>
        """
        
        return html
