from fastapi import APIRouter

router = APIRouter()


@router.get("/test",
            name="test",
            response_description="test market pulse api")
async def test():
    return {"result": "Hi, nice to meet you!"}
