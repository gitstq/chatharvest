"""
ChatHarvest - AI Coding Conversation Harvest & Intelligence Engine
🌾 Extract, analyze, search, and unlock value from AI coding assistant conversations.
"""

__version__ = "1.0.0"
__author__ = "ChatHarvest Team"
__license__ = "MIT"

from chatharvest.models import Conversation, Message, CodeSnippet, ConversationStats
from chatharvest.extractors import get_extractor, list_extractors, extract_all

__all__ = [
    "__version__",
    "Conversation",
    "Message",
    "CodeSnippet",
    "ConversationStats",
    "get_extractor",
    "list_extractors",
    "extract_all",
]
