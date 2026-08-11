from typing import Dict, Any
from smart_ocr_finance.preprocessing.image_loader import ImageLoader
from smart_ocr_finance.preprocessing.processor import ImageProcessor
from smart_ocr_finance.ocr.engine import OCREngine
from smart_ocr_finance.parser.document_parser import DocumentParser
from smart_ocr_finance.utils.logger import log

class OCRService:
    """
    Serviço principal que orquestra as camadas de Pré-processamento,
    OCR e Parsing de Dados.
    """
    
    def __init__(self):
        # A engine é instanciada apenas uma vez por worker para não recarregar os modelos de IA
        self.engine = OCREngine()
        
    def process_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Executa o pipeline ponta-a-ponta em um documento enviado.
        """
        log.info("Iniciando processamento completo de nova imagem.")
        
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
        
        # Adiciona o texto bruto ao retorno
        extracted_data["raw_text"] = full_text
        
        log.info("Processamento de imagem concluído com sucesso.")
        return extracted_data
