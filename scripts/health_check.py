"""
System Health Check Script
Validates all dependencies, configurations, and services
"""
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = []
        self.errors = []
        self.warnings = []
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 10:
            return True, f"[+] Python {version.major}.{version.minor}.{version.micro}"
        else:
            return False, f"[-] Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"
    
    def check_package(self, package_name: str, import_name: str = None) -> Tuple[bool, str]:
        """Check if a Python package is installed"""
        import_name = import_name or package_name
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'unknown')
                return True, f"[+] {package_name} ({version})"
            except:
                return True, f"[+] {package_name} (installed)"
        return False, f"[-] {package_name} (not installed)"
    
    def check_git(self) -> Tuple[bool, str]:
        """Check Git installation"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"[+] {version}"
            return False, "[-] Git not found"
        except:
            return False, "[-] Git not installed"
    
    def check_docker(self) -> Tuple[bool, str]:
        """Check Docker installation"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"[+] {version}"
            return False, "[-] Docker not found"
        except:
            return False, "[-] Docker not installed"
    
    def check_env_file(self) -> Tuple[bool, str]:
        """Check .env file exists"""
        env_file = self.project_root / ".env"
        if env_file.exists():
            return True, f"[+] .env file exists ({env_file})"
        return False, f"[!] .env file not found (copy from .env.example)"
    
    def check_git_config(self) -> Tuple[bool, str]:
        """Check Git configuration"""
        git_config = self.project_root / "config" / "git_config.yaml"
        if git_config.exists():
            return True, f"[+] Git config exists ({git_config})"
        return False, f"[-] Git config not found"
    
    def check_ollama(self) -> Tuple[bool, str]:
        """Check Ollama service"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return True, f"[+] Ollama running ({len(models)} models available)"
            return False, "[!] Ollama not responding"
        except:
            return False, "[!] Ollama not accessible (optional)"
    
    def check_database(self) -> Tuple[bool, str]:
        """Check database file"""
        db_file = self.project_root / "sql_app.db"
        if db_file.exists():
            size_kb = db_file.stat().st_size / 1024
            return True, f"[+] Database exists ({size_kb:.1f} KB)"
        return False, "[!] Database not initialized (will be created on first run)"
    
    def run_all_checks(self):
        """Run all health checks"""
        print("=" * 70)
        print("AI Orchestrator - System Health Check")
        print("=" * 70)
        print()
        
        # Python version
        print("[*] Python Environment")
        print("-" * 70)
        success, msg = self.check_python_version()
        print(msg)
        if not success:
            self.errors.append(msg)
        print()
        
        # Core dependencies
        print("[*] Core Dependencies")
        print("-" * 70)
        core_packages = [
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("pydantic", "pydantic"),
            ("sqlalchemy", "sqlalchemy"),
            ("torch", "torch"),
            ("transformers", "transformers"),
        ]
        
        for package, import_name in core_packages:
            success, msg = self.check_package(package, import_name)
            print(msg)
            if not success:
                self.errors.append(msg)
        print()
        
        # Optional dependencies
        print("[*] Optional Dependencies")
        print("-" * 70)
        optional_packages = [
            ("docker", "docker"),
            ("kubernetes", "kubernetes"),
            ("redis", "redis"),
            ("pymongo", "pymongo"),
        ]
        
        for package, import_name in optional_packages:
            success, msg = self.check_package(package, import_name)
            print(msg)
            if not success:
                self.warnings.append(msg)
        print()
        
        # External tools
        print("[*] External Tools")
        print("-" * 70)
        success, msg = self.check_git()
        print(msg)
        if not success:
            self.errors.append(msg)
        
        success, msg = self.check_docker()
        print(msg)
        if not success:
            self.warnings.append(msg)
        print()
        
        # Configuration files
        print("[*] Configuration")
        print("-" * 70)
        success, msg = self.check_env_file()
        print(msg)
        if not success:
            self.warnings.append(msg)
        
        success, msg = self.check_git_config()
        print(msg)
        if not success:
            self.errors.append(msg)
        print()
        
        # Services
        print("[*] Services")
        print("-" * 70)
        success, msg = self.check_ollama()
        print(msg)
        if not success:
            self.warnings.append(msg)
        
        success, msg = self.check_database()
        print(msg)
        if not success:
            self.warnings.append(msg)
        print()
        
        # Summary
        print("=" * 70)
        print("[*] Health Check Summary")
        print("=" * 70)
        
        if not self.errors and not self.warnings:
            print("[+] All checks passed! System is ready.")
            return 0
        
        if self.errors:
            print(f"\n[!] {len(self.errors)} Critical Error(s):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n[!] {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print()
        if self.errors:
            print("[*] Action Required:")
            print("   1. Install missing dependencies: pip install -r requirements.txt")
            print("   2. Configure environment: copy .env.example to .env")
            print("   3. Run Git setup: python scripts/setup_git.py")
            return 1
        else:
            print("[i] System is functional but some optional features may be unavailable.")
            return 0


def main():
    """Main entry point"""
    checker = HealthChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

