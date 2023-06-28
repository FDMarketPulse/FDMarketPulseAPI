from __future__ import annotations

from typing import List

from pydantic import BaseModel


class SingleNewsInfo(BaseModel):
    id: str
    title: str
    provider: str
    published: float
    sentiment: float

class NewsInfo(BaseModel):
    type: str
    result: List[SingleNewsInfo]




