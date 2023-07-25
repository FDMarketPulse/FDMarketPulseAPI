from typing import List

from fastapi import APIRouter, Depends

from application.services import TdViewNews
from .schema import NewsInfo

router = APIRouter()


@router.get("/news-info",
            response_model=List[NewsInfo],
            response_description="get news list")
async def get_news_list(service: TdViewNews = Depends()):
    return service.get_overall_news()


@router.get("/details-news-via-id/{item_id}",
            # response_model=SingleNewsContent,
            response_description="get news details via news id")
async def get_news_detail(item_id: str, service: TdViewNews = Depends()):
    return service.get_single_news(item_id)

