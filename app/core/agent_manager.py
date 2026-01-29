"""Agent lifecycle management with TTL cleanup."""
import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from cachetools import TTLCache

logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    session_id: str
    user_id: str
    agent_type: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    llm_chain: Any = None
    memory: Any = None
    websocket_connections: set = field(default_factory=set)
    
    def touch(self):
        self.last_activity = datetime.utcnow()

class AgentManager:
    """Manages agent sessions with automatic cleanup to prevent memory leaks."""
    
    def __init__(self, session_ttl: int = 3600, max_sessions: int = 10000):
        self.session_ttl = session_ttl
        self.max_sessions = max_sessions
        # Initialize TTLCache - cachetools will handle TTL expiration
        self._sessions: TTLCache = TTLCache(maxsize=max_sessions, ttl=session_ttl)
        self._cleanup_task = None
        self._running = False
        
    async def start(self):
        if self._running:
            return
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"AgentManager started (TTL: {self.session_ttl}s, Max: {self.max_sessions})")
        
    async def stop(self):
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        for sid in list(self._sessions.keys()):
            await self.destroy_session(sid)
        logger.info("AgentManager stopped")
    
    async def create_session(self, user_id: str, agent_type: str = "default") -> str:
        if len(self._sessions) >= self.max_sessions:
            raise RuntimeError("Max sessions reached")
        
        session_id = str(uuid.uuid4())
        context = AgentContext(session_id=session_id, user_id=user_id, agent_type=agent_type)
        
        await self._init_agent(context)
        self._sessions[session_id] = context
        logger.info(f"Created agent session {session_id} for user {user_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[AgentContext]:
        context = self._sessions.get(session_id)
        if context:
            context.touch()
        return context
    
    async def destroy_session(self, session_id: str):
        context = self._sessions.get(session_id)
        if not context:
            return False
        del self._sessions[session_id]
        await self._cleanup_resources(context)
        logger.info(f"Destroyed agent session {session_id}")
        return True
    
    async def _init_agent(self, context: AgentContext):
        """Initialize LangChain components for the agent."""
        try:
            from langchain.memory import ConversationBufferWindowMemory
            from langchain_openai import ChatOpenAI
            # Using gpt-4o as default as per spec
            context.llm_chain = ChatOpenAI(model="gpt-4o", temperature=0.7)
            context.memory = ConversationBufferWindowMemory(k=10)
        except ImportError:
            logger.warning("LangChain components not found, agent will have limited functionality")
            pass
    
    async def _cleanup_resources(self, context: AgentContext):
        """Explicitly clear memory, close WebSockets, and purge references."""
        # 1. Force close all Associated WebSockets (code 1001 = going away)
        if context.websocket_connections:
            await asyncio.gather(
                *[ws.close(code=1001) for ws in context.websocket_connections],
                return_exceptions=True
            )
            context.websocket_connections.clear()

        # 2. Clear LangChain memory
        if context.memory and hasattr(context.memory, 'clear'):
            context.memory.clear()
        
        context.llm_chain = None
        context.memory = None
    
    async def _cleanup_loop(self):
        """Background loop pruning stale sessions every 300s."""
        while self._running:
            try:
                # TTLCache handles removal automatically on access,
                # but we force explicit cleanup/pruning for memory safety.
                expired = []
                current_time = datetime.utcnow()
                
                for sid, context in list(self._sessions.items()):
                    delta = (current_time - context.last_activity).total_seconds()
                    if delta > self.session_ttl:
                        expired.append(sid)
                
                for sid in expired:
                    logger.info(f"Pruning stale session {sid}")
                    await self.destroy_session(sid)
                
                await asyncio.sleep(300) # Task requirement: 300s
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in agent cleanup loop: {e}")

agent_manager = AgentManager()
