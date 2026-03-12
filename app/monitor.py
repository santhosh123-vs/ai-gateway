import time
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class Monitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.requests: List[Dict] = []
        self.total_requests = 0
        self.total_errors = 0
        self.total_cost = 0.0
        self.total_cache_hits = 0
        self.requests_by_provider = defaultdict(int)
        self.requests_by_task = defaultdict(int)
        self.latencies: List[float] = []

    def log_request(
        self,
        task: str,
        provider: str,
        model: str,
        latency_ms: float,
        tokens_used: dict,
        cost_usd: float,
        success: bool,
        cached: bool = False
    ):
        self.total_requests += 1
        self.requests_by_provider[provider] += 1
        self.requests_by_task[task] += 1
        self.latencies.append(latency_ms)
        self.total_cost += cost_usd

        if not success:
            self.total_errors += 1

        if cached:
            self.total_cache_hits += 1

        request_log = {
            "task": task,
            "provider": provider,
            "model": model,
            "latency_ms": round(latency_ms, 2),
            "tokens_used": tokens_used,
            "cost_usd": round(cost_usd, 6),
            "success": success,
            "cached": cached,
            "timestamp": datetime.now().isoformat()
        }

        self.requests.append(request_log)

        # Keep only last 1000 requests in memory
        if len(self.requests) > 1000:
            self.requests = self.requests[-1000:]

    def get_metrics(self) -> dict:
        avg_latency = 0.0
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)

        error_rate = 0.0
        if self.total_requests > 0:
            error_rate = self.total_errors / self.total_requests

        cache_hit_rate = 0.0
        if self.total_requests > 0:
            cache_hit_rate = self.total_cache_hits / self.total_requests

        uptime = str(datetime.now() - self.start_time)

        return {
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost, 6),
            "average_latency_ms": round(avg_latency, 2),
            "requests_by_provider": dict(self.requests_by_provider),
            "requests_by_task": dict(self.requests_by_task),
            "error_rate": round(error_rate, 4),
            "cache_hit_rate": round(cache_hit_rate, 4),
            "uptime": uptime
        }

    def get_recent_requests(self, limit: int = 20) -> List[Dict]:
        return self.requests[-limit:]


# Global monitor instance
monitor = Monitor()
