"""
Aider extractor - extracts conversations from Aider AI pair programmer.
Aider stores chat history in .aider* files and input/output logs.
"""

import os
import uuid
import re
from datetime import datetime
from typing import List, Optional

from chatharvest.extractors.base import BaseExtractor
from chatharvest.models import Conversation, Message


class AiderExtractor(BaseExtractor):
    name = "aider"
    display_name = "Aider"
    default_path = "."
    file_patterns = [".aider.chat.history.md", ".aider.input.history", ".aider.tags.cache.v3"]

    def extract(self, path: Optional[str] = None) -> List[Conversation]:
        data_path = self._resolve_path(path)
        conversations = []

        # Aider stores per-project chat history
        if os.path.isdir(data_path):
            for root, dirs, files in os.walk(data_path):
                # Skip hidden dirs except .aider
                dirs[:] = [d for d in dirs if not d.startswith(".") or d == ".aider"]
                for f in files:
                    if f == ".aider.chat.history.md":
                        filepath = os.path.join(root, f)
                        conv = self._parse_chat_history(filepath, root)
                        if conv:
                            conversations.append(conv)
        elif os.path.isfile(data_path):
            conv = self._parse_chat_history(data_path, os.path.dirname(data_path))
            if conv:
                conversations.append(conv)

        return self._deduplicate(conversations)

    def _parse_chat_history(self, filepath: str, project_dir: str) -> Optional[Conversation]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return None

        if not content.strip():
            return None

        messages = self._parse_markdown_chat(content)
        if not messages:
            return None

        project_name = os.path.basename(project_dir) or "unknown"
        mtime = os.path.getmtime(filepath)
        updated = datetime.fromtimestamp(mtime).isoformat()

        conv = Conversation(
            id=str(uuid.uuid4()),
            source=self.name,
            title=f"Aider - {project_name}",
            messages=messages,
            created_at=updated,
            updated_at=updated,
            metadata={
                "project": project_name,
                "source_file": filepath,
            }
        )
        conv.compute_stats()
        return conv

    def _parse_markdown_chat(self, content: str) -> List[Message]:
        """Parse Aider's markdown chat history format."""
        messages = []
        lines = content.split("\n")
        current_role = None
        current_content = []

        for line in lines:
            # Aider uses ## User / ## Assistant headers
            user_match = re.match(r'^#+\s*(User|user|You|🧑)\b', line)
            assistant_match = re.match(r'^#+\s*(Assistant|assistant|Aider|🤖|AI)\b', line)

            if user_match:
                if current_role and current_content:
                    messages.append(Message(role=current_role, content="\n".join(current_content).strip()))
                current_role = "user"
                current_content = []
            elif assistant_match:
                if current_role and current_content:
                    messages.append(Message(role=current_role, content="\n".join(current_content).strip()))
                current_role = "assistant"
                current_content = []
            else:
                if current_role:
                    current_content.append(line)

        if current_role and current_content:
            messages.append(Message(role=current_role, content="\n".join(current_content).strip()))

        return messages
