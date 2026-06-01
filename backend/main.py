import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.models.database import init_db
from backend.api.routes import router
from backend.api.auth_routes import router as auth_router
from backend.api.webhooks_routes import webhook_router, analytics_router
from backend.logging_config import get_logger
from backend.waf import WAFMiddleware
from backend.monitoring import MetricsMiddleware, get_metrics, record_rate_limit
from prometheus_client import CONTENT_TYPE_LATEST

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Autonomous Research Agent API")
    init_db()
    yield
    logger.info("Shutting down Autonomous Research Agent API")


app = FastAPI(
    title="Autonomous Research Agent API",
    description="A multi-agent research system that searches, analyzes, and generates reports",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    record_rate_limit(request.url.path)
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add WAF middleware
app.add_middleware(WAFMiddleware)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Completed {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {process_time:.2f}s"
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(router)
app.include_router(auth_router)
app.include_router(webhook_router)
app.include_router(analytics_router)


@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    logger.debug("Health check request")
    return {"status": "ok", "service": "autonomous-research-agent"}
