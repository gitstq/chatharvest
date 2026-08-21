"""
ChatHarvest Data Models - Unified conversation representation across all AI coding tools.
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class CodeSnippet:
    """A code block extracted from a message."""
    language: str
    code: str
    filename: Optional[str] = None
    line_start: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # user, assistant, system, tool
    content: str
    timestamp: Optional[str] = None
    model: Optional[str] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    code_snippets: List[CodeSnippet] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return (self.tokens_input or 0) + (self.tokens_output or 0)

    @property
    def char_count(self) -> int:
        return len(self.content or "")

    @property
    def line_count(self) -> int:
        return (self.content or "").count("\n") + 1 if self.content else 0

    def extract_code_snippets(self) -> List[CodeSnippet]:
        """Extract fenced code blocks from message content."""
        snippets = []
        if not self.content:
            return snippets
        lines = self.content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith("```"):
                lang = line.strip()[3:].strip() or "text"
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    snippets.append(CodeSnippet(
                        language=lang,
                        code="\n".join(code_lines)
                    ))
            i += 1
        self.code_snippets = snippets
        return snippets

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["total_tokens"] = self.total_tokens
        d["char_count"] = self.char_count
        d["line_count"] = self.line_count
        return d


@dataclass
class ConversationStats:
    """Computed statistics for a conversation."""
    message_count: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    total_tokens: int = 0
    total_chars: int = 0
    code_snippet_count: int = 0
    languages_used: List[str] = field(default_factory=list)
    duration_seconds: Optional[float] = None
    estimated_cost_usd: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Conversation:
    """A unified conversation representation."""
    id: str
    source: str  # claude-code, cursor, windsurf, aider, cline, chatgpt, gemini
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    model: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    stats: Optional[ConversationStats] = None
    extracted_knowledge: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for msg in self.messages:
            if not msg.code_snippets:
                msg.extract_code_snippets()

    @property
    def content_hash(self) -> str:
        """Generate a unique hash for deduplication based on message content (not title)."""
        content = f"{self.source}:"
        for msg in self.messages:
            content += f"{msg.role}:{msg.content[:200]}|"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def compute_stats(self, cost_per_1k_input: float = 0.003,
                      cost_per_1k_output: float = 0.015) -> ConversationStats:
        """Compute conversation statistics."""
        stats = ConversationStats()
        stats.message_count = len(self.messages)
        total_input = 0
        total_output = 0
        langs = set()

        for msg in self.messages:
            if msg.role == "user":
                stats.user_messages += 1
            elif msg.role == "assistant":
                stats.assistant_messages += 1
            total_input += msg.tokens_input or 0
            total_output += msg.tokens_output or 0
            stats.total_chars += msg.char_count
            stats.code_snippet_count += len(msg.code_snippets)
            for snippet in msg.code_snippets:
                if snippet.language and snippet.language != "text":
                    langs.add(snippet.language)

        stats.total_tokens = total_input + total_output
        stats.languages_used = sorted(langs)

        # Estimate cost
        if stats.total_tokens > 0:
            stats.estimated_cost_usd = round(
                (total_input / 1000 * cost_per_1k_input) +
                (total_output / 1000 * cost_per_1k_output), 6
            )

        # Duration
        if self.created_at and self.updated_at:
            try:
                start = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
                stats.duration_seconds = (end - start).total_seconds()
            except (ValueError, TypeError):
                pass

        self.stats = stats
        return stats

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
            "tags": self.tags,
            "metadata": self.metadata,
            "messages": [m.to_dict() for m in self.messages],
            "content_hash": self.content_hash,
        }
        if self.stats:
            d["stats"] = self.stats.to_dict()
        if self.extracted_knowledge:
            d["extracted_knowledge"] = self.extracted_knowledge
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)
