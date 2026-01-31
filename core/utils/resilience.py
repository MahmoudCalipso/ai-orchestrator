import asyncio
import functools
import logging
import time
from typing import Callable, Any, Type, Tuple, Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerError(Exception):
    """Exception raised when the circuit is open"""
    pass

def retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt >= retries:
                        logger.error(f"Retry failed after {retries} attempts for {func.__name__}: {e}")
                        break
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{retries + 1} failed for {func.__name__}. "
                        f"Retrying in {current_delay:.2f}s... Error: {e}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Simple Circuit Breaker for managing service reliability.
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        async with self._lock:
            await self._before_call()

        try:
            result = await func(*args, **kwargs)
            
            async with self._lock:
                await self._on_success()
            return result
        except Exception as e:
            async with self._lock:
                await self._on_failure()
            raise e

    async def _before_call(self):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info(f"Circuit Breaker '{self.name}' moved to HALF-OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError(f"Circuit Breaker '{self.name}' is OPEN")

    async def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit Breaker '{self.name}' recovered and CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    async def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.error(f"Circuit Breaker '{self.name}' is now OPEN (threshold {self.failure_threshold} reached)")
            self.state = CircuitState.OPEN

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0
):
    """
    Circuit breaker decorator.
    Maintains a single instance of CircuitBreaker per decorated function.
    """
    breakers: Dict[str, CircuitBreaker] = {}

    def decorator(func: Callable):
        func_name = f"{func.__module__}.{func.__name__}"
        if func_name not in breakers:
            breakers[func_name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                name=func_name
            )
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await breakers[func_name].call(func, *args, **kwargs)
        return wrapper
    return decorator
