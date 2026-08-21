"""
Tests for ChatHarvest extractors.
"""

import os
import json
import tempfile
import pytest

from chatharvest.extractors import list_extractors, get_extractor, EXTRACTOR_REGISTRY
from chatharvest.extractors.base import BaseExtractor
from chatharvest.extractors.claude_code import ClaudeCodeExtractor
from chatharvest.extractors.chatgpt import ChatGPTExtractor
from chatharvest.models import Conversation


class TestExtractorRegistry:
    def test_list_extractors(self):
        extractors = list_extractors()
        assert len(extractors) >= 7
        assert "claude-code" in extractors
        assert "cursor" in extractors
        assert "aider" in extractors
        assert "cline" in extractors
        assert "chatgpt" in extractors
        assert "gemini" in extractors
        assert "windsurf" in extractors

    def test_get_extractor(self):
        extractor = get_extractor("claude-code")
        assert extractor is not None
        assert isinstance(extractor, ClaudeCodeExtractor)

    def test_get_unknown_extractor(self):
        assert get_extractor("nonexistent") is None

    def test_all_extractors_inherit_base(self):
        for name, cls in EXTRACTOR_REGISTRY.items():
            assert issubclass(cls, BaseExtractor), f"{name} does not inherit BaseExtractor"


class TestClaudeCodeExtractor:
    def test_extract_from_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = ClaudeCodeExtractor()
            conversations = extractor.extract(tmpdir)
            assert conversations == []

    def test_extract_from_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = os.path.join(tmpdir, "myproject")
            os.makedirs(project_dir)
            conv_data = {
                "title": "Test Conversation",
                "model": "claude-sonnet-4",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!", "model": "claude-sonnet-4"},
                ],
            }
            conv_file = os.path.join(project_dir, "abc123.json")
            with open(conv_file, "w") as f:
                json.dump(conv_data, f)

            extractor = ClaudeCodeExtractor()
            conversations = extractor.extract(tmpdir)
            assert len(conversations) == 1
            assert conversations[0].title == "Test Conversation"
            assert len(conversations[0].messages) == 2


class TestChatGPTExtractor:
    def test_extract_from_conversations_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            conv_data = [{
                "title": "ChatGPT Test",
                "conversation_id": "conv-123",
                "create_time": 1700000000,
                "mapping": {
                    "msg1": {
                        "message": {"role": "user", "content": {"content_type": "text", "parts": ["Hello"]}},
                        "parent": None,
                        "children": ["msg2"],
                    },
                    "msg2": {
                        "message": {"role": "assistant", "content": {"content_type": "text", "parts": ["Hi!"]}},
                        "parent": "msg1",
                        "children": [],
                    },
                },
                "current_node": "msg2",
            }]
            filepath = os.path.join(tmpdir, "conversations.json")
            with open(filepath, "w") as f:
                json.dump(conv_data, f)

            extractor = ChatGPTExtractor()
            conversations = extractor.extract(filepath)
            assert len(conversations) == 1
            assert conversations[0].title == "ChatGPT Test"


class TestBaseExtractor:
    def test_safe_get(self):
        extractor = ClaudeCodeExtractor()
        data = {"a": {"b": {"c": 42}}}
        assert extractor._safe_get(data, "a", "b", "c") == 42
        assert extractor._safe_get(data, "a", "x", "c") is None
        assert extractor._safe_get(data, "a", "b", "c", default=0) == 42

    def test_deduplicate(self):
        extractor = ClaudeCodeExtractor()
        from chatharvest.models import Message
        conv1 = Conversation(id="1", source="test", title="A", messages=[Message(role="user", content="Hello")])
        conv2 = Conversation(id="2", source="test", title="B", messages=[Message(role="user", content="Hello")])
        conv3 = Conversation(id="3", source="test", title="C", messages=[Message(role="user", content="World")])
        result = extractor._deduplicate([conv1, conv2, conv3])
        assert len(result) == 2
