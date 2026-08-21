"""
Base extractor class - defines the interface for all platform extractors.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from chatharvest.models import Conversation, Message


class BaseExtractor(ABC):
    """Abstract base class for conversation extractors."""

    name: str = "base"
    display_name: str = "Base"
    default_path: str = ""
    file_patterns: List[str] = []

    def __init__(self):
        self.conversations: List[Conversation] = []

    @abstractmethod
    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        """Extract conversations from the given path."""
        pass

    def _resolve_path(self, path: Optional[str]) -> str:
        """Resolve the data path, using default if not provided."""
        if path:
            return os.path.expanduser(path)
        return os.path.expanduser(self.default_path)

    def _find_files(self, directory: str, patterns: List[str]) -> List[str]:
        """Find files matching patterns in directory recursively."""
        found = []
        if not os.path.isdir(directory):
            return found
        for root, _, files in os.walk(directory):
            for f in files:
                for pattern in patterns:
                    if f.endswith(pattern) or f == pattern:
                        found.append(os.path.join(root, f))
                        break
        return sorted(found)

    def _read_json(self, filepath: str):
        """Read and parse a JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                with open(filepath, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception:
                return None
        except Exception:
            return None

    def _read_jsonl(self, filepath: str) -> List[dict]:
        """Read and parse a JSONL file."""
        records = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        return records

    def _safe_get(self, obj: dict, *keys, default=None):
        """Safely get nested dict values."""
        current = obj
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
        return current if current is not None else default

    def _deduplicate(self, conversations: List[Conversation]) -> List[Conversation]:
        """Remove duplicate conversations by content hash."""
        seen = set()
        unique = []
        for conv in conversations:
            h = conv.content_hash
            if h not in seen:
                seen.add(h)
                unique.append(conv)
        return unique
