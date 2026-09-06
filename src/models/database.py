from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from src.config import settings
from src.utils.logger import log
import sqlite3


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM do SQLAlchemy."""
    pass


# Configuração específica para SQLite (habilitar foreign keys)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.ENVIRONMENT == "development"  # Log SQL queries em desenvolvimento
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependência FastAPI que provê e fecha automaticamente uma sessão de banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Cria todas as tabelas definidas nos modelos ORM."""
    log.info("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    log.info("Tabelas criadas com sucesso.")


def drop_tables():
    """Remove todas as tabelas (CUIDADO: uso apenas em desenvolvimento/testes)"""
    log.warning("Removendo todas as tabelas do banco de dados...")
    Base.metadata.drop_all(bind=engine)
    log.info("Tabelas removidas.")


def reset_database():
    """Recria o banco de dados do zero (CUIDADO: dados serão perdidos)"""
    log.warning("Resetando banco de dados...")
    drop_tables()
    create_tables()
    log.info("Banco de dados resetado com sucesso.")
