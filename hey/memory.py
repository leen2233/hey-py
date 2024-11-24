"""Message caching system for hey."""
import json
import os
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Deque, Dict

from .models import ChatMessage


@dataclass
class CachedMessage:
    message: ChatMessage
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            "role": self.message.role,
            "content": self.message.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CachedMessage":
        return cls(
            message=ChatMessage(role=data["role"], content=data["content"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class MessageCache:
    
    def __init__(self, max_size: int = 10, expiry_hours: int = 24):
        """Initialize the message cache.
        
        Args:
            max_size: Maximum number of messages to store
            expiry_hours: Number of hours after which messages expire
        """
        self._messages: Deque[CachedMessage] = deque(maxlen=max_size)
        self._expiry_delta = timedelta(hours=expiry_hours)
        self._load_cache()

    @staticmethod
    def get_cache_dir() -> str:
        return os.getenv("HEY_CACHE_PATH", os.path.expanduser("~/.cache/hey"))

    @staticmethod
    def get_cache_file() -> str:
        return os.getenv("HEY_CACHE_FILENAME", "messages.json")

    def _load_cache(self) -> None:
        try:
            cache_path = Path(self.get_cache_dir())
            cache_file = cache_path / self.get_cache_file()
            
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    messages = [CachedMessage.from_dict(msg) for msg in data]
                    self._messages = deque(messages, maxlen=self._messages.maxlen)
                    self._cleanup_expired()
        except Exception as e:
            print(f"Warning: Failed to load message cache: {e}")
            self._messages.clear()

    def _save_cache(self) -> None:
        try:
            cache_path = Path(self.get_cache_dir())
            cache_path.mkdir(parents=True, exist_ok=True)
            
            cache_file = cache_path / self.get_cache_file()
            with open(cache_file, 'w') as f:
                data = [msg.to_dict() for msg in self._messages]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save message cache: {e}")

    def add_message(self, message: ChatMessage) -> None:
        self._cleanup_expired()
        self._messages.append(CachedMessage(message, datetime.now()))
        self._save_cache()

    def get_messages(self) -> List[ChatMessage]:
        self._cleanup_expired()
        return [m.message for m in self._messages]

    def clear(self) -> None:
        self._messages.clear()
        self._save_cache()

    def _cleanup_expired(self) -> None:
        now = datetime.now()
        self._messages = deque(
            (msg for msg in self._messages 
             if now - msg.timestamp <= self._expiry_delta),
            maxlen=self._messages.maxlen
        )
        self._save_cache()

    @property
    def size(self) -> int:
        self._cleanup_expired()
        return len(self._messages)


# Global cache instance
_cache: Optional[MessageCache] = None

def get_cache() -> MessageCache:
    global _cache
    if _cache is None:
        _cache = MessageCache()
    return _cache
