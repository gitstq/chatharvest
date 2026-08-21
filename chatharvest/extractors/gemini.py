"""
Gemini extractor - extracts conversations from exported Google Gemini data.
Gemini exports conversations as JSON files in Takeout.
"""

import os
import uuid
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class GeminiExtractor(BaseExtractor):
    name = "gemini"
    display_name = "Google Gemini"
    default_path = "."
    file_patterns = [".json"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        if os.path.isfile(data_path):
            data = self._read_json(data_path)
            if data:
                if isinstance(data, list):
                    for record in data:
                        conv = self._parse_conversation(record)
                        if conv:
                            conversations.append(conv)
                else:
                    conv = self._parse_conversation(data)
                    if conv:
                        conversations.append(conv)
        elif os.path.isdir(data_path):
            # Look in Takeout/Gemini/Chats/
            gemini_dirs = [
                os.path.join(data_path, "Takeout", "Gemini", "Chats"),
                os.path.join(data_path, "Gemini", "Chats"),
                os.path.join(data_path, "Chats"),
                data_path,
            ]
            for gemini_dir in gemini_dirs:
                if os.path.isdir(gemini_dir):
                    for f in os.listdir(gemini_dir):
                        if f.endswith(".json"):
                            filepath = os.path.join(gemini_dir, f)
                            data = self._read_json(filepath)
                            if data:
                                conv = self._parse_conversation(data)
                                if conv:
                                    conversations.append(conv)

        return self._deduplicate(conversations)

    def _parse_conversation(self, data: dict) -> Optional[Conversation]:
        # Gemini export format
        title = data.get("title", "Untitled Gemini Chat")
        conv_id = data.get("conversation_id") or data.get("id") or str(uuid.uuid4())
        create_time = data.get("create_time") or data.get("createdAt")

        messages_data = data.get("messages") or data.get("conversation") or []
        if not messages_data:
            return None

        messages = []
        for msg_data in messages_data:
            if not isinstance(msg_data, dict):
                continue

            role = msg_data.get("role", msg_data.get("author", "user"))
            # Normalize role
            if role in ("0", "user"):
                role = "user"
            elif role in ("1", "assistant", "model"):
                role = "assistant"

            content = msg_data.get("content", "")
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        if "text" in part:
                            text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                content = "\n".join(text_parts)

            if not content or not str(content).strip():
                continue

            msg = Message(
                role=role,
                content=str(content),
                model=msg_data.get("model"),
                timestamp=msg_data.get("create_time") or msg_data.get("timestamp"),
            )
            messages.append(msg)

        if not messages:
            return None

        conv = Conversation(
            id=conv_id,
            source=self.name,
            title=title,
            messages=messages,
            created_at=create_time,
            updated_at=data.get("update_time") or data.get("updatedAt"),
            model=data.get("model"),
            metadata={
                "conversation_id": conv_id,
                "drafts": data.get("drafts"),
            }
        )
        conv.compute_stats()
        return conv
