from __future__ import annotations

from typing import List, Any

from pydantic import BaseModel


class RoleMessage(BaseModel):
    role: str
    content: str


class ChatHistory(BaseModel):
    message: str
    answer: str


class Message(BaseModel):
    message: str
    api_key: str
    chat_history: List[RoleMessage]


class DocMessage(BaseModel):
    message: str
    delete_index: bool
    doc_history: list[tuple[str, Any]]
    chat_history: List[RoleMessage]


class QnA(BaseModel):
    message: str
    url: str


class NewsContent(BaseModel):
    message: str
    api_key: str
