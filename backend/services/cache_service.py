import os
import json
import hashlib
import time
from typing import Optional


class CacheService:
    def __init__(self, ttl: int = 3600):
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
        self.ttl = ttl
        os.makedirs(self.cache_dir, exist_ok=True)

    def _key_path(self, key: str) -> str:
        hashed = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed}.json")

    def get(self, key: str) -> Optional[any]:
        path = self._key_path(key)
        try:
            with open(path) as f:
                data = json.load(f)
            if time.time() - data["timestamp"] < self.ttl:
                return data["value"]
            os.remove(path)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return None

    def set(self, key: str, value: any):
        path = self._key_path(key)
        try:
            with open(path, "w") as f:
                json.dump({"timestamp": time.time(), "value": value}, f)
        except Exception:
            pass

    def clear(self):
        for fname in os.listdir(self.cache_dir):
            try:
                os.remove(os.path.join(self.cache_dir, fname))
            except Exception:
                pass
