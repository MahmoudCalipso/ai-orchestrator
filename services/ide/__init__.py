"""
IDE module initialization
"""
from .editor import EditorService, LSPManager
from .terminal import TerminalService
from .debugger import DebuggerService

__all__ = ['EditorService', 'LSPManager', 'TerminalService', 'DebuggerService']
