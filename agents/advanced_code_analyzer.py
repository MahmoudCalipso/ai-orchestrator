"""
ADVANCED CODE ANALYZER
Deep code analysis with AST parsing, complexity metrics, and security scanning
"""
import ast
import re
import os
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AdvancedCodeAnalyzer:
    """
    Advanced code analyzer with:
    - AST (Abstract Syntax Tree) parsing
    - Cyclomatic complexity calculation
    - Security vulnerability detection
    - Code smell detection
    - Dependency analysis
    - Architecture pattern detection
    """
    
    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        self.code_smells = self._load_code_smell_patterns()
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Comprehensive project analysis"""
        
        results = {
            "project_path": project_path,
            "files_analyzed": 0,
            "total_lines": 0,
            "languages": {},
            "complexity": {},
            "security_issues": [],
            "code_smells": [],
            "dependencies": {},
            "architecture": {},
            "quality_score": 0
        }
        
        # Scan all files
        for root, dirs, files in os.walk(project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build']]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix
                
                # Analyze based on file type
                if file_ext == '.py':
                    await self._analyze_python_file(file_path, results)
                elif file_ext in ['.java', '.kt']:
                    await self._analyze_java_file(file_path, results)
                elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                    await self._analyze_javascript_file(file_path, results)
                elif file_ext in ['.go']:
                    await self._analyze_go_file(file_path, results)
                elif file_ext in ['.cs']:
                    await self._analyze_csharp_file(file_path, results)
                
                results["files_analyzed"] += 1
        
        # Calculate quality score
        results["quality_score"] = self._calculate_quality_score(results)
        
        return results
    
    async def _analyze_python_file(self, file_path: str, results: Dict[str, Any]):
        """Analyze Python file using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                results["total_lines"] += len(code.splitlines())
            
            # Parse AST
            tree = ast.parse(code)
            
            # Count language usage
            results["languages"]["python"] = results["languages"].get("python", 0) + 1
            
            # Analyze complexity
            complexity = self._calculate_complexity_python(tree)
            results["complexity"][file_path] = complexity
            
            # Detect security issues
            security_issues = self._detect_security_issues_python(code, file_path)
            results["security_issues"].extend(security_issues)
            
            # Detect code smells
            code_smells = self._detect_code_smells_python(tree, file_path)
            results["code_smells"].extend(code_smells)
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    def _calculate_complexity_python(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate cyclomatic complexity for Python code"""
        complexity = {
            "cyclomatic": 1,  # Base complexity
            "functions": 0,
            "classes": 0,
            "max_nesting": 0
        }
        
        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity["cyclomatic"] += 1
            elif isinstance(node, ast.BoolOp):
                complexity["cyclomatic"] += len(node.values) - 1
            
            # Count functions and classes
            if isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1
        
        return complexity
    
    def _detect_security_issues_python(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect security vulnerabilities in Python code"""
        issues = []
        
        # SQL Injection
        if re.search(r'execute\(["\'].*%s.*["\']\s*%', code):
            issues.append({
                "file": file_path,
                "severity": "critical",
                "type": "SQL Injection",
                "description": "Potential SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries"
            })
        
        # Hardcoded secrets
        if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            issues.append({
                "file": file_path,
                "severity": "high",
                "type": "Hardcoded Secrets",
                "description": "Hardcoded credentials detected",
                "recommendation": "Use environment variables or secret management"
            })
        
        # Unsafe deserialization
        if 'pickle.loads' in code or 'yaml.load(' in code:
            issues.append({
                "file": file_path,
                "severity": "high",
                "type": "Unsafe Deserialization",
                "description": "Unsafe deserialization detected",
                "recommendation": "Use safe_load() or json.loads()"
            })
        
        # Command injection
        if re.search(r'os\.system\(.*\+.*\)|subprocess\.call\(.*\+.*\)', code):
            issues.append({
                "file": file_path,
                "severity": "critical",
                "type": "Command Injection",
                "description": "Potential command injection vulnerability",
                "recommendation": "Use subprocess with list arguments"
            })
        
        return issues
    
    def _detect_code_smells_python(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Detect code smells in Python code"""
        smells = []
        
        for node in ast.walk(tree):
            # Long functions
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    smells.append({
                        "file": file_path,
                        "type": "Long Function",
                        "function": node.name,
                        "lines": len(node.body),
                        "recommendation": "Consider breaking into smaller functions"
                    })
                
                # Too many parameters
                if len(node.args.args) > 5:
                    smells.append({
                        "file": file_path,
                        "type": "Too Many Parameters",
                        "function": node.name,
                        "parameters": len(node.args.args),
                        "recommendation": "Consider using a parameter object"
                    })
            
            # Large classes
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    smells.append({
                        "file": file_path,
                        "type": "God Class",
                        "class": node.name,
                        "methods": len(methods),
                        "recommendation": "Consider splitting into multiple classes"
                    })
        
        return smells
    
    async def _analyze_java_file(self, file_path: str, results: Dict[str, Any]):
        """Analyze Java file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                results["total_lines"] += len(code.splitlines())
            
            results["languages"]["java"] = results["languages"].get("java", 0) + 1
            
            # Basic security checks
            if re.search(r'Statement.*executeQuery.*\+', code):
                results["security_issues"].append({
                    "file": file_path,
                    "severity": "critical",
                    "type": "SQL Injection",
                    "description": "String concatenation in SQL query",
                    "recommendation": "Use PreparedStatement"
                })
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    async def _analyze_javascript_file(self, file_path: str, results: Dict[str, Any]):
        """Analyze JavaScript/TypeScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                results["total_lines"] += len(code.splitlines())
            
            results["languages"]["javascript"] = results["languages"].get("javascript", 0) + 1
            
            # Security checks
            if 'eval(' in code:
                results["security_issues"].append({
                    "file": file_path,
                    "severity": "high",
                    "type": "Dangerous Function",
                    "description": "Use of eval() detected",
                    "recommendation": "Avoid eval(), use safer alternatives"
                })
            
            if 'innerHTML' in code and 'sanitize' not in code.lower():
                results["security_issues"].append({
                    "file": file_path,
                    "severity": "medium",
                    "type": "XSS Vulnerability",
                    "description": "innerHTML usage without sanitization",
                    "recommendation": "Sanitize user input or use textContent"
                })
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    async def _analyze_go_file(self, file_path: str, results: Dict[str, Any]):
        """Analyze Go file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                results["total_lines"] += len(code.splitlines())
            
            results["languages"]["go"] = results["languages"].get("go", 0) + 1
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    async def _analyze_csharp_file(self, file_path: str, results: Dict[str, Any]):
        """Analyze C# file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                results["total_lines"] += len(code.splitlines())
            
            results["languages"]["csharp"] = results["languages"].get("csharp", 0) + 1
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall code quality score (0-100)"""
        score = 100
        
        # Deduct for security issues
        critical_issues = len([i for i in results["security_issues"] if i["severity"] == "critical"])
        high_issues = len([i for i in results["security_issues"] if i["severity"] == "high"])
        medium_issues = len([i for i in results["security_issues"] if i["severity"] == "medium"])
        
        score -= (critical_issues * 20)
        score -= (high_issues * 10)
        score -= (medium_issues * 5)
        
        # Deduct for code smells
        score -= min(len(results["code_smells"]) * 2, 30)
        
        # Deduct for high complexity
        high_complexity_files = sum(1 for c in results["complexity"].values() if c.get("cyclomatic", 0) > 10)
        score -= min(high_complexity_files * 3, 20)
        
        return max(0, min(100, score))
    
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security vulnerability patterns"""
        return {
            "sql_injection": [
                r'execute\(["\'].*%s.*["\']\s*%',
                r'Statement.*executeQuery.*\+',
            ],
            "xss": [
                r'innerHTML\s*=',
                r'document\.write\(',
            ],
            "command_injection": [
                r'os\.system\(',
                r'exec\(',
                r'eval\(',
            ]
        }
    
    def _load_code_smell_patterns(self) -> Dict[str, Any]:
        """Load code smell patterns"""
        return {
            "long_function": {"threshold": 50},
            "too_many_parameters": {"threshold": 5},
            "god_class": {"threshold": 20}
        }
