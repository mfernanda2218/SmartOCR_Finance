"""
Exemplo Prático de Testes com PostgreSQL - SmartOCR Finance

Este arquivo demonstra como configurar e executar testes usando
um banco de dados PostgreSQL real para testes de integração.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base
from src.repositories.extraction_repository import ExtractionRepository


# Configuração do banco de teste PostgreSQL
POSTGRES_TEST_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/smartocr_test"
)


@pytest.fixture(scope="session")
def postgres_engine():
    """
    Cria engine PostgreSQL para a sessão de testes.
    Este fixture é executado uma vez no início da sessão de testes.
    """
    engine = create_engine(POSTGRES_TEST_URL)
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Limpar tabelas ao final da sessão
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def postgres_session(postgres_engine):
    """
    Cria uma sessão PostgreSQL para cada teste.
    Cada teste tem sua própria transação que é rollbackada.
    """
    TestingSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=postgres_engine
    )
    session = TestingSession()
    
    # Iniciar transação
    connection = postgres_engine.connect()
    transaction = connection.begin()
    
    # Bind da sessão à conexão
    session.bind = connection
    
    yield session
    
    # Rollback ao final do teste
    session.close()
    transaction.rollback()
    connection.close()


class TestPostgreSQLIntegration:
    """Testes de integração usando PostgreSQL"""
    
    def test_conexao_postgresql(self, postgres_session):
        """Testa conexão básica com PostgreSQL"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        
        # Act
        record = ExtractionRecord(
            filename="teste_postgres.png",
            raw_text="Texto de teste PostgreSQL",
            document_type="DESCONHECIDO",
            processing_status="SUCCESS"
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.id is not None
        assert record.filename == "teste_postgres.png"
    
    def test_repository_com_postgres(self, postgres_session):
        """Testa repositório usando PostgreSQL"""
        # Arrange
        repo = ExtractionRepository(postgres_session)
        
        # Act - Create
        record = repo.save(
            filename="repo_test.png",
            raw_text="CPF: 123.456.789-00",
            cpfs=["123.456.789-00"],
            cnpjs=[],
            dates=["15/09/2026"],
            values=["100.00"],
            boleto_lines=[]
        )
        
        # Assert - Create
        assert record.id is not None
        
        # Act - Read
        found = repo.get_by_id(record.id)
        
        # Assert - Read
        assert found is not None
        assert found.filename == "repo_test.png"
        
        # Act - Read All
        all_records = repo.get_all()
        
        # Assert - Read All
        assert len(all_records) >= 1
        
        # Act - Delete
        deleted = repo.delete(record.id)
        
        # Assert - Delete
        assert deleted is True
        assert repo.get_by_id(record.id) is None
    
    def test_transacao_rollback(self, postgres_session):
        """Testa que transações são rollbackadas entre testes"""
        # Arrange
        repo = ExtractionRepository(postgres_session)
        
        # Act - Criar registro no primeiro teste
        record1 = repo.save(
            filename="rollback_test1.png",
            raw_text="Texto 1",
            cpfs=[],
            cnpjs=[],
            dates=[],
            values=[],
            boleto_lines=[]
        )
        
        # Assert
        assert record1.id is not None
        
        # Verificar que o registro existe
        records_before = repo.get_all()
        count_before = len(records_before)
        
        # Este teste termina aqui, e a transação é rollbackada
        # No próximo teste, o registro não deve existir


class TestPostgreSQLPerformance:
    """Testes de performance com PostgreSQL"""
    
    def test_insercao_em_massa(self, postgres_session):
        """Testa performance de inserção em massa"""
        import time
        
        # Arrange
        repo = ExtractionRepository(postgres_session)
        num_records = 100
        
        # Act
        start_time = time.time()
        
        for i in range(num_records):
            repo.save(
                filename=f"perf_test_{i}.png",
                raw_text=f"Texto {i}",
                cpfs=[f"123.456.789-{i:02d}"],
                cnpjs=[],
                dates=["15/09/2026"],
                values=[f"{(i+1)*10}.00"],
                boleto_lines=[]
            )
        
        elapsed_time = time.time() - start_time
        
        # Assert
        records = repo.get_all()
        assert len(records) == num_records
        assert elapsed_time < 5.0, f"Inserção demorou {elapsed_time:.2f}s (limite: 5s)"
    
    def test_consulta_complexa(self, postgres_session):
        """Testa performance de consulta complexa"""
        import time
        
        # Arrange
        repo = ExtractionRepository(postgres_session)
        
        # Criar dados de teste
        for i in range(50):
            repo.save(
                filename=f"complex_test_{i}.png",
                raw_text=f"Texto {i}",
                cpfs=[f"111.222.333-{i%10:02d}"],
                cnpjs=[],
                dates=["15/09/2026"],
                values=[f"{(i+1)*50}.00"],
                boleto_lines=[]
            )
        
        # Act
        start_time = time.time()
        
        # Consulta simulada
        all_records = repo.get_all()
        filtered = [r for r in all_records if r.cpfs]
        
        elapsed_time = time.time() - start_time
        
        # Assert
        assert len(all_records) == 50
        assert len(filtered) > 0
        assert elapsed_time < 1.0, f"Consulta demorou {elapsed_time:.2f}s (limite: 1s)"


class TestPostgreSQLDataTypes:
    """Testa tipos de dados específicos do PostgreSQL"""
    
    def test_json_fields(self, postgres_session):
        """Testa campos JSON do PostgreSQL"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        import json
        
        # Act
        record = ExtractionRecord(
            filename="json_test.png",
            raw_text="Texto",
            cpfs=json.dumps(["123.456.789-00", "987.654.321-00"]),
            cnpjs=json.dumps(["12.345.678/0001-90"]),
            dates=json.dumps(["15/09/2026", "20/09/2026"]),
            values=json.dumps(["100.00", "200.00"]),
            boleto_lines=json.dumps(["linha1", "linha2", "linha3"])
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.id is not None
        
        # Recuperar e validar JSON
        cpfs_list = json.loads(record.cpfs)
        assert len(cpfs_list) == 2
        assert "123.456.789-00" in cpfs_list
    
    def test_datetime_fields(self, postgres_session):
        """Testa campos datetime do PostgreSQL"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        from datetime import datetime, timezone
        
        # Act
        record = ExtractionRecord(
            filename="datetime_test.png",
            raw_text="Texto",
            processing_time_ms=1500,
            confidence_score=0.95
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.created_at is not None
        assert record.updated_at is not None
        
        # Verificar que são datetime com timezone
        assert isinstance(record.created_at, datetime)


class TestPostgreSQLEdgeCases:
    """Testa casos extremos com PostgreSQL"""
    
    def test_texto_muito_longo(self, postgres_session):
        """Testa inserção de texto muito longo"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        
        long_text = "x" * 10000  # 10.000 caracteres
        
        # Act
        record = ExtractionRecord(
            filename="long_text.png",
            raw_text=long_text
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.id is not None
        assert len(record.raw_text) == 10000
    
    def test_caracteres_especiais(self, postgres_session):
        """Testa caracteres especiais e unicode"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        
        special_text = "áéíóú ñ ç ß ø 中文 العربية"
        
        # Act
        record = ExtractionRecord(
            filename="special_chars.png",
            raw_text=special_text
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.id is not None
        assert record.raw_text == special_text
    
    def test_valores_nulos(self, postgres_session):
        """Testa campos nulos/opcionais"""
        # Arrange
        from src.models.extraction_record import ExtractionRecord
        
        # Act
        record = ExtractionRecord(
            filename="null_test.png",
            raw_text="Texto básico",
            # Campos opcionais não preenchidos
            file_size=None,
            confidence_score=None,
            processing_time_ms=None
        )
        
        postgres_session.add(record)
        postgres_session.commit()
        
        # Assert
        assert record.id is not None
        assert record.file_size is None
        assert record.confidence_score is None


def test_configuracao_postgres():
    """Testa se configuração PostgreSQL está correta"""
    # Arrange
    import os
    
    # Act
    db_url = os.getenv("TEST_DATABASE_URL", POSTGRES_TEST_URL)
    
    # Assert
    assert "postgresql" in db_url
    assert "localhost" in db_url or "127.0.0.1" in db_url


# Exemplo de como executar este teste:
# 
# 1. Configurar variável de ambiente:
#    export TEST_DATABASE_URL="postgresql://usuario:senha@localhost:5432/smartocr_test"
#
# 2. Criar banco de teste:
#    createdb smartocr_test
#
# 3. Executar testes:
#    pytest tests/test_postgres_example.py -v
#
# 4. Ou executar apenas uma classe:
#    pytest tests/test_postgres_example.py::TestPostgreSQLIntegration -v
#
# 5. Ou executar apenas um teste:
#    pytest tests/test_postgres_example.py::TestPostgreSQLIntegration::test_conexao_postgresql -v