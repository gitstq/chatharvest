"""
ChatHarvest Searcher - Full-text search across conversations.
Zero-dependency inverted index search engine.
"""

import re
import math
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional, Set

from chatharvest.models import Conversation, Message


class SearchResult:
    """A single search result."""
    def __init__(self, conversation: Conversation, score: float, matched_terms: List[str],
                 highlight_snippet: str = ""):
        self.conversation = conversation
        self.score = score
        self.matched_terms = matched_terms
        self.highlight_snippet = highlight_snippet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.conversation.id,
            "title": self.conversation.title,
            "source": self.conversation.source,
            "score": round(self.score, 4),
            "matched_terms": self.matched_terms,
            "highlight": self.highlight_snippet,
            "message_count": self.conversation.stats.message_count if self.conversation.stats else 0,
            "created_at": self.conversation.created_at,
        }


class ConversationSearcher:
    """Full-text search engine for conversations using TF-IDF."""

    def __init__(self, conversations: List[Conversation]):
        self.conversations = conversations
        self.inverted_index: Dict[str, Set[int]] = defaultdict(set)
        self.doc_freq: Dict[str, int] = Counter()
        self.doc_lengths: List[int] = []
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer - lowercase, split on non-alphanumeric, filter short tokens."""
        if not text:
            return []
        # Keep Chinese characters, alphanumeric, and underscores
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9_]+', text.lower())
        return [t for t in tokens if len(t) >= 2 or '\u4e00' <= t[0] <= '\u9fff']

    def _build_index(self):
        """Build inverted index from conversations."""
        for idx, conv in enumerate(self.conversations):
            doc_text = self._get_document_text(conv)
            tokens = self._tokenize(doc_text)
            self.doc_lengths.append(len(tokens))
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.inverted_index[token].add(idx)
                self.doc_freq[token] += 1

    def _get_document_text(self, conv: Conversation) -> str:
        """Get full searchable text for a conversation."""
        parts = [conv.title]
        for msg in conv.messages:
            parts.append(msg.content or "")
            for snippet in msg.code_snippets:
                parts.append(snippet.code)
        return " ".join(parts)

    def search(self, query: str, limit: int = 20, source_filter: Optional[str] = None,
               date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[SearchResult]:
        """
        Search conversations using TF-IDF scoring.

        Args:
            query: Search query string
            limit: Maximum number of results
            source_filter: Filter by source (e.g., 'claude-code')
            date_from: Filter conversations created after this date (YYYY-MM-DD)
            date_to: Filter conversations created before this date (YYYY-MM-DD)
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        N = len(self.conversations)
        scores: Dict[int, float] = defaultdict(float)
        matched_terms_per_doc: Dict[int, Set[str]] = defaultdict(set)

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            doc_ids = self.inverted_index[token]
            idf = math.log((N + 1) / (self.doc_freq[token] + 1)) + 1

            for doc_id in doc_ids:
                # Apply filters
                if source_filter and self.conversations[doc_id].source != source_filter:
                    continue
                if date_from or date_to:
                    conv_date = self.conversations[doc_id].created_at
                    if not conv_date:
                        continue
                    conv_date_str = conv_date[:10]
                    if date_from and conv_date_str < date_from:
                        continue
                    if date_to and conv_date_str > date_to:
                        continue

                # TF calculation
                doc_text = self._get_document_text(self.conversations[doc_id])
                tf = doc_text.lower().count(token) / max(self.doc_lengths[doc_id], 1)
                scores[doc_id] += tf * idf
                matched_terms_per_doc[doc_id].add(token)

        # Sort by score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in sorted_docs[:limit]:
            conv = self.conversations[doc_id]
            snippet = self._generate_snippet(conv, query_tokens)
            results.append(SearchResult(
                conversation=conv,
                score=score,
                matched_terms=list(matched_terms_per_doc[doc_id]),
                highlight_snippet=snippet,
            ))

        return results

    def _generate_snippet(self, conv: Conversation, query_tokens: List[str], max_length: int = 200) -> str:
        """Generate a text snippet around the first query match."""
        for msg in conv.messages:
            content = msg.content or ""
            lower_content = content.lower()
            for token in query_tokens:
                pos = lower_content.find(token)
                if pos >= 0:
                    start = max(0, pos - 50)
                    end = min(len(content), pos + max_length - 50)
                    snippet = content[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."
                    return snippet
        return conv.title

    def list_all(self, limit: int = 100, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all conversations with basic info."""
        results = []
        for conv in self.conversations:
            if source_filter and conv.source != source_filter:
                continue
            if not conv.stats:
                conv.compute_stats()
            results.append({
                "id": conv.id,
                "title": conv.title,
                "source": conv.source,
                "messages": conv.stats.message_count,
                "tokens": conv.stats.total_tokens,
                "created_at": conv.created_at,
                "model": conv.model,
            })
            if len(results) >= limit:
                break
        return results
