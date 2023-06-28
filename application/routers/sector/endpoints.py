from typing import List

from fastapi import APIRouter, Depends

from application.services import TdViewAnalysis
from .schema import SectorInfo

router = APIRouter()


@router.get("/sector-overview",
            response_model=List[SectorInfo],
            response_description="get us market sector overview")
async def get_market_cap_sentiments(service: TdViewAnalysis = Depends()):
    return service.get_sector_data()
