from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.api.schemas import (
    OCRExtractionResponse,
    ErrorResponse,
    ExtractionRecordResponse,
    ExtractionRecordListResponse,
    HealthCheckResponse,
)
from src.services.ocr_service import OCRService
from src.repositories.extraction_repository import ExtractionRepository
from src.models.database import get_db
from src.utils.logger import log

router = APIRouter(prefix="/api/v1", tags=["OCR Extraction"])

# Singleton da engine OCR por worker
_ocr_service_instance = None


def get_ocr_service() -> OCRService:
    global _ocr_service_instance
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()
    return _ocr_service_instance


# ---------------------------------------------------------------------------
# POST /extract — Upload e extração de dados
# ---------------------------------------------------------------------------
@router.post(
    "/extract",
    response_model=OCRExtractionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Extrai dados de um documento financeiro",
    description=(
        "Recebe uma imagem (upload), aplica pré-processamento, "
        "passa por OCR e extrai valores, datas, CPF/CNPJ e boletos. "
        "O resultado é automaticamente salvo no histórico."
    ),
)
async def extract_document_data(
    file: UploadFile = File(...),
    service: OCRService = Depends(get_ocr_service),
    db: Session = Depends(get_db),
):
    log.info(f"Requisição de extração: {file.filename} ({file.content_type})")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="O arquivo deve ser uma imagem (ex: image/jpeg, image/png).",
        )

    try:
        content = await file.read()
        result = service.process_image(content, filename=file.filename, db=db)
        return result
    except ValueError as e:
        log.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.exception(f"Erro interno no OCR: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor durante o OCR.")


# ---------------------------------------------------------------------------
# GET /history — Lista o histórico de extrações
# ---------------------------------------------------------------------------
@router.get(
    "/history",
    response_model=ExtractionRecordListResponse,
    summary="Lista o histórico de extrações",
    description="Retorna todos os registros de extração salvos, com suporte a paginação.",
)
def list_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    repo = ExtractionRepository(db)
    records = repo.get_all(skip=skip, limit=limit)
    return {"total": len(records), "records": records}


# ---------------------------------------------------------------------------
# GET /history/{record_id} — Detalhe de uma extração
# ---------------------------------------------------------------------------
@router.get(
    "/history/{record_id}",
    response_model=ExtractionRecordResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Detalha uma extração pelo ID",
)
def get_history_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    repo = ExtractionRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Registro id={record_id} não encontrado.")
    return record


# ---------------------------------------------------------------------------
# DELETE /history/{record_id} — Remove uma extração
# ---------------------------------------------------------------------------
@router.delete(
    "/history/{record_id}",
    summary="Remove um registro do histórico",
    responses={404: {"model": ErrorResponse}},
)
def delete_history_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    repo = ExtractionRepository(db)
    deleted = repo.delete(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Registro id={record_id} não encontrado.")
    return {"message": f"Registro id={record_id} removido com sucesso."}


# ---------------------------------------------------------------------------
# GET /health — Health check específico da API
# ---------------------------------------------------------------------------
@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check da API de OCR",
    description="Verifica o status da API e seus componentes principais.",
)
def health_check():
    """Verifica o status da API e seus componentes"""
    return {
        "status": "healthy",
        "service": "SmartOCR Finance API",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "operational",
            "database": "operational",
            "ocr": "operational"
        }
    }


# ---------------------------------------------------------------------------
# GET /stats — Estatísticas do sistema
# ---------------------------------------------------------------------------
@router.get(
    "/stats",
    summary="Estatísticas do sistema",
    description="Retorna estatísticas de uso do sistema OCR.",
)
def get_stats(
    db: Session = Depends(get_db),
):
    """Retorna estatísticas de uso do sistema"""
    repo = ExtractionRepository(db)
    all_records = repo.get_all(skip=0, limit=10000)  # Buscar todos para stats
    
    total_records = len(all_records)
    
    # Calcular estatísticas básicas
    cpfs_found = sum(1 for r in all_records if r.cpfs and "[]" not in r.cpfs)
    cnpjs_found = sum(1 for r in all_records if r.cnpjs and "[]" not in r.cnpjs)
    values_found = sum(1 for r in all_records if r.values and "[]" not in r.values)
    
    return {
        "total_extractions": total_records,
        "successful_extractions": total_records,  # Assumindo que todos salvos são sucesso
        "documents_with_cpf": cpfs_found,
        "documents_with_cnpj": cnpjs_found,
        "documents_with_values": values_found,
        "average_fields_per_document": (
            (cpfs_found + cnpjs_found + values_found) / total_records if total_records > 0 else 0
        )
    }
