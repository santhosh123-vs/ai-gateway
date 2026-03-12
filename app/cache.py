import hashlib
import json
import time
from typing import Optional, Dict


class SimpleCache:
    """
    In-memory cache for AI responses.
    Avoids duplicate API calls and saves cost.
    """

    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, dict] = {}
        self.default_ttl = default_ttl  # 1 hour default
        self.hits = 0
        self.misses = 0

    def _make_key(self, task: str, input_text: str, model: str, temperature: float) -> str:
        """Create unique hash key from request parameters"""
        raw = f"{task}:{input_text}:{model}:{temperature}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, task: str, input_text: str, model: str, temperature: float) -> Optional[dict]:
        """Get cached response if exists and not expired"""
        key = self._make_key(task, input_text, model, temperature)

        if key in self.cache:
            entry = self.cache[key]
            # Check if expired
            if time.time() - entry["created_at"] < self.default_ttl:
                self.hits += 1
                return entry["response"]
            else:
                # Expired, remove it
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, task: str, input_text: str, model: str, temperature: float, response: dict):
        """Store response in cache"""
        key = self._make_key(task, input_text, model, temperature)
        self.cache[key] = {
            "response": response,
            "created_at": time.time()
        }

        # Keep cache size manageable (max 500 entries)
        if len(self.cache) > 500:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]["created_at"])
            del self.cache[oldest_key]

    def get_stats(self) -> dict:
        """Return cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4)
        }

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


# Global cache instance
cache = SimpleCache()
