<div align="center">

# 🌾 ChatHarvest

### AI Coding Conversation Harvest & Intelligence Engine

**Extract, analyze, search, and unlock value from your AI coding assistant conversations**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Zero%20Core%20Dependencies-✅-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-33%20Passing-brightgreen.svg)]()

[简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | English

</div>

---

## 🎉 Project Introduction

ChatHarvest is a powerful, zero-dependency Python tool that **harvests and analyzes your AI coding assistant conversations** across multiple platforms. Whether you use Claude Code, Cursor, Windsurf, Aider, Cline, ChatGPT, or Gemini — ChatHarvest unifies all your conversations into a single, searchable, analyzable knowledge base.

### 💡 Why ChatHarvest?

Every day, developers have hundreds of valuable conversations with AI assistants — debugging sessions, architecture decisions, code reviews, learning moments. But these conversations are **locked inside each tool**, scattered and unsearchable. ChatHarvest changes that:

- 🔓 **Unlock** your conversation data from siloed tools
- 🔍 **Search** across all platforms with TF-IDF full-text search
- 📊 **Analyze** token usage, costs, coding patterns, and task distribution
- 🧠 **Extract** code snippets, TODOs, decisions, commands, and error patterns
- 📦 **Export** to Markdown, JSON, HTML, PDF, or browse via a built-in Web UI

### 🌟 Inspiration

Born from the observation that developers lose thousands of dollars worth of AI-generated knowledge when switching tools or clearing chat history. ChatHarvest ensures your AI collaboration history becomes a **permanent, searchable asset**.

---

## ✨ Core Features

### 🔌 Multi-Platform Extraction
- **7+ supported platforms**: Claude Code, Cursor, Windsurf, Aider, Cline/Roo Code, ChatGPT, Google Gemini
- **Auto-detection** of default data paths for each platform
- **Smart deduplication** via content hashing — no duplicate conversations
- **Incremental extraction** — only process new data

### 🔍 Intelligent Search
- **TF-IDF full-text search** across all conversations and code snippets
- **Source filtering** — narrow results by platform
- **Date range filtering** — find conversations from specific time periods
- **Relevance scoring** with matched term highlighting
- **Zero external dependencies** — pure Python inverted index

### 📊 Deep Analytics
- **Global statistics**: total conversations, messages, tokens, estimated cost
- **Per-source breakdown**: see which tools you use most
- **Language usage tracking**: which programming languages appear in your chats
- **Task classification**: auto-detect bug fixes, features, refactors, tests, deployments, security
- **Common error patterns**: identify recurring issues across conversations
- **Busiest periods**: when you code most (by day and hour)
- **Actionable recommendations**: data-driven suggestions to improve your workflow

### 🧠 Knowledge Extraction
- **Code snippet extraction** with language detection and classification (code/config/command/query)
- **TODO/FIXME detection** — never lose track of pending tasks
- **Decision extraction** — capture architectural and technical decisions
- **Command harvesting** — collect useful shell commands
- **Error pattern mining** — build a personal error knowledge base
- **Key term extraction** — identify dominant technical topics

### 📦 Multi-Format Export
- **Markdown**: combined archive or per-conversation files
- **JSON**: structured data with full metadata
- **JSONL**: line-delimited for big data pipelines
- **HTML**: standalone, searchable archive with embedded viewer
- **PDF**: printable document (optional `reportlab` dependency)

### 🌐 Built-in Web UI
- **Zero-config dashboard** with statistics overview
- **Searchable conversation browser** with pagination
- **Full conversation viewer** with syntax-highlighted messages
- **Source filtering and sorting**
- **Runs locally** — your data never leaves your machine

### 🛡️ Privacy First
- **100% local processing** — no data sent to external servers
- **Zero core dependencies** — only Python standard library
- **Open source** — audit every line of code
- **MIT licensed** — use freely in personal and commercial projects

---

## 🚀 Quick Start

### 📋 Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **No external dependencies** for core functionality

### ⚙️ Installation

```bash
# Install from source (recommended)
git clone https://github.com/gitstq/chatharvest.git
cd chatharvest
pip install -e .

# Or install with PDF support
pip install -e ".[full]"

# Verify installation
chatharvest --version
```

### 🏃 One-Command Workflow

```bash
# 1. Extract conversations from Claude Code
chatharvest extract claude-code -o my_conversations.json

# 2. Analyze your conversations
chatharvest analyze -i my_conversations.json

# 3. Search for specific topics
chatharvest search -i my_conversations.json "docker compose"

# 4. Export to a searchable HTML archive
chatharvest export -i my_conversations.json -o archive.html --format html

# 5. Launch the Web UI dashboard
chatharvest web -i my_conversations.json --port 8080
```

### 🎯 Extract from All Platforms

```bash
# Claude Code (default: ~/.claude/projects)
chatharvest extract claude-code -o claude.json

# Cursor (default: ~/.cursor)
chatharvest extract cursor -o cursor.json

# Windsurf (default: ~/.windsurf)
chatharvest extract windsurf -o windsurf.json

# Aider (default: current directory)
chatharvest extract aider --path ~/projects/myapp -o aider.json

# Cline / Roo Code (default: ~/.vscode)
chatharvest extract cline -o cline.json

# ChatGPT (exported conversations.json)
chatharvest extract chatgpt --path ~/Downloads/conversations.json -o chatgpt.json

# Google Gemini (Takeout export)
chatharvest extract gemini --path ~/Downloads/Takeout -o gemini.json
```

---

## 📖 Detailed Usage Guide

### 🔧 CLI Commands Reference

#### `extract` — Extract Conversations

```bash
chatharvest extract <source> [--path PATH] [--output FILE] [--format FORMAT]
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `source` | Platform type (claude-code, cursor, windsurf, aider, cline, chatgpt, gemini) | Required |
| `--path, -p` | Path to data directory/file | Platform default |
| `--output, -o` | Output file path | stdout summary |
| `--format, -f` | Output format: json, jsonl, markdown, html, pdf | json |

#### `analyze` — Analyze Conversations

```bash
chatharvest analyze --input FILE [--output REPORT]
```

Generates a comprehensive analysis report including:
- Global statistics (conversations, messages, tokens, cost)
- Per-source and per-model breakdown
- Language usage distribution
- Task type classification
- Common error patterns
- Busiest coding periods
- Actionable recommendations

#### `search` — Search Conversations

```bash
chatharvest search --input FILE <query> [--limit N] [--source SOURCE]
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search terms | Required |
| `--limit, -n` | Maximum results | 20 |
| `--source, -s` | Filter by platform | All sources |

#### `export` — Export Conversations

```bash
chatharvest export --input FILE --output PATH --format FORMAT [--split]
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--format, -f` | json, jsonl, markdown, html, pdf | markdown |
| `--split` | Split markdown into per-conversation files | false |

#### `knowledge` — Extract Knowledge

```bash
chatharvest knowledge --input FILE [--output FILE]
```

Extracts structured knowledge: code snippets, TODOs, decisions, commands, errors, key terms.

#### `web` — Launch Web UI

```bash
chatharvest web [--input FILE] [--host HOST] [--port PORT]
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--host` | Bind address | 127.0.0.1 |
| `--port, -p` | Port number | 8765 |

#### `list` — List Extractors

```bash
chatharvest list
```

### 📁 Data Format

ChatHarvest uses a unified conversation format:

```json
{
  "id": "unique-id",
  "source": "claude-code",
  "title": "Conversation Title",
  "created_at": "2026-08-15T10:30:00Z",
  "model": "claude-sonnet-4",
  "messages": [
    {
      "role": "user",
      "content": "How do I...",
      "tokens_input": 25,
      "tokens_output": null,
      "code_snippets": []
    }
  ],
  "stats": {
    "message_count": 10,
    "total_tokens": 855,
    "estimated_cost_usd": 0.0119,
    "languages_used": ["python", "yaml"]
  }
}
```

### 🖼️ Web UI Screenshots

The Web UI provides a modern, dark-themed dashboard:

- **Statistics cards** showing key metrics at a glance
- **Search bar** with instant filtering
- **Conversation table** with source badges, message counts, token usage
- **Detail modal** with full conversation view
- **Responsive design** that works on desktop and mobile

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Design Principles

1. **Zero Core Dependencies**: The core engine uses only Python's standard library. No pip installs required for basic functionality.
2. **Privacy First**: All processing happens locally. Your conversation data never touches the internet.
3. **Unified Format**: Every platform's data is normalized into a single, consistent schema.
4. **Extensible Architecture**: New extractors are simple classes that inherit from `BaseExtractor`.
5. **Developer Friendly**: Clean CLI, clear output, meaningful error messages.

### 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **Language** | Python 3.8+ | Ubiquitous, great for data processing |
| **Core Engine** | Python Stdlib | Zero dependencies, maximum compatibility |
| **Search** | Custom TF-IDF | Lightweight, no external search engine needed |
| **Web UI** | Stdlib HTTP + Vanilla JS | No build step, runs anywhere |
| **Testing** | pytest | Industry standard, easy to extend |
| **Packaging** | setuptools + pyproject.toml | Modern Python packaging |

### 🗺️ Roadmap

#### ✅ v1.0.0 (Current)
- [x] 7+ platform extractors
- [x] TF-IDF full-text search
- [x] Comprehensive analytics engine
- [x] Knowledge extraction (snippets, TODOs, decisions, commands, errors)
- [x] Multi-format export (JSON, JSONL, Markdown, HTML, PDF)
- [x] Built-in Web UI dashboard
- [x] Smart deduplication
- [x] 33 unit tests, all passing
- [x] Zero core dependencies

#### 🔜 v1.1.0 (Planned)
- [ ] Continue conversation extraction (resume from last checkpoint)
- [ ] Conversation tagging and categorization
- [ ] Cost comparison across platforms
- [ ] Code snippet deduplication across conversations
- [ ] Anki card export for spaced repetition
- [ ] More platform support (Zed, Continue.dev, Codeium)

#### 🔮 v2.0.0 (Future)
- [ ] Local LLM-powered conversation summarization
- [ ] Semantic search (embeddings-based)
- [ ] Knowledge graph generation
- [ ] Multi-user team knowledge base
- [ ] Plugin system for custom extractors and analyzers

### 🤝 Community Contribution Areas

We welcome contributions in:
- **New extractors**: Support for more AI coding tools
- **Better analysis**: New metrics, visualizations, insights
- **Documentation**: Tutorials, examples, translations
- **Testing**: More test coverage, edge cases
- **Performance**: Optimize for large conversation datasets

---

## 📦 Packaging & Deployment

### 🐍 Python Package

```bash
# Build the package
python -m build

# Install locally
pip install dist/chatharvest-1.0.0-py3-none-any.whl

# Run
chatharvest --help
```

### 📦 Standalone Executable (Optional)

Using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --name chatharvest chatharvest/__main__.py
# Output: dist/chatharvest (or chatharvest.exe on Windows)
```

### 🐳 Docker (Optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
VOLUME /data
EXPOSE 8765
ENTRYPOINT ["chatharvest"]
```

```bash
docker build -t chatharvest .
docker run -v ~/.claude:/root/.claude -p 8765:8765 chatharvest web --host 0.0.0.0
```

### 🔧 Compatible Environments

| Environment | Status | Notes |
|-------------|--------|-------|
| **Python 3.8-3.12** | ✅ Fully supported | Core functionality |
| **Windows 10/11** | ✅ Supported | Paths auto-adjusted |
| **macOS 12+** | ✅ Supported | Default paths configured |
| **Linux (all distros)** | ✅ Supported | Primary development platform |
| **Docker** | ✅ Supported | Via optional Dockerfile |
| **PDF Export** | ⚠️ Optional | Requires `pip install reportlab` |

---

## 🤝 Contributing

We welcome contributions from everyone! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick steps:**
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a Pull Request

### 📐 Pull Request Format

Use Conventional Commits for PR titles:
- `feat: add new extractor for X`
- `fix: resolve token counting bug`
- `docs: update installation guide`
- `refactor: optimize search performance`

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 ChatHarvest Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">

**Made with 🌾 by developers, for developers**

[⭐ Star this repo](https://github.com/gitstq/chatharvest) · [🐛 Report Issues](https://github.com/gitstq/chatharvest/issues) · [🤝 Contribute](CONTRIBUTING.md)

</div>
