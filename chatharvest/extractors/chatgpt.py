"""
ChatGPT extractor - extracts conversations from exported ChatGPT data.
ChatGPT exports conversations as a single conversations.json file or JSONL.
"""

import os
import uuid
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class ChatGPTExtractor(BaseExtractor):
    name = "chatgpt"
    display_name = "ChatGPT"
    default_path = "."
    file_patterns = ["conversations.json", ".jsonl"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        if os.path.isfile(data_path):
            # Single file
            if data_path.endswith(".jsonl"):
                records = self._read_jsonl(data_path)
                for record in records:
                    conv = self._parse_conversation(record)
                    if conv:
                        conversations.append(conv)
            else:
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
            # Look for conversations.json in directory
            for root, dirs, files in os.walk(data_path):
                for f in files:
                    if f in ("conversations.json", "chatgpt_conversations.json") or (f.endswith(".json") and "conversation" in f.lower()):
                        filepath = os.path.join(root, f)
                        data = self._read_json(filepath)
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
                    elif f.endswith(".jsonl") and "chat" in f.lower():
                        records = self._read_jsonl(os.path.join(root, f))
                        for record in records:
                            conv = self._parse_conversation(record)
                            if conv:
                                conversations.append(conv)

        return self._deduplicate(conversations)

    def _parse_conversation(self, data: dict) -> Optional[Conversation]:
        # ChatGPT export format
        title = data.get("title", "Untitled Chat")
        conversation_id = data.get("conversation_id") or data.get("id") or str(uuid.uuid4())
        create_time = data.get("create_time")
        update_time = data.get("update_time")

        # ChatGPT stores messages in a mapping dict
        mapping = data.get("mapping", {})
        messages_data = []

        if mapping:
            # Walk the message tree
            current = data.get("current_node")
            visited = set()
            while current and current in mapping and current not in visited:
                visited.add(current)
                node = mapping[current]
                msg = node.get("message")
                if msg:
                    messages_data.append(msg)
                current = node.get("parent")
            messages_data.reverse()
        else:
            messages_data = data.get("messages", [])

        if not messages_data:
            return None

        messages = []
        for msg_data in messages_data:
            if not isinstance(msg_data, dict):
                continue

            role = msg_data.get("role", "user")
            content = msg_data.get("content", "")

            # ChatGPT content can be dict with parts
            if isinstance(content, dict):
                parts = content.get("parts", [])
                text_parts = []
                for part in parts:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict):
                        if part.get("content_type") == "text":
                            text_parts.append("".join(part.get("parts", [])))
                content = "\n".join(text_parts)
            elif isinstance(content, list):
                content = "\n".join(str(p) for p in content if isinstance(p, str))

            # Skip empty messages
            if not content or not str(content).strip():
                continue

            msg = Message(
                role=role,
                content=str(content),
                model=msg_data.get("model"),
                timestamp=str(msg_data.get("create_time", "")) if msg_data.get("create_time") else None,
                tokens_input=msg_data.get("metadata", {}).get("token_details", {}).get("prompt_tokens") if isinstance(msg_data.get("metadata"), dict) else None,
                tokens_output=msg_data.get("metadata", {}).get("token_details", {}).get("completion_tokens") if isinstance(msg_data.get("metadata"), dict) else None,
            )
            messages.append(msg)

        if not messages:
            return None

        conv = Conversation(
            id=conversation_id,
            source=self.name,
            title=title,
            messages=messages,
            created_at=str(create_time) if create_time else None,
            updated_at=str(update_time) if update_time else None,
            model=data.get("default_model_slug"),
            metadata={
                "conversation_id": conversation_id,
                "plugin_ids": data.get("plugin_ids"),
                "conversation_template_id": data.get("conversation_template_id"),
            }
        )
        conv.compute_stats()
        return conv
