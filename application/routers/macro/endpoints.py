from fastapi import APIRouter, Depends

from application.services import YfMacroAnalysis


router = APIRouter()


@router.get("/market-macro",
            response_model=None,
            response_description="get time series market macro from yahoo finance")
async def get_all_macro_data(service: YfMacroAnalysis = Depends()):

    return service.get_all_macro_data()
