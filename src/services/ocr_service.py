from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import time
import json
from src.preprocessing.image_loader import ImageLoader
from src.preprocessing.processor import ImageProcessor
from src.ocr.engine import OCREngine
from src.parser.document_parser import DocumentParser
from src.repositories.extraction_repository import ExtractionRepository
from src.models.extraction_record import DocumentType, ProcessingStatus
from src.utils.logger import log


class OCRService:
    """
    Serviço principal que orquestra as camadas de Pré-processamento,
    OCR e Parsing de Dados, com persistência opcional no banco.
    """

    def __init__(self):
        # A engine é instanciada uma única vez por worker
        self.engine = OCREngine()

    def _detect_document_type(self, extracted_data: Dict[str, Any]) -> DocumentType:
        """
        Detecta o tipo de documento baseado nos campos extraídos.
        """
        if extracted_data.get("boleto_lines"):
            return DocumentType.BOLETO
        elif "energia" in extracted_data.get("raw_text", "").lower():
            return DocumentType.CONTA_ENERGIA
        elif "água" in extracted_data.get("raw_text", "").lower():
            return DocumentType.CONTA_AGUA
        elif "darf" in extracted_data.get("raw_text", "").lower():
            return DocumentType.DARF
        else:
            return DocumentType.DESCONHECIDO

    def _calculate_confidence_score(self, extracted_data: Dict[str, Any]) -> float:
        """
        Calcula um score de confiança baseado na quantidade e qualidade dos dados extraídos.
        """
        score = 0.0
        
        # Pontuação por campos encontrados
        if extracted_data.get("cpfs"):
            score += 0.25
        if extracted_data.get("cnpjs"):
            score += 0.25
        if extracted_data.get("dates"):
            score += 0.2
        if extracted_data.get("values"):
            score += 0.2
        if extracted_data.get("boleto_lines"):
            score += 0.1
        
        # Penalidade se texto bruto for muito curto
        raw_text = extracted_data.get("raw_text", "")
        if len(raw_text) < 50:
            score *= 0.5
        
        return min(score, 1.0)

    def _generate_warnings(self, extracted_data: Dict[str, Any]) -> list:
        """
        Gera warnings baseados na qualidade dos dados extraídos.
        """
        warnings = []
        
        if not extracted_data.get("cpfs") and not extracted_data.get("cnpjs"):
            warnings.append("Nenhum CPF ou CNPJ encontrado")
        
        if not extracted_data.get("dates"):
            warnings.append("Nenhuma data encontrada")
        
        if not extracted_data.get("values"):
            warnings.append("Nenhum valor monetário encontrado")
        
        raw_text = extracted_data.get("raw_text", "")
        if len(raw_text) < 100:
            warnings.append("Texto extraído muito curto, possível baixa qualidade")
        
        return warnings

    def process_image(
        self,
        image_bytes: bytes,
        filename: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Executa o pipeline ponta-a-ponta em um documento enviado.
        Se uma sessão db for fornecida, persiste o resultado no histórico.
        """
        start_time = time.time()
        log.info(f"Iniciando processamento: {filename or 'sem nome'}")

        try:
            # 1. Carregamento
            image = ImageLoader.load_image_from_bytes(image_bytes)
            if image is None:
                raise ValueError("Não foi possível carregar a imagem. Bytes inválidos.")

            if not ImageLoader.validate_image(image):
                raise ValueError("A imagem não possui formato ou dimensões válidas.")

            # 2. Pré-processamento (Correção de Perspectiva)
            warped_image = ImageProcessor.fix_perspective(image)

            # 3. OCR (Extração Bruta)
            full_text = self.engine.get_full_text(warped_image)
            log.debug(f"Texto bruto extraído ({len(full_text)} caracteres).")

            # 4. Parsing (Regex / Heurísticas)
            extracted_data = DocumentParser.extract_all(full_text)
            extracted_data["raw_text"] = full_text

            # 5. Análise avançada
            document_type = self._detect_document_type(extracted_data)
            confidence_score = self._calculate_confidence_score(extracted_data)
            warnings = self._generate_warnings(extracted_data)
            
            # Determinar status
            processing_status = ProcessingStatus.SUCCESS
            if confidence_score < 0.5:
                processing_status = ProcessingStatus.PARTIAL
            if confidence_score < 0.2:
                processing_status = ProcessingStatus.FAILED

            # 6. Persistência (se sessão de banco for fornecida)
            if db is not None:
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                repo = ExtractionRepository(db)
                
                # Usar método atualizado para salvar com novos campos
                # Como o método save atual não suporta os novos campos, vamos usar o create direto
                from src.models.extraction_record import ExtractionRecord
                
                record = ExtractionRecord(
                    filename=filename,
                    file_size=len(image_bytes),
                    document_type=document_type,
                    processing_status=processing_status,
                    processing_time_ms=processing_time_ms,
                    confidence_score=confidence_score,
                    raw_text=full_text,
                    cpfs=json.dumps(extracted_data.get("cpfs", []), ensure_ascii=False),
                    cnpjs=json.dumps(extracted_data.get("cnpjs", []), ensure_ascii=False),
                    dates=json.dumps(extracted_data.get("dates", []), ensure_ascii=False),
                    values=json.dumps(extracted_data.get("values", []), ensure_ascii=False),
                    boleto_lines=json.dumps(extracted_data.get("boleto_lines", []), ensure_ascii=False),
                    warnings=json.dumps(warnings, ensure_ascii=False) if warnings else None,
                    is_validated=False,
                    is_archived=False,
                )
                
                db.add(record)
                db.commit()
                db.refresh(record)
                
                log.info(f"Registro de extração salvo com id={record.id}, tipo={document_type}, score={confidence_score:.2f}")
                
                # Adicionar metadados ao resultado
                extracted_data["metadata"] = {
                    "record_id": record.id,
                    "document_type": document_type.value,
                    "processing_status": processing_status.value,
                    "confidence_score": confidence_score,
                    "processing_time_ms": processing_time_ms,
                    "warnings": warnings
                }

            log.info("Processamento de imagem concluído com sucesso.")
            return extracted_data

        except Exception as e:
            log.exception(f"Erro durante processamento: {e}")
            
            # Salvar registro de erro se banco disponível
            if db is not None:
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                from src.models.extraction_record import ExtractionRecord
                
                record = ExtractionRecord(
                    filename=filename,
                    file_size=len(image_bytes),
                    processing_status=ProcessingStatus.FAILED,
                    processing_time_ms=processing_time_ms,
                    error_message=str(e),
                    is_validated=False,
                    is_archived=False,
                )
                
                db.add(record)
                db.commit()
            
            raise
