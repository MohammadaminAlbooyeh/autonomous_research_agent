"""
API routes for webhooks and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from backend.webhooks import get_webhook_manager, WebhookEventType
from backend.analytics import get_analytics
from backend.auth import get_current_user
from backend.logging_config import get_logger

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

# Pydantic models
class WebhookSubscriptionCreate(BaseModel):
    """Create webhook subscription request."""
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None


class WebhookSubscriptionResponse(BaseModel):
    """Webhook subscription response."""
    id: str
    url: str
    events: List[str]
    active: bool
    created_at: str
    delivery_count: int
    failed_count: int


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery response."""
    id: str
    url: str
    event: str
    status: str
    attempt: int
    created_at: str


class AnalyticsResponse(BaseModel):
    """Analytics response."""
    period_hours: int
    tasks_created: int
    tasks_completed: int
    tasks_failed: int
    completion_rate: float
    avg_completion_time_seconds: float
    total_findings: int
    total_sources: int
    unique_users: int


# Webhook routes
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@webhook_router.post("/subscriptions", response_model=WebhookSubscriptionResponse)
@limiter.limit("5/minute")
def create_webhook(
    request: Request,
    subscription: WebhookSubscriptionCreate,
    current_user: str = Depends(get_current_user)
):
    """Create webhook subscription."""
    logger.info(f"User {current_user} creating webhook subscription for {subscription.url}")
    
    manager = get_webhook_manager()
    sub = manager.create_subscription(
        url=str(subscription.url),
        events=subscription.events,
        secret=subscription.secret
    )
    
    return WebhookSubscriptionResponse(
        id=sub["id"],
        url=sub["url"],
        events=sub["events"],
        active=sub["active"],
        created_at=sub["created_at"],
        delivery_count=sub["delivery_count"],
        failed_count=sub["failed_count"]
    )


@webhook_router.get("/subscriptions", response_model=List[WebhookSubscriptionResponse])
@limiter.limit("10/minute")
def list_webhooks(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """List webhook subscriptions."""
    logger.info(f"User {current_user} listing webhooks")
    
    manager = get_webhook_manager()
    subscriptions = list(manager.subscriptions.values())
    
    return [
        WebhookSubscriptionResponse(
            id=sub["id"],
            url=sub["url"],
            events=sub["events"],
            active=sub["active"],
            created_at=sub["created_at"],
            delivery_count=sub["delivery_count"],
            failed_count=sub["failed_count"]
        )
        for sub in subscriptions
    ]


@webhook_router.get("/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse)
@limiter.limit("10/minute")
def get_webhook(
    request: Request,
    subscription_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get webhook subscription details."""
    manager = get_webhook_manager()
    sub = manager.subscriptions.get(subscription_id)
    
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return WebhookSubscriptionResponse(
        id=sub["id"],
        url=sub["url"],
        events=sub["events"],
        active=sub["active"],
        created_at=sub["created_at"],
        delivery_count=sub["delivery_count"],
        failed_count=sub["failed_count"]
    )


@webhook_router.put("/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse)
@limiter.limit("5/minute")
def update_webhook(
    request: Request,
    subscription_id: str,
    active: Optional[bool] = None,
    events: Optional[List[str]] = None,
    current_user: str = Depends(get_current_user)
):
    """Update webhook subscription."""
    logger.info(f"User {current_user} updating webhook {subscription_id}")
    
    manager = get_webhook_manager()
    updates = {}
    if active is not None:
        updates["active"] = active
    if events is not None:
        updates["events"] = events
    
    sub = manager.update_subscription(subscription_id, **updates)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return WebhookSubscriptionResponse(
        id=sub["id"],
        url=sub["url"],
        events=sub["events"],
        active=sub["active"],
        created_at=sub["created_at"],
        delivery_count=sub["delivery_count"],
        failed_count=sub["failed_count"]
    )


@webhook_router.delete("/subscriptions/{subscription_id}")
@limiter.limit("5/minute")
def delete_webhook(
    request: Request,
    subscription_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete webhook subscription."""
    logger.info(f"User {current_user} deleting webhook {subscription_id}")
    
    manager = get_webhook_manager()
    if not manager.delete_subscription(subscription_id):
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"detail": "Webhook subscription deleted"}


@webhook_router.get("/deliveries", response_model=List[WebhookDeliveryResponse])
@limiter.limit("10/minute")
def get_deliveries(
    request: Request,
    subscription_id: Optional[str] = None,
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get webhook delivery history."""
    manager = get_webhook_manager()
    deliveries = manager.get_delivery_history(subscription_id, limit)
    
    return [
        WebhookDeliveryResponse(
            id=d["id"],
            url=d["url"],
            event=d["payload"]["event"],
            status=d["status"],
            attempt=d["attempt"],
            created_at=d["created_at"]
        )
        for d in deliveries
    ]


# Analytics routes
analytics_router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@analytics_router.get("/summary", response_model=AnalyticsResponse)
@limiter.limit("10/minute")
def get_analytics_summary(
    request: Request,
    hours: int = 24
):
    """Get analytics summary."""
    logger.info(f"Analytics summary requested for {hours} hours")
    
    analytics = get_analytics()
    stats = analytics.get_summary_stats(hours)
    
    return AnalyticsResponse(
        period_hours=stats["period_hours"],
        tasks_created=stats["tasks_created"],
        tasks_completed=stats["tasks_completed"],
        tasks_failed=stats["tasks_failed"],
        completion_rate=stats["completion_rate"],
        avg_completion_time_seconds=stats["avg_completion_time_seconds"],
        total_findings=stats["total_findings"],
        total_sources=stats["total_sources"],
        unique_users=stats["unique_users"]
    )


@analytics_router.get("/topics")
@limiter.limit("10/minute")
def get_popular_topics(
    request: Request,
    limit: int = 10,
    hours: int = 24
):
    """Get popular research topics."""
    analytics = get_analytics()
    topics = analytics.get_popular_topics(limit, hours)
    return {"topics": topics}


@analytics_router.get("/depth-distribution")
@limiter.limit("10/minute")
def get_depth_distribution(
    request: Request,
    hours: int = 24
):
    """Get research depth distribution."""
    analytics = get_analytics()
    distribution = analytics.get_depth_distribution(hours)
    return {"distribution": distribution}


@analytics_router.get("/user-activity")
@limiter.limit("10/minute")
def get_user_activity(
    request: Request,
    hours: int = 24
):
    """Get user activity metrics."""
    analytics = get_analytics()
    activity = analytics.get_user_activity(hours)
    return {"activity": activity}


@analytics_router.get("/performance-trends")
@limiter.limit("10/minute")
def get_performance_trends(
    request: Request,
    hours: int = 24,
    interval_minutes: int = 60
):
    """Get performance trends."""
    analytics = get_analytics()
    trends = analytics.get_performance_trends(hours, interval_minutes)
    return {"trends": trends}


@analytics_router.get("/export")
@limiter.limit("5/minute")
def export_analytics(
    request: Request,
):
    """Export all analytics data."""
    logger.info("Analytics export requested")
    
    analytics = get_analytics()
    return analytics.export_metrics()
