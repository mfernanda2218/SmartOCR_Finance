from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from smart_ocr_finance.api.schemas import OCRExtractionResponse, ErrorResponse
from smart_ocr_finance.services.ocr_service import OCRService
from smart_ocr_finance.utils.logger import log

router = APIRouter(prefix="/api/v1", tags=["OCR Extraction"])

# Dependência (Singleton improvisado)
_ocr_service_instance = None

def get_ocr_service() -> OCRService:
    global _ocr_service_instance
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()
    return _ocr_service_instance

@router.post(
    "/extract",
    response_model=OCRExtractionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Extrai dados de um documento financeiro",
    description="Recebe uma imagem (upload), corrige perspectiva, passa por OCR e extrai valores, datas, CPF/CNPJ e boletos."
)
async def extract_document_data(
    file: UploadFile = File(...),
    service: OCRService = Depends(get_ocr_service)
):
    log.info(f"Recebendo requisição de extração: Arquivo {file.filename} (Tipo: {file.content_type})")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        log.warning("Upload rejeitado: Tipo MIME inválido.")
        raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem (ex: image/jpeg, image/png).")
        
    try:
        content = await file.read()
        result = service.process_image(content)
        return result
    except ValueError as e:
        log.warning(f"Erro de validação no processamento da imagem: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.exception(f"Erro interno e inesperado no processamento OCR: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor durante o OCR.")
