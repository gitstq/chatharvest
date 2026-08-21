"""
Cline/Roo Code extractor - extracts conversations from Cline VS Code extension.
Cline stores conversations as JSON files in the extension's globalStorage.
"""

import os
import uuid
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class ClineExtractor(BaseExtractor):
    name = "cline"
    display_name = "Cline / Roo Code"
    default_path = "~/.vscode"
    file_patterns = [".json"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        if not os.path.isdir(data_path):
            return conversations

        # Cline stores in globalStorage with extension ID
        candidate_dirs = [
            os.path.join(data_path, "User", "globalStorage", "saoudrizwan.claude-dev"),
            os.path.join(data_path, "User", "globalStorage", "rooveterinaryinc.roo-cline"),
            os.path.join(data_path, "user", "globalStorage", "saoudrizwan.claude-dev"),
            os.path.join(data_path, "user", "globalStorage", "rooveterinaryinc.roo-cline"),
            data_path,
        ]

        for candidate in candidate_dirs:
            if os.path.isdir(candidate):
                conversations.extend(self._scan_directory(candidate))

        return self._deduplicate(conversations)

    def _scan_directory(self, directory: str) -> List[Conversation]:
        conversations = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".json") and ("task" in f.lower() or "conversation" in f.lower() or "cline" in f.lower()):
                    filepath = os.path.join(root, f)
                    conv = self._parse_conversation(filepath)
                    if conv:
                        conversations.append(conv)
                # Also check tasks subdirectory
                if "tasks" in root.lower() and f.endswith(".json"):
                    filepath = os.path.join(root, f)
                    conv = self._parse_conversation(filepath)
                    if conv:
                        conversations.append(conv)
        return conversations

    def _parse_conversation(self, filepath: str) -> Optional[Conversation]:
        data = self._read_json(filepath)
        if not data:
            return None

        # Cline task format
        messages_data = data.get("conversationHistory") or data.get("messages") or []
        if not messages_data:
            return None

        messages = []
        for msg_data in messages_data:
            if not isinstance(msg_data, dict):
                continue

            role = msg_data.get("role", "user")
            content = msg_data.get("content", "")

            # Handle array content
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif part.get("type") == "tool_result":
                            tc = part.get("content", "")
                            if isinstance(tc, list):
                                for t in tc:
                                    if isinstance(t, dict) and t.get("type") == "text":
                                        text_parts.append(f"[Tool: {t.get('text', '')}]")
                            else:
                                text_parts.append(f"[Tool: {tc}]")
                content = "\n".join(text_parts)

            # Skip empty system messages
            if role == "system" and not content:
                continue

            msg = Message(
                role=role,
                content=content or "",
                model=msg_data.get("model"),
                tokens_input=msg_data.get("usage", {}).get("input_tokens") if isinstance(msg_data.get("usage"), dict) else None,
                tokens_output=msg_data.get("usage", {}).get("output_tokens") if isinstance(msg_data.get("usage"), dict) else None,
            )
            messages.append(msg)

        if not messages:
            return None

        title = data.get("task") or data.get("title") or f"Cline Task - {os.path.basename(filepath)[:8]}"

        conv = Conversation(
            id=str(uuid.uuid4()),
            source=self.name,
            title=title,
            messages=messages,
            created_at=data.get("createdAt") or data.get("timestamp"),
            updated_at=data.get("updatedAt"),
            model=data.get("model"),
            metadata={
                "source_file": filepath,
                "task_id": data.get("taskId"),
                "status": data.get("status"),
            }
        )
        conv.compute_stats()
        return conv
