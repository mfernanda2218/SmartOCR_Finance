from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.config import settings
from src.utils.logger import log
from src.api.routes import router as api_router
from src.models.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    log.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    log.info(f"Ambiente: {settings.ENVIRONMENT}")
    create_tables()
    yield
    # Shutdown
    log.info("Desligando aplicação...")


def create_app() -> FastAPI:
    """Cria e configura a instância da aplicação FastAPI."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Sistema inteligente de extração de dados de documentos financeiros.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar origens permitidas
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/")
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/health")
    async def health_check():
        """Health check detalhado"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # Exception handler global
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.exception(f"Erro não tratado: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Erro interno do servidor", "error": str(exc)},
        )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=(settings.ENVIRONMENT == "development"),
    )
