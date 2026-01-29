"""Military-grade resilience with Circuit Breakers & Multi-Provider Failover."""
import asyncio
import time
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal
    OPEN = "open"          # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreakerOpen(Exception):
    """Raised when the circuit is in OPEN state."""
    pass

class CircuitBreaker:
    """Implement V2.0 State Machine: CLOSED -> OPEN -> HALF_OPEN."""
    
    def __init__(self, name: str, threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = threshold
        self.recovery_timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self._lock = asyncio.Lock()
        # V2.0 requirement: Half-open state tests with 3 probe requests
        self._probe_count = 0 
        self._required_probes = 3

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        # Check current state
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                async with self._lock:
                    self.state = CircuitState.HALF_OPEN
                    self._probe_count = 0
                    logger.info(f"Circuit {self.name} moving to HALF_OPEN (Testing recovery)")
            else:
                raise CircuitBreakerOpen(f"{self.name} circuit OPEN")

        try:
            # V2.0 Requirement: 30-second timeout on ALL LLM calls
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=30)
            await self._on_success()
            return result
        except asyncio.TimeoutError:
            await self._on_failure("timeout")
            raise HTTPException(504, f"{self.name} request timed out")
        except Exception as e:
            await self._on_failure(str(e))
            raise

    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self._probe_count += 1
                if self._probe_count >= self._required_probes:
                    self.state = CircuitState.CLOSED
                    self.failures = 0
                    logger.info(f"Circuit {self.name} successfully recovered and is now CLOSED")
            elif self.state == CircuitState.CLOSED:
                self.failures = 0

    async def _on_failure(self, reason: str):
        async with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            logger.warning(f"Circuit {self.name} failure: {reason}. Count: {self.failures}")
            
            if self.state == CircuitState.HALF_OPEN:
                # Any failure in HALF_OPEN immediately re-opens the circuit
                self.state = CircuitState.OPEN
            elif self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(f"Circuit {self.name} is now OPEN. Refusing requests until recovery.")

class MultiProviderLLM:
    """Enterprise Failover: OpenAI -> Anthropic -> Azure."""
    
    def __init__(self):
        # Priority mapping from spec
        self.breakers = {
            'openai': CircuitBreaker("openai", timeout=60),
            'anthropic': CircuitBreaker("anthropic", timeout=60),
            'azure': CircuitBreaker("azure", timeout=60)
        }
        self.priorities = ['openai', 'anthropic', 'azure']

    async def generate_with_failover(self, prompt: str, primary: str = 'openai', **kwargs):
        """Execute with automatic failover across providers."""
        errors = []
        
        # Determine sequence starting with primary
        sequence = [primary] + [p for p in self.priorities if p != primary]
        
        for provider_name in sequence:
            breaker = self.breakers.get(provider_name)
            if not breaker: continue
            
            try:
                # In a real impl, self._execute would route to the specific client
                return await breaker.call(self._execute_provider, provider_name, prompt, **kwargs)
            except (CircuitBreakerOpen, Exception) as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                errors.append(f"{provider_name}: {str(e)}")
                continue # Try next provider
        
        raise HTTPException(503, f"All LLM providers failed: {'; '.join(errors)}")

    async def _execute_provider(self, name: str, prompt: str, **kwargs):
        """Simplified mock for provider execution logic."""
        # This is where LangChain or direct API calls would go
        await asyncio.sleep(0.1) # Simulate network
        return {"provider": name, "result": "V2.0 Processed Output"}

# Global singleton
resilience_manager = MultiProviderLLM()
