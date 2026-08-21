"""
ChatHarvest Knowledge Extractor - Auto-extract valuable knowledge from conversations.
Extracts code snippets, decisions, TODOs, errors, and patterns.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from chatharvest.models import Conversation, Message, CodeSnippet


@dataclass
class ExtractedKnowledge:
    """Knowledge extracted from a single conversation."""
    code_snippets: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    todos: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


class KnowledgeExtractor:
    """Extracts structured knowledge from AI conversations."""

    # Decision patterns
    DECISION_PATTERNS = [
        r"(?:we|i|let'?s)\s+(?:will|should|decided|choose|go with|use|adopt)\s+([^.\n]+)",
        r"(?:decision|conclusion|approach|solution)[:：]\s*([^\n]+)",
        r"(?:最终|决定|选择|采用|方案是)[:：]?\s*([^\n]+)",
    ]

    # TODO patterns
    TODO_PATTERNS = [
        r"(?:TODO|FIXME|HACK|XXX|NOTE)[:：]?\s*([^\n]+)",
        r"(?:need to|should|must|have to|going to|will)\s+(?:add|implement|fix|create|update|remove|refactor|test|write)\s+([^\n]+)",
        r"(?:待办|需要|应该|必须|后续)\s*[:：]?\s*([^\n]+)",
    ]

    # Error patterns
    ERROR_PATTERNS = [
        r"(?:Error|Exception|Traceback|FATAL|CRITICAL)[:：]?\s*([^\n]+)",
        r"(?:失败|报错|错误|异常|崩溃)[:：]?\s*([^\n]+)",
    ]

    # Command patterns (shell commands in code blocks)
    COMMAND_PATTERNS = [
        r'^\$\s+([^\n]+)',
        r'^(?:npm|pip|python|node|docker|git|cargo|go|make|curl|wget)\s+([^\n]+)',
    ]

    def __init__(self):
        pass

    def extract(self, conversation: Conversation) -> ExtractedKnowledge:
        """Extract all knowledge from a conversation."""
        knowledge = ExtractedKnowledge()

        full_text = "\n".join(m.content or "" for m in conversation.messages)

        # Extract code snippets with context
        knowledge.code_snippets = self._extract_code_snippets(conversation)

        # Extract decisions
        knowledge.decisions = self._extract_patterns(full_text, self.DECISION_PATTERNS)

        # Extract TODOs
        knowledge.todos = self._extract_patterns(full_text, self.TODO_PATTERNS)

        # Extract errors
        knowledge.errors = self._extract_patterns(full_text, self.ERROR_PATTERNS)

        # Extract commands
        knowledge.commands = self._extract_commands(conversation)

        # Extract key terms (top technical terms)
        knowledge.key_terms = self._extract_key_terms(full_text)

        conversation.extracted_knowledge = knowledge.to_dict()
        return knowledge

    def extract_all(self, conversations: List[Conversation]) -> List[ExtractedKnowledge]:
        """Extract knowledge from all conversations."""
        return [self.extract(conv) for conv in conversations]

    def _extract_code_snippets(self, conversation: Conversation) -> List[Dict[str, Any]]:
        """Extract code snippets with metadata."""
        snippets = []
        for msg_idx, msg in enumerate(conversation.messages):
            for snippet in msg.code_snippets:
                # Determine if it's a command, config, or code
                snippet_type = self._classify_snippet(snippet)
                snippets.append({
                    "language": snippet.language,
                    "type": snippet_type,
                    "code": snippet.code,
                    "line_count": snippet.code.count("\n") + 1,
                    "char_count": len(snippet.code),
                    "message_index": msg_idx,
                    "role": msg.role,
                })
        return snippets

    def _classify_snippet(self, snippet: CodeSnippet) -> str:
        """Classify a code snippet by type."""
        code = snippet.code.strip()
        lang = snippet.language.lower()

        # Shell commands
        if lang in ("bash", "sh", "shell", "zsh", "console", "terminal"):
            return "command"
        if code.startswith("$ ") or code.startswith("# "):
            return "command"

        # Config files
        if lang in ("json", "yaml", "yml", "toml", "ini", "cfg", "conf", "env", "dotenv"):
            return "config"

        # SQL
        if lang in ("sql",):
            return "query"

        # Regular code
        return "code"

    def _extract_patterns(self, text: str, patterns: List[str], max_items: int = 20) -> List[str]:
        """Extract text matching regex patterns."""
        results = []
        seen = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                match = match.strip().rstrip(".,;:!?")
                if match and len(match) > 3 and len(match) < 200 and match.lower() not in seen:
                    seen.add(match.lower())
                    results.append(match)
                if len(results) >= max_items:
                    return results
        return results

    def _extract_commands(self, conversation: Conversation) -> List[str]:
        """Extract shell commands from code blocks."""
        commands = []
        seen = set()
        for msg in conversation.messages:
            for snippet in msg.code_snippets:
                if snippet.language.lower() in ("bash", "sh", "shell", "zsh", "console", "terminal"):
                    for line in snippet.code.split("\n"):
                        line = line.strip()
                        if line.startswith("$ "):
                            cmd = line[2:].strip()
                        elif re.match(r'^(npm|pip|python|node|docker|git|cargo|go|make|curl|wget|apt|brew|yarn|pnpm)\s', line):
                            cmd = line
                        else:
                            continue
                        if cmd and cmd not in seen and len(cmd) < 200:
                            seen.add(cmd)
                            commands.append(cmd)
        return commands[:30]

    def _extract_key_terms(self, text: str, top_n: int = 15) -> List[str]:
        """Extract key technical terms from text."""
        # Common technical keywords
        tech_terms = re.findall(
            r'\b(?:python|javascript|typescript|react|vue|angular|node|django|flask|fastapi|'
            r'docker|kubernetes|aws|gcp|azure|redis|postgres|mysql|mongodb|graphql|rest|api|'
            r'git|github|ci|cd|pipeline|testing|unittest|pytest|jest|mocha|webpack|vite|'
            r'linux|ubuntu|debian|centos|nginx|apache|ssl|https|oauth|jwt|auth|token|'
            r'algorithm|data structure|complexity|performance|optimization|refactor|debug|'
            r'microservice|monolith|serverless|lambda|function|class|module|package|library|'
            r'css|html|dom|ajax|fetch|axios|promise|async|await|callback|event|listener)\b',
            text.lower()
        )
        from collections import Counter
        counter = Counter(tech_terms)
        return [term for term, _ in counter.most_common(top_n)]
