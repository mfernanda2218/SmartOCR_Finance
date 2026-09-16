import pytest
import json
from datetime import datetime, timedelta
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
    engine.dispose()

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

def test_save_record_with_advanced_fields(repo):
    """Testa salvar registro com campos avançados."""
    record = repo.save(
        filename="advanced.png",
        raw_text="Texto avançado",
        cpfs=["123.456.789-00"],
        cnpjs=["12.345.678/0001-90"],
        dates=["15/09/2026"],
        values=["1000.00"],
        boleto_lines=["34191.09008"],
        file_size=1024,
        document_type="BOLETO",
        processing_status="SUCCESS",
        processing_time_ms=1500,
        confidence_score=0.95,
        warnings=["Aviso de teste"],
        error_message=None
    )
    assert record.id is not None
    assert record.file_size == 1024
    assert record.document_type == "BOLETO"
    assert record.processing_status == "SUCCESS"
    assert record.processing_time_ms == 1500
    assert record.confidence_score == 0.95
    assert json.loads(record.warnings) == ["Aviso de teste"]

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

def test_get_all_ordering(repo):
    """Testa que get_all retorna registros ordenados por created_at descendente."""
    # Criar registros com um pequeno delay para garantir ordem diferente
    import time
    repo.save("first.png", "txt1", [], [], [], [], [])
    time.sleep(0.01)
    repo.save("second.png", "txt2", [], [], [], [], [])
    time.sleep(0.01)
    repo.save("third.png", "txt3", [], [], [], [], [])
    
    records = repo.get_all()
    assert len(records) == 3
    # O mais recente deve ser o primeiro
    assert records[0].filename == "third.png"
    assert records[1].filename == "second.png"
    assert records[2].filename == "first.png"

def test_get_by_filename(repo):
    """Testa busca por nome de arquivo."""
    repo.save("doc1.png", "texto1", [], [], [], [], [])
    repo.save("doc2.png", "texto2", [], [], [], [], [])
    repo.save("doc1.png", "texto3", [], [], [], [], [])  # Mesmo nome
    
    records = repo.get_by_filename("doc1.png")
    assert len(records) == 2
    assert all(r.filename == "doc1.png" for r in records)

def test_get_by_date_range(repo):
    """Testa busca por intervalo de datas."""
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)
    
    # Criar registros com datas específicas
    repo.save("old.png", "old", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "old.png").update(
        {"created_at": two_days_ago}
    )
    repo.db.commit()
    
    repo.save("recent.png", "recent", [], [], [], [], [])
    
    records = repo.get_by_date_range(yesterday, now)
    assert len(records) == 1
    assert records[0].filename == "recent.png"

def test_get_recent(repo):
    """Testa busca de registros recentes."""
    now = datetime.utcnow()
    five_days_ago = now - timedelta(days=5)
    
    repo.save("recent.png", "recent", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "recent.png").update(
        {"created_at": now - timedelta(hours=2)}
    )
    repo.db.commit()
    
    repo.save("old.png", "old", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "old.png").update(
        {"created_at": five_days_ago}
    )
    repo.db.commit()
    
    records = repo.get_recent(days=3)
    assert len(records) == 1
    assert records[0].filename == "recent.png"

def test_search_by_content(repo):
    """Testa busca por conteúdo textual."""
    repo.save("doc1.png", "CPF: 123.456.789-00", ["123.456.789-00"], [], [], [], [])
    repo.save("doc2.png", "CNPJ: 12.345.678/0001-90", [], ["12.345.678/0001-90"], [], [], [])
    repo.save("doc3.png", "Sem documento", [], [], [], [], [])
    
    # Buscar por CPF
    cpf_results = repo.search_by_content("123.456.789-00")
    assert len(cpf_results) == 1
    assert cpf_results[0].filename == "doc1.png"
    
    # Buscar por CNPJ
    cnpj_results = repo.search_by_content("12.345.678/0001-90")
    assert len(cnpj_results) == 1
    assert cnpj_results[0].filename == "doc2.png"
    
    # Buscar por texto geral
    text_results = repo.search_by_content("documento")
    assert len(text_results) == 1
    assert text_results[0].filename == "doc3.png"

def test_get_statistics(repo):
    """Testa obtenção de estatísticas."""
    # Criar registros com diferentes características
    repo.save("doc1.png", "txt1", ["123.456.789-00"], [], [], ["100.00"], [])
    repo.save("doc2.png", "txt2", [], ["12.345.678/0001-90"], [], ["200.00"], [])
    repo.save("doc3.png", "txt3", ["987.654.321-00"], [], [], [], [])
    repo.save("doc4.png", "txt4", [], [], [], [], ["34191.09008"])
    
    stats = repo.get_statistics()
    assert stats["total_records"] == 4
    assert stats["records_with_cpf"] == 2
    assert stats["records_with_cnpj"] == 1
    assert stats["records_with_values"] == 2
    assert stats["records_with_boleto"] == 1

def test_get_statistics_empty(repo):
    """Testa estatísticas com banco vazio."""
    stats = repo.get_statistics()
    assert stats["total_records"] == 0
    assert stats["records_with_cpf"] == 0
    assert stats["records_with_cnpj"] == 0
    assert stats["records_with_values"] == 0
    assert stats["records_with_boleto"] == 0

def test_delete_record(repo):
    record = repo.save("deletar.png", "txt", [], [], [], [], [])
    deleted = repo.delete(record.id)
    assert deleted is True
    assert repo.get_by_id(record.id) is None

def test_delete_not_found(repo):
    deleted = repo.delete(9999)
    assert deleted is False

def test_delete_old_records(repo):
    """Testa deleção de registros antigos."""
    now = datetime.utcnow()
    ten_days_ago = now - timedelta(days=10)
    forty_days_ago = now - timedelta(days=40)
    
    # Criar registros antigos e recentes
    repo.save("old1.png", "old1", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "old1.png").update(
        {"created_at": forty_days_ago}
    )
    repo.db.commit()
    
    repo.save("old2.png", "old2", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "old2.png").update(
        {"created_at": forty_days_ago}
    )
    repo.db.commit()
    
    repo.save("recent.png", "recent", [], [], [], [], [])
    repo.db.query(ExtractionRecord).filter(ExtractionRecord.filename == "recent.png").update(
        {"created_at": ten_days_ago}
    )
    repo.db.commit()
    
    # Deletar registros com mais de 30 dias
    deleted_count = repo.delete_old_records(days=30)
    assert deleted_count == 2
    
    # Verificar que apenas o recente permanece
    remaining = repo.get_all()
    assert len(remaining) == 1
    assert remaining[0].filename == "recent.png"
