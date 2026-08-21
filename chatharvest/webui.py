"""
ChatHarvest Web UI - Lightweight HTTP server for conversation browsing.
Zero external dependencies - uses Python's built-in http.server.
"""

import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

from chatharvest.models import Conversation
from chatharvest.analyzer import ConversationAnalyzer
from chatharvest.searcher import ConversationSearcher


class WebUIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web UI."""

    conversations: List[Conversation] = []
    searcher: ConversationSearcher = None
    analyzer: ConversationAnalyzer = None
    stats = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200):
        """Send HTML response."""
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self._serve_index()
        elif path == "/api/stats":
            self._api_stats()
        elif path == "/api/conversations":
            self._api_conversations(params)
        elif path == "/api/conversation":
            self._api_conversation_detail(params)
        elif path == "/api/search":
            self._api_search(params)
        elif path == "/api/sources":
            self._api_sources()
        else:
            self.send_error(404)

    def _serve_index(self):
        """Serve the main HTML page."""
        html = self._get_index_html()
        self._send_html(html)

    def _api_stats(self):
        """Return global statistics."""
        if not self.stats:
            self.analyzer = ConversationAnalyzer(self.conversations)
            self.stats = self.analyzer.compute_global_stats()
        self._send_json(self.stats.to_dict())

    def _api_conversations(self, params):
        """Return conversation list with pagination."""
        page = int(params.get("page", [1])[0])
        per_page = int(params.get("per_page", [50])[0])
        source = params.get("source", [None])[0]
        sort = params.get("sort", ["date"])[0]

        filtered = self.conversations
        if source:
            filtered = [c for c in filtered if c.source == source]

        if sort == "messages":
            filtered = sorted(filtered, key=lambda c: c.stats.message_count if c.stats else 0, reverse=True)
        elif sort == "tokens":
            filtered = sorted(filtered, key=lambda c: c.stats.total_tokens if c.stats else 0, reverse=True)
        else:
            filtered = sorted(filtered, key=lambda c: c.created_at or "", reverse=True)

        start = (page - 1) * per_page
        end = start + per_page
        page_items = filtered[start:end]

        result = {
            "total": len(filtered),
            "page": page,
            "per_page": per_page,
            "items": [self._conv_summary(c) for c in page_items],
        }
        self._send_json(result)

    def _api_conversation_detail(self, params):
        """Return full conversation detail."""
        conv_id = params.get("id", [""])[0]
        for conv in self.conversations:
            if conv.id == conv_id:
                self._send_json(conv.to_dict())
                return
        self._send_json({"error": "Not found"}, status=404)

    def _api_search(self, params):
        """Search conversations."""
        query = params.get("q", [""])[0]
        source = params.get("source", [None])[0]
        limit = int(params.get("limit", [20])[0])

        if not self.searcher:
            self.searcher = ConversationSearcher(self.conversations)

        results = self.searcher.search(query, limit=limit, source_filter=source)
        self._send_json([r.to_dict() for r in results])

    def _api_sources(self):
        """Return list of sources."""
        sources = list(set(c.source for c in self.conversations))
        self._send_json(sorted(sources))

    def _conv_summary(self, conv: Conversation) -> Dict[str, Any]:
        """Get a summary of a conversation."""
        if not conv.stats:
            conv.compute_stats()
        return {
            "id": conv.id,
            "title": conv.title,
            "source": conv.source,
            "messages": conv.stats.message_count,
            "tokens": conv.stats.total_tokens,
            "created_at": conv.created_at,
            "model": conv.model,
            "cost": conv.stats.estimated_cost_usd,
        }

    def _get_index_html(self) -> str:
        """Get the main HTML page content."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌾 ChatHarvest - Conversation Intelligence</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.6}
.header{background:linear-gradient(135deg,#1e293b,#0f172a);padding:30px 40px;border-bottom:2px solid #fbbf24;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:1.8em;color:#fbbf24}
.header .subtitle{color:#94a3b8;font-size:0.9em}
.container{max-width:1400px;margin:0 auto;padding:20px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin-bottom:25px}
.stat-card{background:#1e293b;border-radius:12px;padding:20px;text-align:center;border:1px solid #334155;transition:transform .2s}
.stat-card:hover{transform:translateY(-3px);border-color:#fbbf24}
.stat-card .value{font-size:1.8em;font-weight:bold;color:#fbbf24}
.stat-card .label{color:#94a3b8;font-size:0.85em;margin-top:5px}
.toolbar{display:flex;gap:15px;margin-bottom:20px;flex-wrap:wrap;align-items:center}
.toolbar input{flex:1;min-width:250px;padding:12px 18px;font-size:1em;background:#1e293b;border:2px solid #334155;border-radius:10px;color:#e2e8f0;outline:none;transition:border-color .2s}
.toolbar input:focus{border-color:#fbbf24}
.toolbar select{padding:12px 15px;background:#1e293b;border:2px solid #334155;border-radius:10px;color:#e2e8f0;cursor:pointer;outline:none}
.conv-table{width:100%;border-collapse:collapse}
.conv-table th{background:#1e293b;padding:12px 15px;text-align:left;color:#fbbf24;font-size:0.9em;border-bottom:2px solid #334155}
.conv-table td{padding:12px 15px;border-bottom:1px solid #1e293b}
.conv-table tr{cursor:pointer;transition:background .15s}
.conv-table tr:hover{background:#1e293b}
.source-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.75em;font-weight:600}
.source-claude-code{background:#d97757;color:#fff}
.source-cursor{background:#000;color:#fff}
.source-windsurf{background:#7c3aed;color:#fff}
.source-aider{background:#059669;color:#fff}
.source-cline{background:#dc2626;color:#fff}
.source-chatgpt{background:#10a37f;color:#fff}
.source-gemini{background:#4285f4;color:#fff}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.85);z-index:1000;overflow-y:auto}
.modal-content{background:#1e293b;max-width:1000px;margin:30px auto;padding:30px;border-radius:16px;border:1px solid #334155}
.modal-close{float:right;font-size:1.8em;cursor:pointer;color:#94a3b8;transition:color .2s}
.modal-close:hover{color:#fbbf24}
.message{margin:12px 0;padding:15px 18px;border-radius:10px}
.message.user{background:#1e3a5f;border-left:4px solid #3b82f6}
.message.assistant{background:#1a2e1a;border-left:4px solid #22c55e}
.message.system{background:#3b3b1e;border-left:4px solid #eab308}
.message .role{font-weight:700;margin-bottom:8px;font-size:0.9em}
.message .content{white-space:pre-wrap;word-break:break-word;font-size:0.92em}
.message pre{background:#0f172a;padding:12px;border-radius:6px;overflow-x:auto;margin-top:8px;font-size:0.82em}
.pagination{display:flex;justify-content:center;gap:10px;margin-top:25px}
.pagination button{padding:8px 16px;background:#1e293b;border:1px solid #334155;border-radius:8px;color:#e2e8f0;cursor:pointer;transition:all .2s}
.pagination button:hover:not(:disabled){border-color:#fbbf24;color:#fbbf24}
.pagination button:disabled{opacity:.4;cursor:not-allowed}
.pagination .active{background:#fbbf24;color:#0f172a;border-color:#fbbf24}
.loading{text-align:center;padding:40px;color:#94a3b8}
</style>
</head>
<body>
<div class="header">
<div><h1>🌾 ChatHarvest</h1><div class="subtitle">AI Coding Conversation Harvest & Intelligence Engine</div></div>
<div class="subtitle" id="convCount">Loading...</div>
</div>
<div class="container">
<div class="stats-grid" id="statsGrid"></div>
<div class="toolbar">
<input type="text" id="searchInput" placeholder="🔍 Search conversations...">
<select id="sourceFilter"><option value="">All Sources</option></select>
<select id="sortBy"><option value="date">Sort: Date</option><option value="messages">Sort: Messages</option><option value="tokens">Sort: Tokens</option></select>
</div>
<table class="conv-table">
<thead><tr><th>Title</th><th>Source</th><th>Messages</th><th>Tokens</th><th>Cost</th><th>Date</th></tr></thead>
<tbody id="convBody"></tbody>
</table>
<div class="pagination" id="pagination"></div>
</div>
<div class="modal" id="modal">
<div class="modal-content">
<span class="modal-close" onclick="closeModal()">&times;</span>
<div id="modalBody"></div>
</div>
</div>
<script>
let allConversations=[],currentPage=1,perPage=50,filtered=[];
async function init(){
const[stats,sources]=await Promise.all([fetch('/api/stats').then(r=>r.json()),fetch('/api/sources').then(r=>r.json())]);
renderStats(stats);
document.getElementById('convCount').textContent=stats.total_conversations+' conversations';
const sf=document.getElementById('sourceFilter');
sources.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;sf.appendChild(o)});
await loadConversations();
document.getElementById('searchInput').addEventListener('input',debounce(filterConversations,300));
document.getElementById('sourceFilter').addEventListener('change',()=>{currentPage=1;filterConversations()});
document.getElementById('sortBy').addEventListener('change',()=>{currentPage=1;filterConversations()});
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id==='modal')closeModal()});
}
function renderStats(s){
const items=[['📁',s.total_conversations,'Conversations'],['💬',s.total_messages?.toLocaleString(),'Messages'],['🔢',s.total_tokens?.toLocaleString(),'Tokens'],['💸','$'+(s.estimated_total_cost_usd||0).toFixed(2),'Est. Cost'],['💻',s.total_code_snippets,'Code Snippets'],['📊',s.avg_messages_per_conversation,'Avg Msgs/Conv']];
document.getElementById('statsGrid').innerHTML=items.map(([e,v,l])=>`<div class="stat-card"><div class="value">${e} ${v}</div><div class="label">${l}</div></div>`).join('');
}
async function loadConversations(){
const res=await fetch(`/api/conversations?page=${currentPage}&per_page=1000`);
const data=await res.json();
allConversations=data.items;
filtered=allConversations;
renderTable();
}
function filterConversations(){
const q=document.getElementById('searchInput').value.toLowerCase();
const src=document.getElementById('sourceFilter').value;
const sort=document.getElementById('sortBy').value;
filtered=allConversations.filter(c=>{
const mq=!q||c.title.toLowerCase().includes(q);
const ms=!src||c.source===src;
return mq&&ms;
});
filtered.sort((a,b)=>{
if(sort==='messages')return b.messages-a.messages;
if(sort==='tokens')return b.tokens-a.tokens;
return (b.created_at||'').localeCompare(a.created_at||'');
});
currentPage=1;renderTable();
}
function renderTable(){
const start=(currentPage-1)*perPage;
const page=filtered.slice(start,start+perPage);
const tbody=document.getElementById('convBody');
tbody.innerHTML=page.map(c=>`<tr onclick="openConv('${c.id}')">
<td><strong>${esc(c.title)}</strong></td>
<td><span class="source-badge source-${c.source}">${c.source}</span></td>
<td>${c.messages}</td>
<td>${(c.tokens||0).toLocaleString()}</td>
<td>$${(c.cost||0).toFixed(4)}</td>
<td>${c.created_at?c.created_at.substring(0,10):'N/A'}</td>
</tr>`).join('');
renderPagination();
}
function renderPagination(){
const total=Math.ceil(filtered.length/perPage);
const pg=document.getElementById('pagination');
if(total<=1){pg.innerHTML='';return}
let html=`<button onclick="goPage(${currentPage-1})" ${currentPage===1?'disabled':''}>◀ Prev</button>`;
for(let i=1;i<=Math.min(total,7);i++){
if(i===1||i===total||Math.abs(i-currentPage)<=2){
html+=`<button class="${i===currentPage?'active':''}" onclick="goPage(${i})">${i}</button>`;
}else if(Math.abs(i-currentPage)===3){html+='<span style="padding:8px">...</span>';}
}
html+=`<button onclick="goPage(${currentPage+1})" ${currentPage===total?'disabled':''}>Next ▶</button>`;
pg.innerHTML=html;
}
function goPage(p){currentPage=p;renderTable();window.scrollTo(0,0)}
async function openConv(id){
const res=await fetch('/api/conversation?id='+id);
const conv=await res.json();
const body=document.getElementById('modalBody');
body.innerHTML=`<h2 style="color:#fbbf24;margin-bottom:15px">${esc(conv.title)}</h2>
<div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
<span class="source-badge source-${conv.source}">${conv.source}</span>
<span style="color:#94a3b8">🤖 ${conv.model||'N/A'}</span>
<span style="color:#94a3b8">📅 ${conv.created_at||'N/A'}</span>
<span style="color:#94a3b8">💬 ${conv.messages?.length||0} messages</span>
<span style="color:#94a3b8">🔢 ${(conv.stats?.total_tokens||0).toLocaleString()} tokens</span>
</div>`+ (conv.messages||[]).map(m=>`
<div class="message ${m.role}">
<div class="role">${m.role==='user'?'🧑 User':m.role==='assistant'?'🤖 Assistant':'⚙️ '+m.role}</div>
<div class="content">${esc(m.content||'')}</div>
</div>`).join('');
document.getElementById('modal').style.display='block';
}
function closeModal(){document.getElementById('modal').style.display='none'}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function debounce(f,ms){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>f(...a),ms)}}
init();
</script>
</body>
</html>"""


def start_webui(conversations: List[Conversation], host: str = "127.0.0.1", port: int = 8765):
    """Start the web UI server."""
    WebUIHandler.conversations = conversations
    if conversations:
        WebUIHandler.searcher = ConversationSearcher(conversations)
        WebUIHandler.analyzer = ConversationAnalyzer(conversations)
        WebUIHandler.stats = WebUIHandler.analyzer.compute_global_stats()

    server = HTTPServer((host, port), WebUIHandler)
    print(f"   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.server_close()
