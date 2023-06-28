from typing import List

from fastapi import APIRouter, Depends

from application.services import TdViewAnalysis
from .schema import SectorIndustryInfo

router = APIRouter()


@router.get("/industry-sector-overview",
            response_model=List[SectorIndustryInfo],
            response_description="get us market overall industry and sector data")
async def get_sector_industry_data(service: TdViewAnalysis = Depends()):
    return service.get_overall_ind_sec_data()
