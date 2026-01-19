"""
LSP Proxy Service - Language Server Protocol Bridge
Connects Monaco Editor to headless language servers.
"""
import asyncio
import json
import logging
import subprocess
import threading
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class LSPProxyService:
    """Proxies LSP JSON-RPC communication between the frontend and headless servers"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LSPProxyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.active_servers: Dict[str, subprocess.Popen] = {}
        self.output_callbacks: Dict[str, List[Callable]] = {}
        
        # Default LSP server commands
        self.server_configs = {
            "python": ["pyright-langserver", "--stdio"],
            "typescript": ["typescript-language-server", "--stdio"],
            "javascript": ["typescript-language-server", "--stdio"],
            "go": ["gopls"],
            "rust": ["rust-analyzer"],
            "java": ["jdtls"]
        }
        self._initialized = True
        logger.info("LSP Proxy Service initialized")

    def start_server(self, project_id: str, language: str, workspace_root: str) -> bool:
        """Initialize and start an LSP server for a specific language"""
        server_id = f"{project_id}:{language}"
        if server_id in self.active_servers: return True
        
        cmd = self.server_configs.get(language)
        if not cmd:
            logger.error(f"LSP: No server config for {language}")
            return False
            
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace_root,
                bufsize=0
            )
            self.active_servers[server_id] = process
            
            # Start reader thread
            thread = threading.Thread(target=self._read_output, args=(server_id, process), daemon=True)
            thread.start()
            
            logger.info(f"LSP: Started {language} server for {project_id}")
            return True
        except Exception as e:
            logger.error(f"LSP: Failed to launch {language} server: {e}")
            return False

    def send_message(self, project_id: str, language: str, message: Dict[str, Any]):
        """Forward a message from client to the LSP server"""
        server_id = f"{project_id}:{language}"
        process = self.active_servers.get(server_id)
        if not process: return
        
        try:
            json_str = json.dumps(message)
            msg = f"Content-Length: {len(json_str)}\r\n\r\n{json_str}"
            process.stdin.write(msg.encode('utf-8'))
            process.stdin.flush()
        except Exception as e:
            logger.error(f"LSP: Write error for {server_id}: {e}")

    def add_callback(self, project_id: str, language: str, callback: Callable):
        """Add a callback to receive LSP server responses"""
        server_id = f"{project_id}:{language}"
        if server_id not in self.output_callbacks:
            self.output_callbacks[server_id] = []
        self.output_callbacks[server_id].append(callback)

    def stop_server(self, project_id: str, language: str):
        """Shutdown an LSP server instance"""
        server_id = f"{project_id}:{language}"
        process = self.active_servers.get(server_id)
        if process:
            process.terminate()
            del self.active_servers[server_id]
            if server_id in self.output_callbacks:
                del self.output_callbacks[server_id]
            logger.info(f"LSP: Stopped {server_id}")

    def _read_output(self, server_id: str, process: subprocess.Popen):
        """Internal reader thread for LSP stdout"""
        while True:
            if process.poll() is not None: break
            
            try:
                line = process.stdout.readline().decode('utf-8')
                if not line or not line.startswith("Content-Length:"): continue
                
                content_length = int(line.split(":")[1].strip())
                process.stdout.readline() # Skip \r\n
                
                body = process.stdout.read(content_length).decode('utf-8')
                if not body: continue
                
                response = json.loads(body)
                
                # Notify callbacks
                callbacks = self.output_callbacks.get(server_id, [])
                for cb in callbacks:
                    try:
                        cb(response)
                    except: pass
                    
            except Exception as e:
                logger.debug(f"LSP Output Read Error: {e}")
                break
