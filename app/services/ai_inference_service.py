"""Optimized AI inference service with request batching."""
from collections import deque
import asyncio
import httpx
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIInferenceService:
    """Manages LLM inference with request batching and throughput optimization."""
    
    def __init__(self, max_batch_size: int = 10, batch_timeout: float = 0.1):
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests = deque()
        self._batch_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Starts the background batch processor."""
        if self._running:
            return
        self._running = True
        self._batch_task = asyncio.create_task(self._process_loop())
        logger.info("AIInferenceService batch processor started")
    
    async def stop(self):
        """Stops the batch processor and flushes pending requests."""
        self._running = False
        if self._batch_task:
            self._batch_task.cancel()
        logger.info("AIInferenceService stopped")
    
    async def infer(self, prompt: str, model: str = "gpt-4o") -> str:
        """Enqueues an inference request and waits for the result."""
        future = asyncio.Future()
        self.pending_requests.append({
            "prompt": prompt,
            "model": model,
            "future": future,
            "timestamp": time.time()
        })
        return await future
    
    async def _process_loop(self):
        """Background loop to process batches."""
        while self._running:
            try:
                if len(self.pending_requests) >= self.max_batch_size:
                    await self._process_batch()
                else:
                    await asyncio.sleep(self.batch_timeout)
                    if self.pending_requests:
                        await self._process_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in inference batch processor: {e}")
                await asyncio.sleep(1) # Backoff
    
    async def _process_batch(self):
        """Collects and executes a batch of requests."""
        batch = []
        while self.pending_requests and len(batch) < self.max_batch_size:
            batch.append(self.pending_requests.popleft())
        
        if not batch:
            return
        
        # In a real implementation, this would call a batch-supported endpoint
        # or execute multiple requests concurrently using gather.
        prompts = [req["prompt"] for req in batch]
        model = batch[0]["model"] # Assume same model for batch for simplicity
        
        logger.info(f"Processing batch of {len(batch)} requests for model {model}")
        
        try:
            # Placeholder for actual LLM API call
            results = await self._execute_inference(prompts, model)
            for req, result in zip(batch, results):
                if not req["future"].done():
                    req["future"].set_result(result)
        except Exception as e:
            for req in batch:
                if not req["future"].done():
                    req["future"].set_exception(e)
    
    async def _execute_inference(self, prompts: List[str], model: str) -> List[str]:
        """Simulates parallel inference calls."""
        # This would be replaced with actual LangChain or OpenAI calls
        # For now, we simulate concurrent execution
        tasks = [self._mock_api_call(p, model) for p in prompts]
        return await asyncio.gather(*tasks)
    
    async def _mock_api_call(self, prompt: str, model: str) -> str:
        """Mock LLM response for testing purposes."""
        await asyncio.sleep(1.5) # Simulate latency
        return f"AI Response to: {prompt[:20]}... [via {model}]"

class StreamingOptimizer:
    """Buffers streaming responses to improve network efficiency."""
    
    @staticmethod
    async def stream_with_buffering(
        stream_source: Any,
        buffer_size: int = 10,
        flush_interval: float = 0.05
    ):
        """Buffers chunks and flushes them periodically."""
        buffer = []
        last_flush = time.time()
        
        async for chunk in stream_source:
            buffer.append(chunk)
            
            # Flush if buffer is full or time has passed
            if len(buffer) >= buffer_size or (time.time() - last_flush) > flush_interval:
                yield "".join(buffer)
                buffer.clear()
                last_flush = time.time()
        
        # Final flush
        if buffer:
            yield "".join(buffer)

ai_inference = AIInferenceService()
