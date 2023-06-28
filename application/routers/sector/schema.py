from __future__ import annotations

from pydantic import BaseModel


class SectorInfo(BaseModel):
    description: str
    market: str
    change: float
    perf_w: float
    perf_1_m: float
    perf_3_m: float
    perf_6_m: float
    perf_ytd: float
    perf_y: float
    perf_5_y: float
    perf__all: float
