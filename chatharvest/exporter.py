"""
ChatHarvest Exporter - Multi-format conversation export engine.
Supports Markdown, JSON, HTML, PDF, and Anki card export.
"""

import os
import json
import html
from datetime import datetime
from typing import List, Dict, Any, Optional

from chatharvest.models import Conversation, Message
from chatharvest.analyzer import GlobalStats


class ConversationExporter:
    """Exports conversations to multiple formats."""

    def __init__(self, conversations: List[Conversation], stats: Optional[GlobalStats] = None):
        self.conversations = conversations
        self.stats = stats

    def export_markdown(self, output_path: str, single_file: bool = True) -> List[str]:
        """
        Export conversations to Markdown.

        Args:
            output_path: Output file or directory path
            single_file: If True, export all to one file; else one file per conversation
        """
        if single_file:
            content = self._generate_combined_markdown()
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return [output_path]
        else:
            os.makedirs(output_path, exist_ok=True)
            files = []
            for i, conv in enumerate(self.conversations):
                safe_title = self._sanitize_filename(conv.title)
                filepath = os.path.join(output_path, f"{i+1:04d}_{safe_title}.md")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self._generate_single_markdown(conv))
                files.append(filepath)
            return files

    def export_json(self, output_path: str, pretty: bool = True) -> str:
        """Export conversations to JSON."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "count": len(self.conversations),
            "conversations": [conv.to_dict() for conv in self.conversations],
        }
        if self.stats:
            data["global_stats"] = self.stats.to_dict()

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            else:
                json.dump(data, f, ensure_ascii=False, default=str)
        return output_path

    def export_jsonl(self, output_path: str) -> str:
        """Export conversations to JSONL (one JSON per line)."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for conv in self.conversations:
                f.write(json.dumps(conv.to_dict(), ensure_ascii=False, default=str) + "\n")
        return output_path

    def export_html(self, output_path: str) -> str:
        """Export conversations to a standalone HTML file with search."""
        content = self._generate_html()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

    def export_pdf(self, output_path: str) -> str:
        """Export conversations to PDF (requires reportlab)."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_LEFT
        except ImportError:
            raise ImportError("PDF export requires reportlab. Install with: pip install reportlab")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=12)
        h2_style = ParagraphStyle('CustomH2', parent=styles['Heading2'], fontSize=14, spaceAfter=8)
        body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], fontSize=10, leading=14)
        code_style = ParagraphStyle('CustomCode', parent=styles['Code'], fontSize=8, leading=10)

        story = []
        story.append(Paragraph("ChatHarvest - Conversation Export", title_style))
        story.append(Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
        story.append(Paragraph(f"Total conversations: {len(self.conversations)}", body_style))
        story.append(Spacer(1, 0.5*cm))

        for i, conv in enumerate(self.conversations):
            story.append(Paragraph(f"{i+1}. {html.escape(conv.title)}", h2_style))
            story.append(Paragraph(f"Source: {conv.source} | Messages: {len(conv.messages)}", body_style))
            story.append(Spacer(1, 0.3*cm))

            for msg in conv.messages[:50]:  # Limit messages per conversation in PDF
                role_text = msg.role.capitalize()
                safe_content = html.escape(msg.content or "")[:2000]
                story.append(Paragraph(f"<b>{role_text}:</b> {safe_content}", body_style))
                story.append(Spacer(1, 0.1*cm))

            if len(conv.messages) > 50:
                story.append(Paragraph(f"... ({len(conv.messages) - 50} more messages)", body_style))

            story.append(PageBreak())

        doc.build(story)
        return output_path

    def _generate_combined_markdown(self) -> str:
        """Generate combined markdown for all conversations."""
        lines = [
            "# 🌾 ChatHarvest - Conversation Archive",
            "",
            f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Conversations:** {len(self.conversations)}",
            "",
        ]

        if self.stats:
            lines.extend([
                "## 📊 Global Statistics",
                "",
                f"- **Total Messages:** {self.stats.total_messages}",
                f"- **Total Tokens:** {self.stats.total_tokens:,}",
                f"- **Estimated Cost:** ${self.stats.estimated_total_cost_usd:.4f}",
                f"- **Code Snippets:** {self.stats.total_code_snippets}",
                "",
            ])

        lines.append("## 📑 Table of Contents")
        lines.append("")
        for i, conv in enumerate(self.conversations):
            anchor = self._markdown_anchor(conv.title)
            lines.append(f"{i+1}. [{conv.title}](#{anchor}) ({conv.source})")
        lines.append("")
        lines.append("---")
        lines.append("")

        for i, conv in enumerate(self.conversations):
            lines.extend(self._generate_single_markdown(conv, index=i+1))
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_single_markdown(self, conv: Conversation, index: Optional[int] = None) -> List[str]:
        """Generate markdown for a single conversation."""
        prefix = f"{index}. " if index else ""
        lines = [
            f"## {prefix}{conv.title}",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Source** | {conv.source} |",
            f"| **Messages** | {len(conv.messages)} |",
            f"| **Created** | {conv.created_at or 'N/A'} |",
            f"| **Model** | {conv.model or 'N/A'} |",
        ]
        if conv.stats:
            lines.append(f"| **Tokens** | {conv.stats.total_tokens:,} |")
            lines.append(f"| **Est. Cost** | ${conv.stats.estimated_cost_usd or 0:.4f} |")
        lines.append("")
        lines.append("### Conversation")
        lines.append("")

        for msg in conv.messages:
            role_emoji = "🧑" if msg.role == "user" else "🤖" if msg.role == "assistant" else "⚙️"
            lines.append(f"**{role_emoji} {msg.role.capitalize()}**")
            lines.append("")
            content = msg.content or ""
            # Truncate very long messages
            if len(content) > 5000:
                content = content[:5000] + "\n\n... (truncated)"
            lines.append(content)
            lines.append("")

        return lines

    def _generate_html(self) -> str:
        """Generate a standalone HTML file with embedded data and search."""
        conversations_json = json.dumps([conv.to_dict() for conv in self.conversations], ensure_ascii=False, default=str)
        stats_json = json.dumps(self.stats.to_dict() if self.stats else {}, ensure_ascii=False, default=str)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌾 ChatHarvest - Conversation Archive</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #1e293b; margin-bottom: 30px; }}
header h1 {{ font-size: 2.5em; color: #fbbf24; margin-bottom: 10px; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0; }}
.stat-card {{ background: #1e293b; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #334155; }}
.stat-card .value {{ font-size: 2em; font-weight: bold; color: #fbbf24; }}
.stat-card .label {{ color: #94a3b8; font-size: 0.9em; margin-top: 5px; }}
.search-bar {{ margin: 20px 0; }}
.search-bar input {{ width: 100%; padding: 15px 20px; font-size: 1.1em; background: #1e293b; border: 2px solid #334155; border-radius: 12px; color: #e2e8f0; outline: none; }}
.search-bar input:focus {{ border-color: #fbbf24; }}
.filters {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
.filters select {{ padding: 8px 15px; background: #1e293b; border: 1px solid #334155; border-radius: 8px; color: #e2e8f0; cursor: pointer; }}
.conv-list {{ list-style: none; }}
.conv-item {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #334155; cursor: pointer; transition: all 0.2s; }}
.conv-item:hover {{ border-color: #fbbf24; transform: translateY(-2px); }}
.conv-item h3 {{ color: #fbbf24; margin-bottom: 8px; }}
.conv-meta {{ display: flex; gap: 15px; font-size: 0.85em; color: #94a3b8; flex-wrap: wrap; }}
.conv-meta span {{ background: #0f172a; padding: 3px 10px; border-radius: 20px; }}
.modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto; }}
.modal-content {{ background: #1e293b; max-width: 900px; margin: 30px auto; padding: 30px; border-radius: 16px; border: 1px solid #334155; }}
.modal-close {{ float: right; font-size: 1.5em; cursor: pointer; color: #94a3b8; }}
.modal-close:hover {{ color: #fbbf24; }}
.message {{ margin: 15px 0; padding: 15px; border-radius: 8px; }}
.message.user {{ background: #1e3a5f; border-left: 4px solid #3b82f6; }}
.message.assistant {{ background: #1a2e1a; border-left: 4px solid #22c55e; }}
.message .role {{ font-weight: bold; margin-bottom: 8px; }}
.message pre {{ background: #0f172a; padding: 12px; border-radius: 6px; overflow-x: auto; margin-top: 8px; font-size: 0.85em; }}
.highlight {{ background: #fbbf24; color: #0f172a; padding: 1px 4px; border-radius: 3px; }}
</style>
</head>
<body>
<div class="container">
<header>
<h1>🌾 ChatHarvest</h1>
<p>AI Coding Conversation Archive & Intelligence</p>
</header>
<div class="stats-grid" id="statsGrid"></div>
<div class="search-bar">
<input type="text" id="searchInput" placeholder="🔍 Search conversations...">
</div>
<div class="filters">
<select id="sourceFilter"><option value="">All Sources</option></select>
<select id="sortBy"><option value="date">Sort by Date</option><option value="messages">Sort by Messages</option><option value="tokens">Sort by Tokens</option></select>
</div>
<ul class="conv-list" id="convList"></ul>
</div>
<div class="modal" id="modal">
<div class="modal-content">
<span class="modal-close" onclick="closeModal()">&times;</span>
<div id="modalBody"></div>
</div>
</div>
<script>
const conversations = {conversations_json};
const stats = {stats_json};

function renderStats() {{
const grid = document.getElementById('statsGrid');
const items = [
{{value: stats.total_conversations || conversations.length, label: 'Conversations'}},
{{value: (stats.total_messages || 0).toLocaleString(), label: 'Messages'}},
{{value: (stats.total_tokens || 0).toLocaleString(), label: 'Tokens'}},
{{value: '$' + (stats.estimated_total_cost_usd || 0).toFixed(2), label: 'Est. Cost'}},
];
grid.innerHTML = items.map(i => `<div class="stat-card"><div class="value">${{i.value}}</div><div class="label">${{i.label}}</div></div>`).join('');
}}

function renderList(filtered) {{
const list = document.getElementById('convList');
list.innerHTML = filtered.map((c, i) => `
<li class="conv-item" onclick="openModal('${{c.id}}')">
<h3>${{c.title}}</h3>
<div class="conv-meta">
<span>📡 ${{c.source}}</span>
<span>💬 ${{c.stats ? c.stats.message_count : c.messages.length}} msgs</span>
<span>🔢 ${{c.stats ? c.stats.total_tokens.toLocaleString() : 0}} tokens</span>
<span>📅 ${{c.created_at ? c.created_at.substring(0,10) : 'N/A'}}</span>
</div>
</li>`).join('');
}}

function filterConversations() {{
const query = document.getElementById('searchInput').value.toLowerCase();
const source = document.getElementById('sourceFilter').value;
const sortBy = document.getElementById('sortBy').value;
let filtered = conversations.filter(c => {{
const matchQuery = !query || c.title.toLowerCase().includes(query) ||
c.messages.some(m => (m.content||'').toLowerCase().includes(query));
const matchSource = !source || c.source === source;
return matchQuery && matchSource;
}});
filtered.sort((a,b) => {{
if (sortBy === 'messages') return (b.stats?b.stats.message_count:0) - (a.stats?a.stats.message_count:0);
if (sortBy === 'tokens') return (b.stats?b.stats.total_tokens:0) - (a.stats?a.stats.total_tokens:0);
return (b.created_at||'').localeCompare(a.created_at||'');
}});
renderList(filtered);
}}

function openModal(id) {{
const conv = conversations.find(c => c.id === id);
if (!conv) return;
const body = document.getElementById('modalBody');
body.innerHTML = `<h2 style="color:#fbbf24;margin-bottom:15px">${{conv.title}}</h2>
<div class="conv-meta" style="margin-bottom:20px">
<span>📡 ${{conv.source}}</span>
<span>🤖 ${{conv.model || 'N/A'}}</span>
<span>📅 ${{conv.created_at || 'N/A'}}</span>
</div>` + conv.messages.map(m => `
<div class="message ${{m.role}}">
<div class="role">${{m.role === 'user' ? '🧑 User' : m.role === 'assistant' ? '🤖 Assistant' : '⚙️ ' + m.role}}</div>
<div>${{(m.content||'').replace(/\\n/g, '<br>')}}</div>
</div>`).join('');
document.getElementById('modal').style.display = 'block';
}}

function closeModal() {{ document.getElementById('modal').style.display = 'none'; }}

document.getElementById('searchInput').addEventListener('input', filterConversations);
document.getElementById('sourceFilter').addEventListener('change', filterConversations);
document.getElementById('sortBy').addEventListener('change', filterConversations);
document.getElementById('modal').addEventListener('click', e => {{ if(e.target.id==='modal') closeModal(); }});

// Populate source filter
const sources = [...new Set(conversations.map(c => c.source))];
document.getElementById('sourceFilter').innerHTML = '<option value="">All Sources</option>' +
sources.map(s => `<option value="${{s}}">${{s}}</option>`).join('');

renderStats();
renderList(conversations);
</script>
</body>
</html>"""

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use as a filename."""
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip('. ')
        return name[:80] or "untitled"

    def _markdown_anchor(self, text: str) -> str:
        """Generate a markdown anchor from text."""
        import re
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[\s_]+', '-', anchor)
        return anchor.strip('-')


import re
