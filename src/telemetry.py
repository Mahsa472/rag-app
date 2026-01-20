import os
from opentelemetry import metrics, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from prometheus_client import start_http_server

resource = Resource.create({"service.name": "rag2-app"})

prometheus_reader = PrometheusMetricReader()
metrics_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
metrics.set_meter_provider(metrics_provider)

meter = metrics.get_meter(__name__)

questions_total = meter.create_counter(
    name="rag_questions_total",
    description="Total number of questions asked",
)

retrieval_latency = meter.create_histogram(
    name="rag_retrieval_latency_seconds",
    description="Latency of the retrieval process",
    unit="s",
)

retrieval_chunks = meter.create_histogram(
    name="rag_retrieval_chunks",
    description="Number of chunks retrieved for a question",
)

llm_latency = meter.create_histogram(
    name="rag_llm_latency_seconds",
    description="Latency of the LLM call",
    unit="s",
)

tokens_in = meter.create_counter(
    name="llm_tokens_input_total",
    description="Total number of tokens input to the LLM",
)

tokens_out = meter.create_counter(
    name="llm_tokens_output_total",
    description="Total number of tokens output from the LLM",
)

def initialize_telemetry(app):
    FlaskInstrumentor().instrument_app(app)
    print(f"OpenTelemetry metrics are available at http://localhost:8000/metrics")
