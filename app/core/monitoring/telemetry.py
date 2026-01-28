"""OpenTelemetry integration for tracing and metrics."""
import logging
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import os

logger = logging.getLogger(__name__)

def setup_telemetry(app):
    """Initializes tracing and metrics for the application."""
    
    # Trace Provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # OTLP Exporter (Jaeger/Tempo)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317")
    try:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Auto-Instrumentation
        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()
        
        logger.info(f"OpenTelemetry instrumentation enabled, exporting to {otlp_endpoint}")
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
    
    return tracer

# Global tracer access
tracer = trace.get_tracer("ai-orchestrator")
