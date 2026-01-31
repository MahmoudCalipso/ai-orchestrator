"""
Async Subprocess Utilities
Non-blocking execution of system commands.
"""
import asyncio
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)

async def run_command_async(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: int = 60
) -> Tuple[int, str, str]:
    """
    Execute a system command asynchronously.
    Returns: (returncode, stdout, stderr)
    """
    logger.debug(f"Executing async command: {' '.join(cmd)} (cwd: {cwd})")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return process.returncode, stdout.decode().strip(), stderr.decode().strip()
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            logger.error(f"Command timed out: {' '.join(cmd)}")
            return -1, "", "Command timed out"
            
    except Exception as e:
        logger.error(f"Failed to execute command {' '.join(cmd)}: {e}")
        return -1, "", str(e)
