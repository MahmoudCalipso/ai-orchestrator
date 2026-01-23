"""
Asynchronous Message Bus
Decouples agents and services using a lightweight internal Pub/Sub system.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from collections import defaultdict

logger = logging.getLogger(__name__)

class MessageBus:
    """Lightweight event bus and message queue for asynchronous coordination"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MessageBus, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = defaultdict(list)
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self._initialized = True
        self._worker_task: Optional[asyncio.Task] = None
        logger.info("MessageBus initialized")

    async def start(self):
        """Start the background task worker"""
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._process_queue())
            logger.info("MessageBus Background Worker started")

    async def stop(self):
        """Stop the background task worker"""
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Subscribe a handler to a specific topic"""
        self.subscribers[topic].append(handler)
        logger.info(f"Subscribed handler to topic: {topic}")

    async def publish(self, topic: str, data: Dict[str, Any]):
        """Publish a message to a topic (Fire-and-forget for handlers)"""
        logger.info(f"Publishing to {topic}: {str(data)[:100]}...")
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                # Non-blocking invocation of handlers
                asyncio.create_task(handler(data))

    async def enqueue_task(self, task_type: str, payload: Dict[str, Any]):
        """Add a long-running task to the background queue"""
        await self.task_queue.put({"type": task_type, "payload": payload})
        logger.info(f"Task enqueued: {task_type}")

    async def _process_queue(self):
        """Infinite loop to process background tasks"""
        while True:
            try:
                task = await self.task_queue.get()
                logger.info(f"Processing background task: {task['type']}")
                
                # In a real system, we'd route this to a specific Worker class
                # For this implementation, we broadcast it to a special "worker_topic"
                await self.publish(f"worker:{task['type']}", task["payload"])
                
                self.task_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"MessageBus worker error: {e}")
                await asyncio.sleep(1) # Backoff
