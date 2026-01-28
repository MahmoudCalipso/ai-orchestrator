"""Prevents cascade failures when LLM APIs are down."""
import asyncio
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Implements the circuit breaker pattern for external service calls."""
    
    def __init__(
        self, 
        name: str = "default",
        failure_threshold: int = 5, 
        recovery_timeout: int = 60
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executes a function through the circuit breaker."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_retry():
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit {self.name} moving to HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker {self.name} is OPEN. Failure count: {self.failure_count}")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit {self.name} successfully recovered and is now CLOSED")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure = datetime.utcnow()
            logger.warning(f"Circuit {self.name} failure reported. Count: {self.failure_count}")
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(f"Circuit {self.name} is now OPEN. Threshold of {self.failure_threshold} reached")
    
    def _should_retry(self) -> bool:
        """Checks if enough time has passed to attempt a recovery."""
        if not self.last_failure:
            return True
        return datetime.utcnow() - self.last_failure > timedelta(seconds=self.recovery_timeout)

# Shared circuit breakers for common services
llm_breaker = CircuitBreaker(name="llm_api")
db_breaker = CircuitBreaker(name="database")
