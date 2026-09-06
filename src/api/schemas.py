import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.extraction_record import DocumentType, ProcessingStatus


class OCRExtractionResponse(BaseModel):
    """Schema de resposta padrão para extração OCR."""
    cpfs: List[str] = Field(description="Lista de CPFs encontrados")
    cnpjs: List[str] = Field(description="Lista de CNPJs encontrados")
    dates: List[str] = Field(description="Datas encontradas")
    values: List[str] = Field(description="Valores monetários encontrados")
    boleto_lines: List[str] = Field(description="Linhas digitáveis de boleto encontradas")
    raw_text: Optional[str] = Field(default=None, description="Texto bruto extraído pelo OCR")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados do processamento")


class ErrorResponse(BaseModel):
    """Schema para mensagens de erro."""
    detail: str


class ExtractionRecordResponse(BaseModel):
    """Schema de resposta para um registro de histórico no banco de dados."""
    id: int
    filename: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    document_type: Optional[DocumentType]
    processing_status: Optional[ProcessingStatus]
    processing_time_ms: Optional[int]
    confidence_score: Optional[float]
    raw_text: Optional[str]
    cpfs: List[str]
    cnpjs: List[str]
    dates: List[str]
    values: List[str]
    boleto_lines: List[str]
    additional_data: Optional[str]
    error_message: Optional[str]
    warnings: Optional[List[str]]
    is_validated: bool
    is_archived: bool

    @field_validator("cpfs", "cnpjs", "dates", "values", "boleto_lines", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        """Converte strings JSON armazenadas no DB para listas Python."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []

    @field_validator("warnings", mode="before")
    @classmethod
    def parse_warnings(cls, v):
        """Converte warnings JSON para lista."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []

    model_config = {"from_attributes": True}


class ExtractionRecordListResponse(BaseModel):
    """Schema de resposta para listagem paginada do histórico."""
    total: int
    records: List[ExtractionRecordResponse]


class HealthCheckResponse(BaseModel):
    """Schema de resposta para health check."""
    status: str
    service: str
    version: str
    timestamp: str
    components: dict


class StatsResponse(BaseModel):
    """Schema de resposta para estatísticas."""
    total_extractions: int
    successful_extractions: int
    documents_with_cpf: int
    documents_with_cnpj: int
    documents_with_values: int
    average_fields_per_document: float
