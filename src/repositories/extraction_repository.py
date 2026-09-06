import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from src.models.extraction_record import ExtractionRecord, DocumentType, ProcessingStatus
from src.utils.logger import log


class ExtractionRepository:
    """
    Repositório responsável pelas operações CRUD do ExtractionRecord.
    Segue o padrão Repository (separação entre lógica de negócio e acesso a dados).
    """

    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        filename: Optional[str],
        raw_text: Optional[str],
        cpfs: List[str],
        cnpjs: List[str],
        dates: List[str],
        values: List[str],
        boleto_lines: List[str],
        file_size: Optional[int] = None,
        document_type: Optional[DocumentType] = None,
        processing_status: Optional[ProcessingStatus] = None,
        processing_time_ms: Optional[int] = None,
        confidence_score: Optional[float] = None,
        warnings: Optional[List[str]] = None,
        error_message: Optional[str] = None,
    ) -> ExtractionRecord:
        """
        Persiste um novo registro de extração no banco de dados com campos avançados.
        """
        record = ExtractionRecord(
            filename=filename,
            file_size=file_size,
            raw_text=raw_text,
            document_type=document_type,
            processing_status=processing_status,
            processing_time_ms=processing_time_ms,
            confidence_score=confidence_score,
            cpfs=json.dumps(cpfs, ensure_ascii=False),
            cnpjs=json.dumps(cnpjs, ensure_ascii=False),
            dates=json.dumps(dates, ensure_ascii=False),
            values=json.dumps(values, ensure_ascii=False),
            boleto_lines=json.dumps(boleto_lines, ensure_ascii=False),
            warnings=json.dumps(warnings, ensure_ascii=False) if warnings else None,
            error_message=error_message,
            is_validated=False,
            is_archived=False,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        log.info(f"Registro de extração salvo com id={record.id}.")
        return record

    def get_by_id(self, record_id: int) -> Optional[ExtractionRecord]:
        """Busca um registro pelo ID."""
        return self.db.query(ExtractionRecord).filter(ExtractionRecord.id == record_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ExtractionRecord]:
        """Retorna todos os registros com paginação."""
        return self.db.query(ExtractionRecord).order_by(ExtractionRecord.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_filename(self, filename: str) -> List[ExtractionRecord]:
        """Busca registros por nome de arquivo."""
        return self.db.query(ExtractionRecord).filter(ExtractionRecord.filename == filename).all()

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ExtractionRecord]:
        """Busca registros em um intervalo de datas."""
        return self.db.query(ExtractionRecord).filter(
            and_(
                ExtractionRecord.created_at >= start_date,
                ExtractionRecord.created_at <= end_date
            )
        ).order_by(ExtractionRecord.created_at.desc()).all()

    def get_recent(self, days: int = 7) -> List[ExtractionRecord]:
        """Busca registros dos últimos N dias."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_by_date_range(start_date, datetime.utcnow())

    def search_by_content(self, search_term: str) -> List[ExtractionRecord]:
        """Busca registros que contenham o termo em qualquer campo textual."""
        search_pattern = f"%{search_term}%"
        return self.db.query(ExtractionRecord).filter(
            or_(
                ExtractionRecord.raw_text.ilike(search_pattern),
                ExtractionRecord.filename.ilike(search_pattern),
                ExtractionRecord.cpfs.ilike(search_pattern),
                ExtractionRecord.cnpjs.ilike(search_pattern),
            )
        ).order_by(ExtractionRecord.created_at.desc()).all()

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas agregadas dos registros."""
        total_count = self.db.query(func.count(ExtractionRecord.id)).scalar()
        
        if total_count == 0:
            return {
                "total_records": 0,
                "records_with_cpf": 0,
                "records_with_cnpj": 0,
                "records_with_values": 0,
                "records_with_boleto": 0,
            }
        
        records_with_cpf = self.db.query(func.count(ExtractionRecord.id)).filter(
            ExtractionRecord.cpfs.isnot(None),
            ExtractionRecord.cpfs != "[]"
        ).scalar()
        
        records_with_cnpj = self.db.query(func.count(ExtractionRecord.id)).filter(
            ExtractionRecord.cnpjs.isnot(None),
            ExtractionRecord.cnpjs != "[]"
        ).scalar()
        
        records_with_values = self.db.query(func.count(ExtractionRecord.id)).filter(
            ExtractionRecord.values.isnot(None),
            ExtractionRecord.values != "[]"
        ).scalar()
        
        records_with_boleto = self.db.query(func.count(ExtractionRecord.id)).filter(
            ExtractionRecord.boleto_lines.isnot(None),
            ExtractionRecord.boleto_lines != "[]"
        ).scalar()
        
        return {
            "total_records": total_count,
            "records_with_cpf": records_with_cpf,
            "records_with_cnpj": records_with_cnpj,
            "records_with_values": records_with_values,
            "records_with_boleto": records_with_boleto,
        }

    def delete(self, record_id: int) -> bool:
        """Remove um registro pelo ID. Retorna True se deletado, False se não encontrado."""
        record = self.get_by_id(record_id)
        if not record:
            log.warning(f"Tentativa de deletar registro inexistente id={record_id}.")
            return False
        self.db.delete(record)
        self.db.commit()
        log.info(f"Registro id={record_id} removido com sucesso.")
        return True

    def delete_old_records(self, days: int = 30) -> int:
        """Remove registros mais antigos que N dias. Retorna quantidade deletada."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_records = self.db.query(ExtractionRecord).filter(
            ExtractionRecord.created_at < cutoff_date
        ).all()
        
        count = len(old_records)
        for record in old_records:
            self.db.delete(record)
        
        self.db.commit()
        log.info(f"{count} registros antigos removidos (mais de {days} dias).")
        return count
