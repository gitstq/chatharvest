"""
Windsurf extractor - extracts conversations from Windsurf IDE.
Similar storage format to Cursor (Codeium based).
"""

import os
import uuid
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class WindsurfExtractor(BaseExtractor):
    name = "windsurf"
    display_name = "Windsurf"
    default_path = "~/.windsurf"
    file_patterns = [".json", ".jsonl"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        if not os.path.isdir(data_path):
            return conversations

        candidate_dirs = [
            os.path.join(data_path, "User", "globalStorage"),
            os.path.join(data_path, "user", "globalStorage"),
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
                if ("chat" in f.lower() or "cascade" in f.lower()) and (f.endswith(".json") or f.endswith(".jsonl")):
                    filepath = os.path.join(root, f)
                    if f.endswith(".jsonl"):
                        records = self._read_jsonl(filepath)
                        for record in records:
                            conv = self._parse_record(record, filepath)
                            if conv:
                                conversations.append(conv)
                    else:
                        data = self._read_json(filepath)
                        if data:
                            if isinstance(data, list):
                                for record in data:
                                    conv = self._parse_record(record, filepath)
                                    if conv:
                                        conversations.append(conv)
                            else:
                                conv = self._parse_record(data, filepath)
                                if conv:
                                    conversations.append(conv)
        return conversations

    def _parse_record(self, data: dict, filepath: str) -> Optional[Conversation]:
        messages_data = data.get("messages") or data.get("chatMessages") or []
        if not messages_data and "conversation" in data:
            messages_data = data["conversation"].get("messages", [])

        if not messages_data:
            return None

        messages = []
        for msg_data in messages_data:
            if isinstance(msg_data, str):
                messages.append(Message(role="user", content=msg_data))
                continue

            role = msg_data.get("role", msg_data.get("author", "user"))
            content = msg_data.get("content", msg_data.get("text", ""))

            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                content = "\n".join(text_parts)

            msg = Message(
                role=role,
                content=content or "",
                model=msg_data.get("model"),
                tokens_input=msg_data.get("inputTokens") or msg_data.get("prompt_tokens"),
                tokens_output=msg_data.get("outputTokens") or msg_data.get("completion_tokens"),
            )
            messages.append(msg)

        if not messages:
            return None

        title = data.get("title") or data.get("name") or f"Windsurf Cascade - {os.path.basename(filepath)}"

        conv = Conversation(
            id=str(uuid.uuid4()),
            source=self.name,
            title=title,
            messages=messages,
            created_at=data.get("createdAt") or data.get("timestamp"),
            updated_at=data.get("updatedAt"),
            model=data.get("model"),
            metadata={"source_file": filepath}
        )
        conv.compute_stats()
        return conv
