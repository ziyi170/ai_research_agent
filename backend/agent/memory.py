"""
Conversation Memory - stores multi-turn dialogue history per session.

In production this would be backed by Redis or a database.
Here we use an in-memory dict for simplicity and portability.
"""

from collections import defaultdict
from typing import Optional


class ConversationMemory:
    """
    Manages per-session conversation history.
    
    Each session stores a list of {role, content} dicts
    compatible with the OpenAI messages format.
    """

    def __init__(self, max_turns: int = 3):
        self._store: dict[str, list[dict]] = defaultdict(list)
        self.max_turns = max_turns  # sliding window to stay within context limit

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str):
        """Append a user/assistant exchange to the session history."""
        history = self._store[session_id]
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": assistant_msg})

        # Keep only the last N turns to avoid exceeding context window
        if len(history) > self.max_turns * 2:
            self._store[session_id] = history[-(self.max_turns * 2):]

    def get_history(self, session_id: str) -> list[dict]:
        """Returns the full history for a session."""
        return self._store.get(session_id, [])

    def clear(self, session_id: str):
        """Removes all history for a session."""
        if session_id in self._store:
            del self._store[session_id]

    def session_count(self) -> int:
        return len(self._store)
