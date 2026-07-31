from fastapi import FastAPI
from src.config import settings
from src.utils import log

def create_app() -> FastAPI:
    """
    Cria e configura a instância da aplicação FastAPI.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Sistema inteligente de extração de dados de documentos financeiros.",
    )

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
