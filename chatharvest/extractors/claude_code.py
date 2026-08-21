"""
Claude Code extractor - extracts conversations from Claude Code CLI.
Claude Code stores conversations as JSON files in ~/.claude/projects/<project>/
"""

import os
import uuid
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class ClaudeCodeExtractor(BaseExtractor):
    name = "claude-code"
    display_name = "Claude Code"
    default_path = "~/.claude/projects"
    file_patterns = [".json"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        if not os.path.isdir(data_path):
            return conversations

        # Claude Code stores per-project conversation JSON files
        for root, dirs, files in os.walk(data_path):
            for f in files:
                if f.endswith(".json"):
                    filepath = os.path.join(root, f)
                    conv = self._parse_conversation(filepath, root)
                    if conv:
                        conversations.append(conv)

        return self._deduplicate(conversations)

    def _parse_conversation(self, filepath: str, project_dir: str) -> Optional[Conversation]:
        data = self._read_json(filepath)
        if not data:
            return None

        # Claude Code conversation format
        messages_data = data.get("messages", [])
        if not messages_data:
            return None

        messages = []
        for msg_data in messages_data:
            role = msg_data.get("role", "user")
            content = msg_data.get("content", "")

            # Handle content as list (multimodal)
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif part.get("type") == "tool_result":
                            tool_content = part.get("content", "")
                            if isinstance(tool_content, list):
                                for tp in tool_content:
                                    if isinstance(tp, dict) and tp.get("type") == "text":
                                        text_parts.append(f"[Tool Result] {tp.get('text', '')}")
                            else:
                                text_parts.append(f"[Tool Result] {tool_content}")
                content = "\n".join(text_parts)

            msg = Message(
                role=role,
                content=content or "",
                timestamp=msg_data.get("timestamp"),
                model=msg_data.get("model"),
                tokens_input=msg_data.get("usage", {}).get("input_tokens") if isinstance(msg_data.get("usage"), dict) else None,
                tokens_output=msg_data.get("usage", {}).get("output_tokens") if isinstance(msg_data.get("usage"), dict) else None,
            )
            messages.append(msg)

        if not messages:
            return None

        project_name = os.path.basename(project_dir)
        title = data.get("title") or f"Claude Code - {project_name} - {os.path.basename(filepath)[:8]}"

        conv = Conversation(
            id=str(uuid.uuid4()),
            source=self.name,
            title=title,
            messages=messages,
            created_at=data.get("created_at") or data.get("timestamp"),
            updated_at=data.get("updated_at"),
            model=data.get("model"),
            metadata={
                "project": project_name,
                "source_file": filepath,
                "cost": data.get("cost"),
                "token_count": data.get("token_count"),
            }
        )
        conv.compute_stats()
        return conv
