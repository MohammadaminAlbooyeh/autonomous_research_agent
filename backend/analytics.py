"""
Analytics system for research task metrics and insights.

Tracks: task statistics, user activity, completion rates, performance metrics.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from enum import Enum
import json


class AnalyticsMetric(str, Enum):
    """Types of analytics metrics."""
    TASKS_CREATED = "tasks_created"
    TASKS_COMPLETED = "tasks_completed"
    TASKS_FAILED = "tasks_failed"
    AVG_COMPLETION_TIME = "avg_completion_time"
    USER_COUNT = "user_count"
    POPULAR_TOPICS = "popular_topics"
    RESEARCH_DEPTH_DISTRIBUTION = "depth_distribution"


class Analytics:
    """Track and analyze research task metrics."""

    def __init__(self):
        """Initialize analytics."""
        self.metrics: Dict[str, Any] = defaultdict(list)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.task_metrics: Dict[str, Dict[str, Any]] = {}

    def record_task_started(
        self,
        task_id: str,
        user: str,
        topic: str,
        depth: str
    ) -> None:
        """Record task start."""
        self.task_metrics[task_id] = {
            "id": task_id,
            "user": user,
            "topic": topic,
            "depth": depth,
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "status": "started",
            "duration_seconds": None,
        }
        
        self.metrics["tasks_created"].append({
            "task_id": task_id,
            "user": user,
            "topic": topic,
            "depth": depth,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_task_completed(
        self,
        task_id: str,
        findings_count: int,
        sources_count: int
    ) -> None:
        """Record task completion."""
        if task_id not in self.task_metrics:
            return
        
        task = self.task_metrics[task_id]
        completed_at = datetime.now(timezone.utc)
        task["completed_at"] = completed_at
        task["status"] = "completed"
        task["duration_seconds"] = (
            completed_at - task["started_at"]
        ).total_seconds()
        task["findings_count"] = findings_count
        task["sources_count"] = sources_count
        
        self.metrics["tasks_completed"].append({
            "task_id": task_id,
            "user": task["user"],
            "topic": task["topic"],
            "duration_seconds": task["duration_seconds"],
            "findings": findings_count,
            "sources": sources_count,
            "timestamp": completed_at.isoformat(),
        })

    def record_task_failed(
        self,
        task_id: str,
        error: str
    ) -> None:
        """Record task failure."""
        if task_id not in self.task_metrics:
            return
        
        task = self.task_metrics[task_id]
        task["status"] = "failed"
        task["error"] = error
        task["completed_at"] = datetime.now(timezone.utc)
        
        self.metrics["tasks_failed"].append({
            "task_id": task_id,
            "user": task["user"],
            "topic": task["topic"],
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_summary_stats(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get summary statistics for last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        tasks_created = [
            t for t in self.metrics["tasks_created"]
            if datetime.fromisoformat(t["timestamp"]) > cutoff
        ]
        tasks_completed = [
            t for t in self.metrics["tasks_completed"]
            if datetime.fromisoformat(t["timestamp"]) > cutoff
        ]
        tasks_failed = [
            t for t in self.metrics["tasks_failed"]
            if datetime.fromisoformat(t["timestamp"]) > cutoff
        ]
        
        completion_times = [
            t["duration_seconds"] for t in tasks_completed
            if t.get("duration_seconds") is not None
        ]
        
        return {
            "period_hours": hours,
            "tasks_created": len(tasks_created),
            "tasks_completed": len(tasks_completed),
            "tasks_failed": len(tasks_failed),
            "completion_rate": (
                len(tasks_completed) / len(tasks_created)
                if tasks_created else 0
            ),
            "avg_completion_time_seconds": (
                sum(completion_times) / len(completion_times)
                if completion_times else 0
            ),
            "total_findings": sum(t.get("findings", 0) for t in tasks_completed),
            "total_sources": sum(t.get("sources", 0) for t in tasks_completed),
            "unique_users": len(set(t["user"] for t in tasks_created)),
        }

    def get_popular_topics(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get most popular research topics."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        topics = defaultdict(int)
        for task in self.metrics["tasks_created"]:
            if datetime.fromisoformat(task["timestamp"]) > cutoff:
                topics[task["topic"]] += 1
        
        return sorted(
            [{"topic": k, "count": v} for k, v in topics.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:limit]

    def get_depth_distribution(
        self,
        hours: int = 24
    ) -> Dict[str, int]:
        """Get distribution of research depths."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        distribution = defaultdict(int)
        for task in self.metrics["tasks_created"]:
            if datetime.fromisoformat(task["timestamp"]) > cutoff:
                distribution[task["depth"]] += 1
        
        return dict(distribution)

    def get_user_activity(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get user activity metrics."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        user_stats = defaultdict(lambda: {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        })
        
        for task in self.metrics["tasks_created"]:
            if datetime.fromisoformat(task["timestamp"]) > cutoff:
                user_stats[task["user"]]["tasks_created"] += 1
        
        for task in self.metrics["tasks_completed"]:
            if datetime.fromisoformat(task["timestamp"]) > cutoff:
                user_stats[task["user"]]["tasks_completed"] += 1
        
        for task in self.metrics["tasks_failed"]:
            if datetime.fromisoformat(task["timestamp"]) > cutoff:
                user_stats[task["user"]]["tasks_failed"] += 1
        
        return dict(user_stats)

    def get_performance_trends(
        self,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get performance trends over time."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        now = datetime.now(timezone.utc)
        
        trends = []
        current_time = cutoff
        
        while current_time <= now:
            next_time = current_time + timedelta(minutes=interval_minutes)
            
            completed_in_window = [
                t for t in self.metrics["tasks_completed"]
                if datetime.fromisoformat(t["timestamp"]) >= current_time
                and datetime.fromisoformat(t["timestamp"]) < next_time
            ]
            
            avg_time = (
                sum(t["duration_seconds"] for t in completed_in_window) / len(completed_in_window)
                if completed_in_window else 0
            )
            
            trends.append({
                "timestamp": current_time.isoformat(),
                "completed_tasks": len(completed_in_window),
                "avg_completion_time": avg_time,
            })
            
            current_time = next_time
        
        return trends

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics as JSON."""
        return {
            "metrics": {
                "tasks_created": self.metrics["tasks_created"],
                "tasks_completed": self.metrics["tasks_completed"],
                "tasks_failed": self.metrics["tasks_failed"],
            },
            "summary": self.get_summary_stats(),
            "popular_topics": self.get_popular_topics(),
            "depth_distribution": self.get_depth_distribution(),
            "user_activity": self.get_user_activity(),
            "performance_trends": self.get_performance_trends(),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }


# Global analytics instance
_analytics = None


def get_analytics() -> Analytics:
    """Get or create global analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics
