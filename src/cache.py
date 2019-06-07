from dataclasses import dataclass
from typing import Any, Dict, Optional

from psn_client import UnixTimestamp

@dataclass
class CacheEntry:
    value: Any
    timestamp: UnixTimestamp

class Cache:
    def __init__(self):
        self._entries: Dict[Any, CacheEntry] = {}

    def get(self, key: Any, timestamp: UnixTimestamp):
        entry: Optional[CacheEntry] = self._entries.get(key)
        if entry is None:
            return None
        if entry.timestamp < timestamp:
            return None
        return entry.value

    def update(self, key: Any, value: Any, timestamp: UnixTimestamp):
        entry: Optional[CacheEntry] = self._entries.get(key)
        if entry is None:
            self._entries[key] = CacheEntry(value, timestamp)
        else:
            if entry.timestamp < timestamp:
                entry.value = value
                entry.timestamp = timestamp

    def __iter__(self):
        for key, entry in self._entries.items():
            yield key, entry.value
