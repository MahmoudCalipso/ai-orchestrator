"""
Prometheus Metrics Integration
Advanced monitoring and observability
"""
import time
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Comprehensive Prometheus metrics for AI Orchestrator"""

    def __init__(self):
        self.registry = CollectorRegistry()

        # Request metrics
        self.request_total = Counter(
            'orchestrator_requests_total',
            'Total number of inference requests',
            ['model', 'task_type', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'orchestrator_request_duration_seconds',
            'Request processing duration',
            ['model', 'task_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )

        self.tokens_generated = Counter(
            'orchestrator_tokens_generated_total',
            'Total tokens generated',
            ['model'],
            registry=self.registry
        )

        # Model metrics
        self.models_loaded = Gauge(
            'orchestrator_models_loaded',
            'Number of currently loaded models',
            registry=self.registry
        )

        self.model_load_duration = Histogram(
            'orchestrator_model_load_duration_seconds',
            'Model loading duration',
            ['model'],
            buckets=[1, 5, 10, 30, 60, 120],
            registry=self.registry
        )

        # Runtime metrics
        self.runtime_health = Gauge(
            'orchestrator_runtime_health',
            'Runtime health status (1=healthy, 0=unhealthy)',
            ['runtime'],
            registry=self.registry
        )

        self.runtime_active_requests = Gauge(
            'orchestrator_runtime_active_requests',
            'Number of active requests per runtime',
            ['runtime'],
            registry=self.registry
        )

        # Resource metrics
        self.gpu_utilization = Gauge(
            'orchestrator_gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu_id', 'gpu_name'],
            registry=self.registry
        )

        self.gpu_memory_used = Gauge(
            'orchestrator_gpu_memory_used_bytes',
            'GPU memory used in bytes',
            ['gpu_id', 'gpu_name'],
            registry=self.registry
        )

        self.cpu_utilization = Gauge(
            'orchestrator_cpu_utilization_percent',
            'CPU utilization percentage',
            registry=self.registry
        )

        self.memory_utilization = Gauge(
            'orchestrator_memory_utilization_percent',
            'Memory utilization percentage',
            registry=self.registry
        )

        # Error metrics
        self.errors_total = Counter(
            'orchestrator_errors_total',
            'Total number of errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        # Queue metrics
        self.queue_length = Gauge(
            'orchestrator_queue_length',
            'Number of requests in queue',
            registry=self.registry
        )

        self.queue_wait_time = Summary(
            'orchestrator_queue_wait_seconds',
            'Time requests spend in queue',
            registry=self.registry
        )

        # Migration metrics
        self.migrations_total = Counter(
            'orchestrator_migrations_total',
            'Total number of task migrations',
            ['from_model', 'to_model', 'status'],
            registry=self.registry
        )

        # Cache metrics
        self.cache_hits = Counter(
            'orchestrator_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_misses = Counter(
            'orchestrator_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )

    def track_request(self, model: str, task_type: str, status: str, duration: float, tokens: int):
        """Track an inference request"""
        self.request_total.labels(model=model, task_type=task_type, status=status).inc()
        self.request_duration.labels(model=model, task_type=task_type).observe(duration)
        self.tokens_generated.labels(model=model).inc(tokens)

    def update_models_loaded(self, count: int):
        """Update loaded models count"""
        self.models_loaded.set(count)

    def track_model_load(self, model: str, duration: float):
        """Track model loading"""
        self.model_load_duration.labels(model=model).observe(duration)

    def update_runtime_health(self, runtime: str, is_healthy: bool):
        """Update runtime health status"""
        self.runtime_health.labels(runtime=runtime).set(1 if is_healthy else 0)

    def update_gpu_metrics(self, gpu_id: str, gpu_name: str, utilization: float, memory_used: int):
        """Update GPU metrics"""
        self.gpu_utilization.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(utilization)
        self.gpu_memory_used.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(memory_used * 1024 * 1024)  # MB to bytes

    def update_system_metrics(self, cpu_percent: float, memory_percent: float):
        """Update system resource metrics"""
        self.cpu_utilization.set(cpu_percent)
        self.memory_utilization.set(memory_percent)

    def track_error(self, error_type: str, component: str):
        """Track an error"""
        self.errors_total.labels(error_type=error_type, component=component).inc()

    def update_queue_metrics(self, length: int):
        """Update queue length"""
        self.queue_length.set(length)

    def track_queue_wait(self, wait_time: float):
        """Track queue wait time"""
        self.queue_wait_time.observe(wait_time)

    def track_migration(self, from_model: str, to_model: str, status: str):
        """Track a migration"""
        self.migrations_total.labels(from_model=from_model, to_model=to_model, status=status).inc()

    def track_cache_hit(self, cache_type: str):
        """Track cache hit"""
        self.cache_hits.labels(cache_type=cache_type).inc()

    def track_cache_miss(self, cache_type: str):
        """Track cache miss"""
        self.cache_misses.labels(cache_type=cache_type).inc()

    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get content type for metrics"""
        return CONTENT_TYPE_LATEST


# Decorator for tracking function execution
def track_execution(metrics: PrometheusMetrics, component: str):
    """Decorator to track function execution time and errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                return result
            except Exception as e:
                metrics.track_error(type(e).__name__, component)
                raise
        return wrapper
    return decorator


# Global metrics instance
_metrics_instance = None


def get_metrics() -> PrometheusMetrics:
    """Get global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PrometheusMetrics()
    return _metrics_instance