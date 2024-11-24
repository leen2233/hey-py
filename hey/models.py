from dataclasses import dataclass
from typing import List


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatPayload:
    model: str
    messages: List[ChatMessage]
