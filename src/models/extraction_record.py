from datetime import datetime
from sqlalchemy import Integer, String, Float, Text, DateTime, func, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from src.models.database import Base
import enum


class DocumentType(str, enum.Enum):
    """Tipos de documentos suportados"""
    BOLETO = "boleto"
    CONTA_ENERGIA = "conta_energia"
    CONTA_AGUA = "conta_agua"
    DARF = "darf"
    OUTRO = "outro"
    DESCONHECIDO = "desconhecido"


class ProcessingStatus(str, enum.Enum):
    """Status do processamento"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


class ExtractionRecord(Base):
    """
    Modelo ORM que representa um histórico de extração OCR.
    Cada linha armazena os dados extraídos de uma imagem processada.
    """
    __tablename__ = "extraction_records"

    # Campos principais
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)  # Tamanho em bytes
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Status e metadados
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType), 
        default=DocumentType.DESCONHECIDO,
        nullable=True
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.SUCCESS,
        nullable=True
    )
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)  # Tempo de processamento em ms
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)  # Score de confiança do OCR (0-1)

    # Texto bruto extraído pelo OCR
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campos extraídos (armazenados como string JSON)
    cpfs: Mapped[str | None] = mapped_column(Text, nullable=True)
    cnpjs: Mapped[str | None] = mapped_column(Text, nullable=True)
    dates: Mapped[str | None] = mapped_column(Text, nullable=True)
    values: Mapped[str | None] = mapped_column(Text, nullable=True)
    boleto_lines: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campos adicionais para documentos específicos
    additional_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON com dados extras

    # Erros e warnings
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON com lista de warnings

    # Flags
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)  # Se foi validado manualmente
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)  # Se está arquivado

    def __repr__(self) -> str:
        return f"<ExtractionRecord id={self.id} filename={self.filename} type={self.document_type} status={self.processing_status} at={self.created_at}>"

    def to_dict(self) -> dict:
        """Converte o registro para dicionário"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "document_type": self.document_type.value if self.document_type else None,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "processing_time_ms": self.processing_time_ms,
            "confidence_score": self.confidence_score,
            "raw_text": self.raw_text,
            "cpfs": self.cpfs,
            "cnpjs": self.cnpjs,
            "dates": self.dates,
            "values": self.values,
            "boleto_lines": self.boleto_lines,
            "additional_data": self.additional_data,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "is_validated": self.is_validated,
            "is_archived": self.is_archived,
        }
