from __future__ import annotations

from typing import List

from pydantic import BaseModel


class RoleMessage(BaseModel):
    role: str
    content: str


class Message(BaseModel):
    message: str
    api_key: str
    chat_history: List[RoleMessage]


class NewsContent(BaseModel):
    message: str
    api_key: str
