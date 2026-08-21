"""
ChatHarvest Extractors - Platform-specific conversation extractors.
"""

from chatharvest.extractors.base import BaseExtractor
from chatharvest.extractors.claude_code import ClaudeCodeExtractor
from chatharvest.extractors.cursor import CursorExtractor
from chatharvest.extractors.windsurf import WindsurfExtractor
from chatharvest.extractors.aider import AiderExtractor
from chatharvest.extractors.cline import ClineExtractor
from chatharvest.extractors.chatgpt import ChatGPTExtractor
from chatharvest.extractors.gemini import GeminiExtractor
from chatharvest.models import Conversation

from typing import List, Optional

EXTRACTOR_REGISTRY = {
    "claude-code": ClaudeCodeExtractor,
    "cursor": CursorExtractor,
    "windsurf": WindsurfExtractor,
    "aider": AiderExtractor,
    "cline": ClineExtractor,
    "chatgpt": ChatGPTExtractor,
    "gemini": GeminiExtractor,
}


def get_extractor(source: str) -> Optional[BaseExtractor]:
    """Get an extractor instance by source name."""
    cls = EXTRACTOR_REGISTRY.get(source.lower())
    if cls:
        return cls()
    return None


def list_extractors() -> List[str]:
    """List all available extractor names."""
    return sorted(EXTRACTOR_REGISTRY.keys())


def extract_all(source: str, path: Optional[str] = None) -> List[Conversation]:
    """Extract all conversations from a given source."""
    extractor = get_extractor(source)
    if not extractor:
        raise ValueError(f"Unknown source: {source}. Available: {list_extractors()}")
    return extractor.extract(path)
