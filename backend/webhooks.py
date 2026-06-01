"""
Webhook system for research task events.

Supports event subscriptions, delivery, retries, and verification.
"""

import uuid
import hmac
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
import logging

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """Types of webhook events."""
    RESEARCH_STARTED = "research.started"
    RESEARCH_COMPLETED = "research.completed"
    RESEARCH_FAILED = "research.failed"
    RESEARCH_PROGRESS = "research.progress"


class WebhookDeliveryStatus(str, Enum):
    """Status of webhook delivery attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookManager:
    """Manage webhook subscriptions and deliveries."""

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 60

    def __init__(self):
        """Initialize webhook manager."""
        # In-memory storage (replace with database in production)
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.deliveries: Dict[str, Dict[str, Any]] = {}
        self.http_client = None

    async def get_http_client(self):
        """Get or create async HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client

    def create_subscription(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        active: bool = True
    ) -> Dict[str, Any]:
        """
        Create new webhook subscription.
        
        Args:
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret: Secret for HMAC signing
            active: Whether subscription is active
            
        Returns:
            Subscription object
        """
        subscription_id = str(uuid.uuid4())
        
        if not secret:
            secret = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        
        subscription = {
            "id": subscription_id,
            "url": url,
            "events": events,
            "secret": secret,
            "active": active,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_delivery_at": None,
            "delivery_count": 0,
            "failed_count": 0,
        }
        
        self.subscriptions[subscription_id] = subscription
        logger.info(f"Created webhook subscription {subscription_id} for {url}")
        
        return subscription

    def get_subscriptions(self, event_type: str) -> List[Dict[str, Any]]:
        """Get active subscriptions for event type."""
        return [
            sub for sub in self.subscriptions.values()
            if sub["active"] and event_type in sub["events"]
        ]

    async def trigger_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """
        Trigger webhook event to all subscribed endpoints.
        
        Args:
            event_type: Type of event
            data: Event payload
            
        Returns:
            List of delivery IDs
        """
        subscriptions = self.get_subscriptions(event_type)
        delivery_ids = []
        
        for subscription in subscriptions:
            delivery_id = await self._queue_delivery(
                subscription_id=subscription["id"],
                event_type=event_type,
                data=data,
                url=subscription["url"],
                secret=subscription["secret"]
            )
            delivery_ids.append(delivery_id)
        
        return delivery_ids

    async def _queue_delivery(
        self,
        subscription_id: str,
        event_type: str,
        data: Dict[str, Any],
        url: str,
        secret: str
    ) -> str:
        """Queue webhook delivery."""
        delivery_id = str(uuid.uuid4())
        
        payload = {
            "id": delivery_id,
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        # Calculate signature
        signature = self._calculate_signature(json.dumps(payload), secret)
        
        delivery = {
            "id": delivery_id,
            "subscription_id": subscription_id,
            "url": url,
            "payload": payload,
            "signature": signature,
            "status": WebhookDeliveryStatus.PENDING,
            "attempt": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "next_retry_at": datetime.now(timezone.utc).isoformat(),
        }
        
        self.deliveries[delivery_id] = delivery
        
        # Try immediate delivery
        await self._deliver_webhook(delivery_id)
        
        return delivery_id

    async def _deliver_webhook(self, delivery_id: str) -> bool:
        """
        Attempt to deliver webhook.
        
        Args:
            delivery_id: ID of delivery attempt
            
        Returns:
            True if successful
        """
        delivery = self.deliveries.get(delivery_id)
        if not delivery:
            return False
        
        delivery["attempt"] += 1
        client = await self.get_http_client()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Event": delivery["payload"]["event"],
                "X-Webhook-Delivery": delivery_id,
                "X-Webhook-Signature": f"sha256={delivery['signature']}",
            }
            
            response = await client.post(
                delivery["url"],
                json=delivery["payload"],
                headers=headers
            )
            
            if response.status_code in (200, 201, 202):
                delivery["status"] = WebhookDeliveryStatus.SUCCESS
                logger.info(f"Webhook {delivery_id} delivered successfully")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Webhook {delivery_id} delivery failed: {e}")
            
            if delivery["attempt"] < self.MAX_RETRIES:
                delivery["status"] = WebhookDeliveryStatus.RETRYING
                # Schedule retry
                retry_at = datetime.now(timezone.utc) + timedelta(
                    seconds=self.RETRY_DELAY_SECONDS * delivery["attempt"]
                )
                delivery["next_retry_at"] = retry_at.isoformat()
            else:
                delivery["status"] = WebhookDeliveryStatus.FAILED
                logger.error(f"Webhook {delivery_id} failed after {self.MAX_RETRIES} attempts")
            
            return False

    @staticmethod
    def _calculate_signature(payload: str, secret: str) -> str:
        """Calculate HMAC-SHA256 signature."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_signature(payload: str, secret: str, signature: str) -> bool:
        """Verify webhook signature."""
        expected = WebhookManager._calculate_signature(payload, secret)
        return hmac.compare_digest(expected, signature)

    def update_subscription(
        self,
        subscription_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update subscription settings."""
        if subscription_id not in self.subscriptions:
            return None
        
        subscription = self.subscriptions[subscription_id]
        for key, value in kwargs.items():
            if key in subscription:
                subscription[key] = value
        
        logger.info(f"Updated subscription {subscription_id}")
        return subscription

    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Deleted subscription {subscription_id}")
            return True
        return False

    def get_delivery_history(
        self,
        subscription_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get delivery history."""
        deliveries = list(self.deliveries.values())
        
        if subscription_id:
            deliveries = [d for d in deliveries if d["subscription_id"] == subscription_id]
        
        return sorted(
            deliveries,
            key=lambda x: x["created_at"],
            reverse=True
        )[:limit]


# Global webhook manager instance
_webhook_manager = None


def get_webhook_manager() -> WebhookManager:
    """Get or create global webhook manager."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
