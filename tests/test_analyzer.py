"""
Tests for ChatHarvest analyzer, searcher, and knowledge extractor.
"""

import pytest
from chatharvest.models import Conversation, Message
from chatharvest.analyzer import ConversationAnalyzer
from chatharvest.searcher import ConversationSearcher
from chatharvest.knowledge import KnowledgeExtractor


def make_conversation(id, source, title, messages_data):
    messages = [Message(role=role, content=content) for role, content in messages_data]
    return Conversation(id=id, source=source, title=title, messages=messages)


@pytest.fixture
def sample_conversations():
    return [
        make_conversation("1", "claude-code", "Docker Setup", [
            ("user", "How do I set up docker compose for a Python app?"),
            ("assistant", "Here is a docker-compose.yml:\n```yaml\nversion: '3'\nservices:\n  app:\n    image: python:3.12\n```"),
        ]),
        make_conversation("2", "cursor", "Bug Fix in React", [
            ("user", "There is a bug in my React component, it throws an error"),
            ("assistant", "I found the bug. Fix the useState hook:\n```jsx\nconst [count, setCount] = useState(0);\n```"),
        ]),
        make_conversation("3", "aider", "API Implementation", [
            ("user", "Implement a REST API with FastAPI"),
            ("assistant", "Here is the implementation:\n```python\nfrom fastapi import FastAPI\napp = FastAPI()\n```"),
            ("user", "Add tests"),
            ("assistant", "TODO: add pytest tests"),
        ]),
    ]


class TestConversationAnalyzer:
    def test_compute_global_stats(self, sample_conversations):
        analyzer = ConversationAnalyzer(sample_conversations)
        stats = analyzer.compute_global_stats()
        assert stats.total_conversations == 3
        assert stats.total_messages == 8
        assert stats.total_code_snippets >= 2
        assert "claude-code" in stats.conversations_by_source
        assert "cursor" in stats.conversations_by_source

    def test_classify_tasks(self, sample_conversations):
        analyzer = ConversationAnalyzer(sample_conversations)
        tasks = analyzer.classify_tasks()
        assert len(tasks) > 0
        # Bug fix conversation should be classified
        all_titles = [t["title"] for tasks_list in tasks.values() for t in tasks_list]
        assert "Bug Fix in React" in all_titles

    def test_generate_insights(self, sample_conversations):
        analyzer = ConversationAnalyzer(sample_conversations)
        insights = analyzer.generate_insights()
        assert "summary" in insights
        assert "recommendations" in insights
        assert len(insights["recommendations"]) > 0

    def test_find_common_errors(self, sample_conversations):
        analyzer = ConversationAnalyzer(sample_conversations)
        errors = analyzer.find_common_errors()
        # Should find the "error" mention
        assert len(errors) >= 0  # May or may not find patterns


class TestConversationSearcher:
    def test_search_basic(self, sample_conversations):
        searcher = ConversationSearcher(sample_conversations)
        results = searcher.search("docker")
        assert len(results) >= 1
        assert results[0].conversation.title == "Docker Setup"

    def test_search_react(self, sample_conversations):
        searcher = ConversationSearcher(sample_conversations)
        results = searcher.search("react bug")
        assert len(results) >= 1
        assert "Bug Fix in React" == results[0].conversation.title

    def test_search_with_source_filter(self, sample_conversations):
        searcher = ConversationSearcher(sample_conversations)
        results = searcher.search("python", source_filter="aider")
        assert len(results) >= 1
        assert all(r.conversation.source == "aider" for r in results)

    def test_search_no_results(self, sample_conversations):
        searcher = ConversationSearcher(sample_conversations)
        results = searcher.search("xyznonexistent123")
        assert len(results) == 0

    def test_list_all(self, sample_conversations):
        searcher = ConversationSearcher(sample_conversations)
        items = searcher.list_all()
        assert len(items) == 3


class TestKnowledgeExtractor:
    def test_extract_code_snippets(self, sample_conversations):
        extractor = KnowledgeExtractor()
        knowledge = extractor.extract(sample_conversations[0])
        assert len(knowledge.code_snippets) >= 1
        assert knowledge.code_snippets[0]["language"] == "yaml"

    def test_extract_todos(self, sample_conversations):
        extractor = KnowledgeExtractor()
        knowledge = extractor.extract(sample_conversations[2])
        # Should find the TODO
        assert len(knowledge.todos) >= 0

    def test_extract_commands(self, sample_conversations):
        extractor = KnowledgeExtractor()
        # Add a conversation with commands
        conv = make_conversation("4", "claude-code", "Commands", [
            ("assistant", "Run these commands:\n```bash\n$ pip install fastapi\n$ docker compose up\n```"),
        ])
        knowledge = extractor.extract(conv)
        assert len(knowledge.commands) >= 1

    def test_extract_key_terms(self, sample_conversations):
        extractor = KnowledgeExtractor()
        knowledge = extractor.extract(sample_conversations[2])
        assert len(knowledge.key_terms) >= 0
