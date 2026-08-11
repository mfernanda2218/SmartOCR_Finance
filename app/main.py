from fastapi import FastAPI
from smart_ocr_finance.config.settings import settings
from smart_ocr_finance.utils.logger import log
from smart_ocr_finance.api.routes import router as api_router

def create_app() -> FastAPI:
    """
    Cria e configura a instância da aplicação FastAPI.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Sistema inteligente de extração de dados de documentos financeiros.",
    )

    # Inclusão das rotas da API
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        log.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
        log.info(f"Ambiente: {settings.ENVIRONMENT}")

    @app.get("/")
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    log.info(f"Iniciando servidor Uvicorn em {settings.API_HOST}:{settings.API_PORT}...")
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
