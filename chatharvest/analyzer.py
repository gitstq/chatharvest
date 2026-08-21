"""
ChatHarvest Analyzer - Conversation analytics and insights engine.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from chatharvest.models import Conversation, Message


@dataclass
class GlobalStats:
    """Global statistics across all conversations."""
    total_conversations: int = 0
    total_messages: int = 0
    total_tokens: int = 0
    total_chars: int = 0
    total_code_snippets: int = 0
    estimated_total_cost_usd: float = 0.0
    conversations_by_source: Dict[str, int] = field(default_factory=dict)
    conversations_by_model: Dict[str, int] = field(default_factory=dict)
    languages_used: Dict[str, int] = field(default_factory=dict)
    busiest_days: Dict[str, int] = field(default_factory=dict)
    busiest_hours: Dict[int, int] = field(default_factory=dict)
    avg_messages_per_conversation: float = 0.0
    avg_tokens_per_conversation: float = 0.0
    top_conversations_by_tokens: List[Dict[str, Any]] = field(default_factory=list)
    top_conversations_by_messages: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


class ConversationAnalyzer:
    """Analyzes conversations and generates insights."""

    # Common coding task patterns
    TASK_PATTERNS = {
        "bug_fix": [r"\bbug\b", r"\bfix\b", r"\berror\b", r"\bexception\b", r"\bcrash\b", r"\bbroken\b", r"\breproduce\b"],
        "feature": [r"\badd\b", r"\bimplement\b", r"\bfeature\b", r"\bnew\b", r"\bcreate\b", r"\bbuild\b"],
        "refactor": [r"\brefactor\b", r"\bclean\b", r"\boptimize\b", r"\brestructure\b", r"\brewrite\b"],
        "debug": [r"\bdebug\b", r"\btrace\b", r"\bprint\b", r"\bconsole\.log\b", r"\bbreakpoint\b"],
        "test": [r"\btest\b", r"\bunit test\b", r"\bspec\b", r"\bassert\b", r"\bpytest\b"],
        "docs": [r"\bdoc\b", r"\breadme\b", r"\bcomment\b", r"\bdocument\b"],
        "deploy": [r"\bdeploy\b", r"\bdocker\b", r"\bci\b", r"\bcd\b", r"\bpipeline\b", r"\bbuild\b"],
        "config": [r"\bconfig\b", r"\bsetting\b", r"\benv\b", r"\bsetup\b", r"\binstall\b"],
        "explain": [r"\bexplain\b", r"\bwhat is\b", r"\bhow does\b", r"\bwhy\b", r"\bunderstand\b"],
        "security": [r"\bsecurity\b", r"\bvulnerab\b", r"\bexploit\b", r"\bencrypt\b", r"\bauth\b", r"\bpermission\b"],
    }

    def __init__(self, conversations: List[Conversation]):
        self.conversations = conversations

    def compute_global_stats(self) -> GlobalStats:
        """Compute global statistics across all conversations."""
        stats = GlobalStats()
        stats.total_conversations = len(self.conversations)

        source_counter = Counter()
        model_counter = Counter()
        lang_counter = Counter()
        day_counter = Counter()
        hour_counter = Counter()

        for conv in self.conversations:
            if not conv.stats:
                conv.compute_stats()

            stats.total_messages += conv.stats.message_count
            stats.total_tokens += conv.stats.total_tokens
            stats.total_chars += conv.stats.total_chars
            stats.total_code_snippets += conv.stats.code_snippet_count
            stats.estimated_total_cost_usd += conv.stats.estimated_cost_usd or 0

            source_counter[conv.source] += 1
            if conv.model:
                model_counter[conv.model] += 1
            for lang in conv.stats.languages_used:
                lang_counter[lang] += 1

            if conv.created_at:
                try:
                    dt = datetime.fromisoformat(conv.created_at.replace("Z", "+00:00"))
                    day_counter[dt.strftime("%Y-%m-%d")] += 1
                    hour_counter[dt.hour] += 1
                except (ValueError, TypeError):
                    pass

        stats.conversations_by_source = dict(source_counter.most_common())
        stats.conversations_by_model = dict(model_counter.most_common(20))
        stats.languages_used = dict(lang_counter.most_common(20))
        stats.busiest_days = dict(day_counter.most_common(10))
        stats.busiest_hours = dict(sorted(hour_counter.items()))

        if stats.total_conversations > 0:
            stats.avg_messages_per_conversation = round(stats.total_messages / stats.total_conversations, 1)
            stats.avg_tokens_per_conversation = round(stats.total_tokens / stats.total_conversations, 1)

        stats.estimated_total_cost_usd = round(stats.estimated_total_cost_usd, 4)

        # Top conversations
        sorted_by_tokens = sorted(self.conversations, key=lambda c: c.stats.total_tokens if c.stats else 0, reverse=True)
        stats.top_conversations_by_tokens = [
            {"title": c.title, "source": c.source, "tokens": c.stats.total_tokens, "messages": c.stats.message_count}
            for c in sorted_by_tokens[:10] if c.stats
        ]

        sorted_by_messages = sorted(self.conversations, key=lambda c: c.stats.message_count if c.stats else 0, reverse=True)
        stats.top_conversations_by_messages = [
            {"title": c.title, "source": c.source, "messages": c.stats.message_count, "tokens": c.stats.total_tokens}
            for c in sorted_by_messages[:10] if c.stats
        ]

        return stats

    def classify_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Classify conversations by task type."""
        classified = defaultdict(list)

        for conv in self.conversations:
            task_types = self._detect_task_types(conv)
            for tt in task_types:
                classified[tt].append({
                    "id": conv.id,
                    "title": conv.title,
                    "source": conv.source,
                    "messages": conv.stats.message_count if conv.stats else 0,
                })

        return dict(classified)

    def _detect_task_types(self, conv: Conversation) -> List[str]:
        """Detect task types from conversation content."""
        full_text = " ".join(m.content.lower() for m in conv.messages[:5])  # Check first 5 messages
        detected = []
        for task_type, patterns in self.TASK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text):
                    detected.append(task_type)
                    break
        return detected or ["other"]

    def find_common_errors(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Find common error patterns across conversations."""
        error_patterns = [
            (r"(?:Error|Exception):\s*([^\n]+)", "error_message"),
            (r"(?:Traceback|Stack trace)[^\n]*\n([^\n]+)", "traceback"),
            (r"(?:Cannot|can't|unable to)\s+([^\n.,]+)", "capability_issue"),
            (r"(?:ModuleNotFoundError|ImportError):\s*([^\n]+)", "import_error"),
            (r"(?:TypeError|ValueError|KeyError|AttributeError):\s*([^\n]+)", "python_error"),
        ]

        error_counter = Counter()
        error_sources = defaultdict(set)

        for conv in self.conversations:
            for msg in conv.messages:
                content = msg.content or ""
                for pattern, error_type in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        key = f"{error_type}: {match.strip()[:100]}"
                        error_counter[key] += 1
                        error_sources[key].add(conv.source)

        return [
            {"pattern": k, "count": v, "sources": list(error_sources[k])}
            for k, v in error_counter.most_common(top_n)
        ]

    def generate_insights(self) -> Dict[str, Any]:
        """Generate human-readable insights from the data."""
        stats = self.compute_global_stats()
        tasks = self.classify_tasks()
        errors = self.find_common_errors(10)

        insights = {
            "summary": {
                "total_conversations": stats.total_conversations,
                "total_messages": stats.total_messages,
                "total_tokens": stats.total_tokens,
                "estimated_cost_usd": stats.estimated_total_cost_usd,
                "total_code_snippets": stats.total_code_snippets,
            },
            "top_sources": list(stats.conversations_by_source.items())[:5],
            "top_languages": list(stats.languages_used.items())[:10],
            "task_distribution": {k: len(v) for k, v in tasks.items()},
            "common_errors": errors[:5],
            "busiest_periods": {
                "days": list(stats.busiest_days.items())[:5],
                "hours": list(stats.busiest_hours.items())[:5],
            },
            "recommendations": self._generate_recommendations(stats, tasks, errors),
        }
        return insights

    def _generate_recommendations(self, stats: GlobalStats, tasks: dict, errors: list) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if stats.estimated_total_cost_usd > 10:
            recs.append(f"💸 累计API花费约 ${stats.estimated_total_cost_usd:.2f}，建议审查高频对话的token使用效率")

        if stats.avg_messages_per_conversation > 20:
            recs.append(f"📝 平均每轮对话 {stats.avg_messages_per_conversation:.0f} 条消息，考虑拆分复杂任务以提升效率")

        bug_count = len(tasks.get("bug_fix", []))
        if bug_count > stats.total_conversations * 0.3:
            recs.append(f"🐛 Bug修复类对话占比 {bug_count/stats.total_conversations*100:.0f}%，建议加强测试覆盖")

        if errors:
            recs.append(f"⚠️ 检测到 {len(errors)} 类常见错误模式，建议建立错误知识库避免重复踩坑")

        if len(stats.conversations_by_source) > 3:
            recs.append("🔄 跨多个AI工具使用，建议统一对话格式以便知识沉淀")

        if not recs:
            recs.append("✅ 对话数据健康，继续保持良好的编码协作习惯！")

        return recs
