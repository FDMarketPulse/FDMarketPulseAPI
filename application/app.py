from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse


def create_app(version="0.0.0", debug=False):
    app = FastAPI(title="Market Pulse API",
                  description="Market Backend APIs",
                  version=version,
                  debug=debug,
                  servers=[{"url": "/api"}],
                  root_path="/",
                  default_response_class=ORJSONResponse)

    from application import routers as r
    app.include_router(r.app_router, prefix="/application", tags=["application"])
    app.include_router(r.sector_router, prefix="/sector", tags=["sector"])
    app.include_router(r.macro_router, prefix="/macro", tags=["macro"])
    app.include_router(r.news_router, prefix="/news", tags=["news"])
    app.include_router(r.chat_router, prefix="/chat", tags=["chat"])
    app.include_router(r.sector_industry_router, prefix="/sector-industry", tags=["sector-industry"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Hello from Fastapi"}

    return app
