"""
Template Code Processor
Handles downloading, analyzing, and customizing purchased code templates
"""
import logging
import zipfile
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class TemplateProcessor:
    """Processes and customizes code templates"""
    
    def __init__(self, temp_dir: str = "temp/templates"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_template(self, url: str, template_name: str) -> Optional[Path]:
        """Download template from URL"""
        try:
            logger.info(f"Downloading template from {url}")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save to temp directory
            template_path = self.temp_dir / f"{template_name}.zip"
            with open(template_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Template downloaded to {template_path}")
            return template_path
            
        except Exception as e:
            logger.error(f"Failed to download template: {e}")
            return None
    
    async def extract_template(self, zip_path: Path) -> Optional[Path]:
        """Extract template ZIP file"""
        try:
            extract_dir = self.temp_dir / zip_path.stem
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Template extracted to {extract_dir}")
            return extract_dir
            
        except Exception as e:
            logger.error(f"Failed to extract template: {e}")
            return None
    
    async def analyze_template(self, template_dir: Path) -> Dict[str, Any]:
        """Analyze template structure and identify customization points"""
        analysis = {
            "structure": {},
            "config_files": [],
            "variables": [],
            "entry_points": []
        }
        
        try:
            # Find configuration files
            config_patterns = ['config.json', 'settings.json', '.env', 'package.json', 'composer.json']
            for pattern in config_patterns:
                config_files = list(template_dir.rglob(pattern))
                analysis["config_files"].extend([str(f.relative_to(template_dir)) for f in config_files])
            
            # Identify entry points
            entry_patterns = ['index.html', 'main.js', 'app.js', 'index.php', 'main.py']
            for pattern in entry_patterns:
                entry_files = list(template_dir.rglob(pattern))
                analysis["entry_points"].extend([str(f.relative_to(template_dir)) for f in entry_files])
            
            # Build directory structure
            analysis["structure"] = self._build_structure_tree(template_dir)
            
            logger.info(f"Template analysis complete: {len(analysis['config_files'])} config files, {len(analysis['entry_points'])} entry points")
            return analysis
            
        except Exception as e:
            logger.error(f"Template analysis failed: {e}")
            return analysis
    
    def _build_structure_tree(self, directory: Path, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Build directory structure tree"""
        if current_depth >= max_depth:
            return {}
        
        tree = {}
        try:
            for item in directory.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    tree[item.name] = self._build_structure_tree(item, max_depth, current_depth + 1)
                elif item.is_file():
                    tree[item.name] = "file"
        except PermissionError:
            pass
        
        return tree
    
    async def customize_template(self, template_dir: Path, variables: Dict[str, str]) -> bool:
        """Replace variables in template files"""
        try:
            # File extensions to process
            text_extensions = ['.html', '.js', '.css', '.json', '.php', '.py', '.java', '.cs', '.xml', '.yml', '.yaml', '.md', '.txt']
            
            for file_path in template_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix in text_extensions:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        # Replace variables (format: {{VARIABLE_NAME}})
                        modified = False
                        for var_name, var_value in variables.items():
                            placeholder = f"{{{{{var_name}}}}}"
                            if placeholder in content:
                                content = content.replace(placeholder, var_value)
                                modified = True
                        
                        if modified:
                            file_path.write_text(content, encoding='utf-8')
                            logger.debug(f"Customized {file_path.relative_to(template_dir)}")
                    
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        continue
            
            logger.info("Template customization complete")
            return True
            
        except Exception as e:
            logger.error(f"Template customization failed: {e}")
            return False
    
    async def merge_with_generated_code(self, template_dir: Path, generated_code: Dict[str, str], output_dir: Path) -> bool:
        """Merge template with generated code"""
        try:
            # Copy template to output directory
            if output_dir.exists():
                shutil.rmtree(output_dir)
            shutil.copytree(template_dir, output_dir)
            
            # Write generated code files
            for filename, code in generated_code.items():
                # Determine appropriate directory based on file type
                if filename.endswith('Controller.py') or filename.endswith('Controller.java'):
                    target_dir = output_dir / "controllers"
                elif filename.endswith('Model.py') or filename.endswith('Entity.java'):
                    target_dir = output_dir / "models"
                elif filename.endswith('Repository.py') or filename.endswith('Repository.java'):
                    target_dir = output_dir / "repositories"
                else:
                    target_dir = output_dir / "generated"
                
                target_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = target_dir / filename
                file_path.write_text(code, encoding='utf-8')
                logger.debug(f"Wrote generated file: {file_path.relative_to(output_dir)}")
            
            logger.info(f"Template merged with generated code at {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Template merge failed: {e}")
            return False
    
    async def process_template(self, url: str, template_name: str, variables: Dict[str, str], generated_code: Dict[str, str], output_dir: Path) -> bool:
        """Complete template processing workflow"""
        try:
            # Download
            zip_path = await self.download_template(url, template_name)
            if not zip_path:
                return False
            
            # Extract
            template_dir = await self.extract_template(zip_path)
            if not template_dir:
                return False
            
            # Analyze
            analysis = await self.analyze_template(template_dir)
            logger.info(f"Template structure: {analysis['structure']}")
            
            # Customize
            if not await self.customize_template(template_dir, variables):
                return False
            
            # Merge with generated code
            if not await self.merge_with_generated_code(template_dir, generated_code, output_dir):
                return False
            
            # Cleanup
            zip_path.unlink()
            shutil.rmtree(template_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Template processing failed: {e}")
            return False
