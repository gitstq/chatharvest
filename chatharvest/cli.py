"""
ChatHarvest CLI - Command-line interface for conversation harvesting.
"""

import argparse
import json
import os
import sys
from typing import List, Optional

from chatharvest import __version__
from chatharvest.extractors import list_extractors, get_extractor, EXTRACTOR_REGISTRY
from chatharvest.models import Conversation
from chatharvest.analyzer import ConversationAnalyzer
from chatharvest.searcher import ConversationSearcher
from chatharvest.knowledge import KnowledgeExtractor
from chatharvest.exporter import ConversationExporter


def print_banner():
    """Print the ChatHarvest banner."""
    banner = """
╔══════════════════════════════════════════════════╗
║  🌾 ChatHarvest v{version}                           ║
║  AI Coding Conversation Harvest & Intelligence    ║
╚══════════════════════════════════════════════════╝
""".format(version=__version__)
    print(banner)


def cmd_extract(args):
    """Extract conversations from a source."""
    source = args.source
    path = args.path
    output = args.output
    format_type = args.format

    print(f"📡 Extracting from: {source}")
    if path:
        print(f"📂 Path: {path}")

    extractor = get_extractor(source)
    if not extractor:
        print(f"❌ Unknown source: {source}")
        print(f"   Available sources: {', '.join(list_extractors())}")
        sys.exit(1)

    conversations = extractor.extract(path)
    print(f"✅ Extracted {len(conversations)} conversations")

    if not conversations:
        print("⚠️  No conversations found. Check the path and source.")
        return

    if output:
        exporter = ConversationExporter(conversations)
        if format_type == "json":
            filepath = exporter.export_json(output)
        elif format_type == "jsonl":
            filepath = exporter.export_jsonl(output)
        elif format_type == "markdown":
            filepath = exporter.export_markdown(output, single_file=True)
            filepath = filepath[0] if isinstance(filepath, list) else filepath
        elif format_type == "html":
            filepath = exporter.export_html(output)
        elif format_type == "pdf":
            filepath = exporter.export_pdf(output)
        else:
            filepath = exporter.export_json(output)
        print(f"💾 Exported to: {filepath}")
    else:
        # Print summary
        for i, conv in enumerate(conversations[:20]):
            stats = conv.stats or conv.compute_stats()
            print(f"  {i+1}. [{conv.source}] {conv.title}")
            print(f"     💬 {stats.message_count} msgs | 🔢 {stats.total_tokens} tokens | 📅 {conv.created_at or 'N/A'}")
        if len(conversations) > 20:
            print(f"  ... and {len(conversations) - 20} more")


def cmd_analyze(args):
    """Analyze extracted conversations."""
    input_file = args.input

    print("📊 Loading conversations...")
    conversations = _load_conversations(input_file)
    if not conversations:
        print("❌ No conversations loaded")
        sys.exit(1)

    print(f"✅ Loaded {len(conversations)} conversations")
    print()

    analyzer = ConversationAnalyzer(conversations)
    stats = analyzer.compute_global_stats()

    print("=" * 60)
    print("📊 GLOBAL STATISTICS")
    print("=" * 60)
    print(f"  📁 Total Conversations: {stats.total_conversations}")
    print(f"  💬 Total Messages: {stats.total_messages:,}")
    print(f"  🔢 Total Tokens: {stats.total_tokens:,}")
    print(f"  💸 Estimated Cost: ${stats.estimated_total_cost_usd:.4f}")
    print(f"  💻 Code Snippets: {stats.total_code_snippets}")
    print(f"  📊 Avg Messages/Conv: {stats.avg_messages_per_conversation}")
    print(f"  🔢 Avg Tokens/Conv: {stats.avg_tokens_per_conversation:,.0f}")
    print()

    print("📡 BY SOURCE:")
    for source, count in stats.conversations_by_source.items():
        print(f"  {source}: {count}")
    print()

    print("💻 TOP LANGUAGES:")
    for lang, count in list(stats.languages_used.items())[:10]:
        print(f"  {lang}: {count} conversations")
    print()

    # Task classification
    tasks = analyzer.classify_tasks()
    print("🏷️  TASK DISTRIBUTION:")
    for task_type, convs in sorted(tasks.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {task_type}: {len(convs)} conversations")
    print()

    # Insights & recommendations
    insights = analyzer.generate_insights()
    print("💡 RECOMMENDATIONS:")
    for rec in insights["recommendations"]:
        print(f"  {rec}")
    print()

    # Export if requested
    if args.output:
        data = {
            "global_stats": stats.to_dict(),
            "task_distribution": {k: len(v) for k, v in tasks.items()},
            "insights": insights,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Analysis report saved to: {args.output}")


def cmd_search(args):
    """Search conversations."""
    input_file = args.input
    query = args.query
    limit = args.limit
    source_filter = args.source

    print(f"🔍 Searching: '{query}'")
    conversations = _load_conversations(input_file)
    if not conversations:
        print("❌ No conversations loaded")
        sys.exit(1)

    searcher = ConversationSearcher(conversations)
    results = searcher.search(query, limit=limit, source_filter=source_filter)

    print(f"✅ Found {len(results)} results")
    print()
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result.conversation.source}] {result.conversation.title}")
        print(f"     Score: {result.score:.4f} | Terms: {', '.join(result.matched_terms)}")
        if result.highlight_snippet:
            print(f"     ...{result.highlight_snippet}...")
        print()


def cmd_export(args):
    """Export conversations to various formats."""
    input_file = args.input
    output = args.output
    format_type = args.format

    print(f"📦 Exporting to {format_type.upper()}: {output}")
    conversations = _load_conversations(input_file)
    if not conversations:
        print("❌ No conversations loaded")
        sys.exit(1)

    analyzer = ConversationAnalyzer(conversations)
    stats = analyzer.compute_global_stats()

    exporter = ConversationExporter(conversations, stats)

    if format_type == "json":
        filepath = exporter.export_json(output)
    elif format_type == "jsonl":
        filepath = exporter.export_jsonl(output)
    elif format_type == "markdown":
        if args.split:
            files = exporter.export_markdown(output, single_file=False)
            print(f"💾 Exported {len(files)} files to: {output}")
            return
        else:
            filepath = exporter.export_markdown(output, single_file=True)
            filepath = filepath[0] if isinstance(filepath, list) else filepath
    elif format_type == "html":
        filepath = exporter.export_html(output)
    elif format_type == "pdf":
        filepath = exporter.export_pdf(output)
    else:
        print(f"❌ Unknown format: {format_type}")
        sys.exit(1)

    print(f"✅ Exported to: {filepath}")


def cmd_knowledge(args):
    """Extract knowledge from conversations."""
    input_file = args.input
    output = args.output

    print("🧠 Extracting knowledge...")
    conversations = _load_conversations(input_file)
    if not conversations:
        print("❌ No conversations loaded")
        sys.exit(1)

    extractor = KnowledgeExtractor()
    all_snippets = []
    all_todos = []
    all_decisions = []
    all_commands = []
    all_errors = []

    for conv in conversations:
        knowledge = extractor.extract(conv)
        all_snippets.extend(knowledge.code_snippets)
        all_todos.extend(knowledge.todos)
        all_decisions.extend(knowledge.decisions)
        all_commands.extend(knowledge.commands)
        all_errors.extend(knowledge.errors)

    print(f"✅ Knowledge extraction complete")
    print(f"  💻 Code Snippets: {len(all_snippets)}")
    print(f"  ✅ TODOs: {len(all_todos)}")
    print(f"  🎯 Decisions: {len(all_decisions)}")
    print(f"  ⌨️  Commands: {len(all_commands)}")
    print(f"  ⚠️  Errors: {len(all_errors)}")
    print()

    # Show top commands
    if all_commands:
        print("⌨️  TOP COMMANDS:")
        from collections import Counter
        for cmd, count in Counter(all_commands).most_common(10):
            print(f"  ({count}x) {cmd}")
        print()

    if output:
        data = {
            "code_snippets": all_snippets,
            "todos": all_todos,
            "decisions": all_decisions,
            "commands": all_commands,
            "errors": all_errors,
        }
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 Knowledge base saved to: {output}")


def cmd_list(args):
    """List available extractors."""
    print("📡 Available extractors:")
    print()
    for name in list_extractors():
        extractor = get_extractor(name)
        print(f"  • {extractor.display_name} ({name})")
        print(f"    Default path: {extractor.default_path}")
        print()


def cmd_web(args):
    """Start the web UI dashboard."""
    from chatharvest.webui import start_webui
    input_file = args.input
    port = args.port
    host = args.host

    conversations = _load_conversations(input_file) if input_file else []
    print(f"🌐 Starting ChatHarvest Web UI at http://{host}:{port}")
    print(f"   Loaded {len(conversations)} conversations")
    start_webui(conversations, host=host, port=port)


def _load_conversations(filepath: str) -> List[Conversation]:
    """Load conversations from a JSON or JSONL file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return []

    conversations = []
    try:
        if filepath.endswith(".jsonl"):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        conv = _dict_to_conversation(data)
                        if conv:
                            conversations.append(conv)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    conv = _dict_to_conversation(item)
                    if conv:
                        conversations.append(conv)
            elif isinstance(data, dict) and "conversations" in data:
                for item in data["conversations"]:
                    conv = _dict_to_conversation(item)
                    if conv:
                        conversations.append(conv)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error loading file: {e}")

    return conversations


def _dict_to_conversation(data: dict) -> Optional[Conversation]:
    """Convert a dict to a Conversation object."""
    try:
        from chatharvest.models import Message, CodeSnippet
        messages = []
        for msg_data in data.get("messages", []):
            snippets = []
            for s in msg_data.get("code_snippets", []):
                snippets.append(CodeSnippet(
                    language=s.get("language", "text"),
                    code=s.get("code", ""),
                    filename=s.get("filename"),
                ))
            messages.append(Message(
                role=msg_data.get("role", "user"),
                content=msg_data.get("content", ""),
                timestamp=msg_data.get("timestamp"),
                model=msg_data.get("model"),
                tokens_input=msg_data.get("tokens_input"),
                tokens_output=msg_data.get("tokens_output"),
                code_snippets=snippets,
                metadata=msg_data.get("metadata", {}),
            ))

        conv = Conversation(
            id=data.get("id", ""),
            source=data.get("source", "unknown"),
            title=data.get("title", "Untitled"),
            messages=messages,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            model=data.get("model"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
        if data.get("stats"):
            from chatharvest.models import ConversationStats
            s = data["stats"]
            conv.stats = ConversationStats(
                message_count=s.get("message_count", 0),
                user_messages=s.get("user_messages", 0),
                assistant_messages=s.get("assistant_messages", 0),
                total_tokens=s.get("total_tokens", 0),
                total_chars=s.get("total_chars", 0),
                code_snippet_count=s.get("code_snippet_count", 0),
                languages_used=s.get("languages_used", []),
                duration_seconds=s.get("duration_seconds"),
                estimated_cost_usd=s.get("estimated_cost_usd"),
            )
        return conv
    except Exception as e:
        print(f"⚠️  Skipping invalid conversation: {e}")
        return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chatharvest",
        description="🌾 ChatHarvest - AI Coding Conversation Harvest & Intelligence Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  chatharvest extract claude-code -o conversations.json
  chatharvest extract cursor --path ~/.cursor -o cursor_chats.json
  chatharvest analyze -i conversations.json -o report.json
  chatharvest search -i conversations.json "docker compose"
  chatharvest export -i conversations.json -o archive.html --format html
  chatharvest knowledge -i conversations.json -o knowledge.json
  chatharvest web -i conversations.json --port 8080
  chatharvest list
        """,
    )
    parser.add_argument("--version", action="version", version=f"ChatHarvest {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract conversations from a source")
    extract_parser.add_argument("source", help=f"Source type: {', '.join(list_extractors())}")
    extract_parser.add_argument("--path", "-p", help="Path to data (uses default if not specified)")
    extract_parser.add_argument("--output", "-o", help="Output file path")
    extract_parser.add_argument("--format", "-f", choices=["json", "jsonl", "markdown", "html", "pdf"],
                                default="json", help="Output format (default: json)")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze conversations")
    analyze_parser.add_argument("--input", "-i", required=True, help="Input JSON/JSONL file")
    analyze_parser.add_argument("--output", "-o", help="Output analysis report")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search conversations")
    search_parser.add_argument("--input", "-i", required=True, help="Input JSON/JSONL file")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-n", type=int, default=20, help="Max results (default: 20)")
    search_parser.add_argument("--source", "-s", help="Filter by source")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export conversations")
    export_parser.add_argument("--input", "-i", required=True, help="Input JSON/JSONL file")
    export_parser.add_argument("--output", "-o", required=True, help="Output file/directory path")
    export_parser.add_argument("--format", "-f", choices=["json", "jsonl", "markdown", "html", "pdf"],
                                default="markdown", help="Output format (default: markdown)")
    export_parser.add_argument("--split", action="store_true", help="Split markdown into separate files")

    # Knowledge command
    knowledge_parser = subparsers.add_parser("knowledge", help="Extract knowledge from conversations")
    knowledge_parser.add_argument("--input", "-i", required=True, help="Input JSON/JSONL file")
    knowledge_parser.add_argument("--output", "-o", help="Output knowledge base JSON")

    # Web command
    web_parser = subparsers.add_parser("web", help="Start web UI dashboard")
    web_parser.add_argument("--input", "-i", help="Input JSON/JSONL file")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    web_parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen (default: 8765)")

    # List command
    subparsers.add_parser("list", help="List available extractors")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    if args.command != "list":
        print_banner()

    commands = {
        "extract": cmd_extract,
        "analyze": cmd_analyze,
        "search": cmd_search,
        "export": cmd_export,
        "knowledge": cmd_knowledge,
        "web": cmd_web,
        "list": cmd_list,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
