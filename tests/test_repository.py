import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.models.extraction_record import ExtractionRecord
from src.repositories.extraction_repository import ExtractionRepository

# Banco em memória para testes (sem tocar no SQLite de desenvolvimento)
TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="function")
def db_session():
    """Cria um banco de dados em memória isolado para cada teste."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def repo(db_session):
    return ExtractionRepository(db_session)


# ---------------------------------------------------------------------------
# Testes de CRUD do Repository
# ---------------------------------------------------------------------------

def test_save_record(repo):
    record = repo.save(
        filename="boleto.png",
        raw_text="Vencimento 10/10/2023 Valor R$ 250,00",
        cpfs=["111.222.333-44"],
        cnpjs=[],
        dates=["10/10/2023"],
        values=["250,00"],
        boleto_lines=[],
    )
    assert record.id is not None
    assert record.filename == "boleto.png"
    assert json.loads(record.dates) == ["10/10/2023"]
    assert json.loads(record.values) == ["250,00"]

def test_get_by_id(repo):
    record = repo.save(
        filename="nota.jpg", raw_text="Texto", cpfs=[], cnpjs=[],
        dates=[], values=["100,00"], boleto_lines=[]
    )
    found = repo.get_by_id(record.id)
    assert found is not None
    assert found.id == record.id

def test_get_by_id_not_found(repo):
    found = repo.get_by_id(9999)
    assert found is None

def test_get_all(repo):
    repo.save("a.png", "txt", [], [], [], ["10,00"], [])
    repo.save("b.png", "txt", [], [], [], ["20,00"], [])
    records = repo.get_all()
    assert len(records) == 2

def test_get_all_pagination(repo):
    for i in range(5):
        repo.save(f"file{i}.png", "txt", [], [], [], [], [])
    records = repo.get_all(skip=2, limit=2)
    assert len(records) == 2

def test_delete_record(repo):
    record = repo.save("deletar.png", "txt", [], [], [], [], [])
    deleted = repo.delete(record.id)
    assert deleted is True
    assert repo.get_by_id(record.id) is None

def test_delete_not_found(repo):
    deleted = repo.delete(9999)
    assert deleted is False
