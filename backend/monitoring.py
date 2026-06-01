"""
Prometheus metrics and monitoring for the research agent.

Tracks: API latency, error rates, task metrics, resource usage.
"""

from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, REGISTRY
)
from typing import Callable, Any
import time
import logging

logger = logging.getLogger(__name__)


# Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Research task metrics
research_tasks_total = Counter(
    "research_tasks_total",
    "Total research tasks",
    ["status"]
)

research_task_duration_seconds = Histogram(
    "research_task_duration_seconds",
    "Research task duration",
    buckets=(1, 5, 10, 30, 60, 300, 600, 1800)
)

research_sources_found = Counter(
    "research_sources_found_total",
    "Total sources found"
)

research_findings_generated = Counter(
    "research_findings_generated_total",
    "Total findings generated"
)

# Error metrics
errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "endpoint"]
)

# API authentication metrics
auth_attempts_total = Counter(
    "auth_attempts_total",
    "Total authentication attempts",
    ["result"]  # success, failure
)

auth_token_created_total = Counter(
    "auth_tokens_created_total",
    "Total tokens created"
)

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Rate limit exceeded count",
    ["endpoint"]
)

# Webhook metrics
webhooks_delivered_total = Counter(
    "webhooks_delivered_total",
    "Total webhooks delivered",
    ["status"]  # success, failed
)

webhook_delivery_duration_seconds = Histogram(
    "webhook_delivery_duration_seconds",
    "Webhook delivery duration",
    buckets=(0.1, 0.5, 1, 2, 5, 10)
)

# System metrics
active_tasks = Gauge(
    "active_tasks",
    "Number of active research tasks"
)

connected_users = Gauge(
    "connected_users",
    "Number of connected users"
)

database_connections = Gauge(
    "database_connections",
    "Number of database connections"
)


def record_http_request(
    method: str,
    endpoint: str,
    status: int,
    duration: float
):
    """Record HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def record_research_task(
    status: str,
    duration: float,
    sources_found: int,
    findings_count: int
):
    """Record research task completion metrics."""
    research_tasks_total.labels(status=status).inc()
    research_task_duration_seconds.observe(duration)
    research_sources_found.inc(sources_found)
    research_findings_generated.inc(findings_count)


def record_error(error_type: str, endpoint: str):
    """Record error."""
    errors_total.labels(error_type=error_type, endpoint=endpoint).inc()


def record_auth_attempt(success: bool):
    """Record authentication attempt."""
    result = "success" if success else "failure"
    auth_attempts_total.labels(result=result).inc()


def record_auth_token_created():
    """Record token creation."""
    auth_token_created_total.inc()


def record_rate_limit(endpoint: str):
    """Record rate limit exceeded."""
    rate_limit_exceeded_total.labels(endpoint=endpoint).inc()


def record_webhook_delivery(success: bool, duration: float):
    """Record webhook delivery."""
    status = "success" if success else "failed"
    webhooks_delivered_total.labels(status=status).inc()
    webhook_delivery_duration_seconds.observe(duration)


def set_active_tasks(count: int):
    """Set active task count."""
    active_tasks.set(count)


def set_connected_users(count: int):
    """Set connected user count."""
    connected_users.set(count)


def set_database_connections(count: int):
    """Set database connection count."""
    database_connections.set(count)


def get_metrics() -> bytes:
    """Get Prometheus metrics."""
    return generate_latest(REGISTRY)


class MetricsMiddleware:
    """Middleware for recording HTTP metrics."""

    def __init__(self, app):
        """Initialize metrics middleware."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process request and record metrics."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        start_time = time.time()
        status_code = 500  # Default to error

        async def send_wrapper(message):
            """Wrap send to capture status code."""
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            logger.error(f"Request error: {e}")
            record_error(str(type(e).__name__), path)
            raise
        finally:
            duration = time.time() - start_time
            record_http_request(method, path, status_code, duration)


class GrafanaDashboardConfig:
    """Grafana dashboard configuration."""

    @staticmethod
    def get_dashboard_json() -> dict:
        """Get Grafana dashboard JSON configuration."""
        return {
            "dashboard": {
                "title": "Autonomous Research Agent",
                "description": "Monitoring dashboard for research tasks",
                "tags": ["research", "monitoring"],
                "timezone": "utc",
                "panels": [
                    {
                        "title": "HTTP Requests (5m)",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])"
                            }
                        ],
                    },
                    {
                        "title": "Request Latency P95",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                            }
                        ],
                    },
                    {
                        "title": "Active Tasks",
                        "targets": [
                            {
                                "expr": "active_tasks"
                            }
                        ],
                    },
                    {
                        "title": "Task Completion Rate",
                        "targets": [
                            {
                                "expr": "rate(research_tasks_total{status=\"completed\"}[1h])"
                            }
                        ],
                    },
                    {
                        "title": "Error Rate",
                        "targets": [
                            {
                                "expr": "rate(errors_total[5m])"
                            }
                        ],
                    },
                    {
                        "title": "Webhook Delivery Success Rate",
                        "targets": [
                            {
                                "expr": "rate(webhooks_delivered_total{status=\"success\"}[1h]) / rate(webhooks_delivered_total[1h])"
                            }
                        ],
                    },
                    {
                        "title": "Average Task Duration",
                        "targets": [
                            {
                                "expr": "avg(research_task_duration_seconds)"
                            }
                        ],
                    },
                    {
                        "title": "Sources Found (1h)",
                        "targets": [
                            {
                                "expr": "increase(research_sources_found_total[1h])"
                            }
                        ],
                    },
                ],
                "refresh": "30s",
                "time": {
                    "from": "now-6h",
                    "to": "now",
                },
            }
        }


# Alert rules for Prometheus
ALERT_RULES = """
groups:
  - name: research_agent_alerts
    interval: 1m
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "P95 latency is {{ $value | humanizeDuration }}"

      - alert: LowWebhookDeliveryRate
        expr: rate(webhooks_delivered_total{status="success"}[1h]) / rate(webhooks_delivered_total[1h]) < 0.95
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Low webhook delivery success rate"
          description: "Success rate is {{ $value | humanizePercentage }}"

      - alert: RateLimitExceeded
        expr: rate(rate_limit_exceeded_total[5m]) > 0
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "Rate limit exceeded"
          description: "Rate limit exceeded on {{ $labels.endpoint }}"
"""
