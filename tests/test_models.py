"""
Tests for ChatHarvest data models.
"""

import pytest
from chatharvest.models import Conversation, Message, CodeSnippet, ConversationStats


class TestMessage:
    def test_create_message(self):
        msg = Message(role="user", content="Hello, world!")
        assert msg.role == "user"
        assert msg.content == "Hello, world!"
        assert msg.char_count == 13
        assert msg.line_count == 1

    def test_message_with_code_snippets(self):
        content = 'Here is some code:\n```python\nprint("hello")\n```\nDone!'
        msg = Message(role="assistant", content=content)
        snippets = msg.extract_code_snippets()
        assert len(snippets) == 1
        assert snippets[0].language == "python"
        assert 'print("hello")' in snippets[0].code

    def test_message_multiple_code_snippets(self):
        content = '```js\nconst x = 1;\n```\n```py\ny = 2\n```'
        msg = Message(role="assistant", content=content)
        snippets = msg.extract_code_snippets()
        assert len(snippets) == 2

    def test_message_total_tokens(self):
        msg = Message(role="assistant", content="test", tokens_input=100, tokens_output=50)
        assert msg.total_tokens == 150

    def test_message_to_dict(self):
        msg = Message(role="user", content="test")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "test"
        assert "char_count" in d
        assert "line_count" in d


class TestConversation:
    def test_create_conversation(self):
        messages = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
        ]
        conv = Conversation(id="test1", source="claude-code", title="Test Chat", messages=messages)
        assert conv.id == "test1"
        assert len(conv.messages) == 2

    def test_compute_stats(self):
        messages = [
            Message(role="user", content="Fix the bug", tokens_input=50),
            Message(role="assistant", content='```python\nprint("fixed")\n```', tokens_output=100),
        ]
        conv = Conversation(id="test2", source="cursor", title="Bug Fix", messages=messages)
        stats = conv.compute_stats()
        assert stats.message_count == 2
        assert stats.user_messages == 1
        assert stats.assistant_messages == 1
        assert stats.total_tokens == 150
        assert stats.code_snippet_count == 1
        assert "python" in stats.languages_used

    def test_content_hash_deduplication(self):
        messages1 = [Message(role="user", content="Hello")]
        messages2 = [Message(role="user", content="Hello")]
        conv1 = Conversation(id="1", source="test", title="A", messages=messages1)
        conv2 = Conversation(id="2", source="test", title="B", messages=messages2)
        assert conv1.content_hash == conv2.content_hash

    def test_content_hash_different(self):
        conv1 = Conversation(id="1", source="test", title="A", messages=[Message(role="user", content="Hello")])
        conv2 = Conversation(id="2", source="test", title="B", messages=[Message(role="user", content="World")])
        assert conv1.content_hash != conv2.content_hash

    def test_to_json(self):
        conv = Conversation(id="1", source="test", title="Test", messages=[Message(role="user", content="hi")])
        json_str = conv.to_json()
        assert '"title": "Test"' in json_str
        assert '"source": "test"' in json_str


class TestCodeSnippet:
    def test_create_snippet(self):
        snippet = CodeSnippet(language="python", code="print('hello')")
        assert snippet.language == "python"
        assert snippet.code == "print('hello')"
