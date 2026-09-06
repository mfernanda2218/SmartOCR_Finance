import easyocr
import numpy as np
from typing import List, Tuple, Any, Union
from src.config import settings
from src.utils.logger import log

class OCREngine:
    """
    Motor de Reconhecimento Óptico de Caracteres (OCR) utilizando EasyOCR.
    """
    
    def __init__(self):
        # Mapeia nosso idioma (ex: 'por') para o suporte do EasyOCR ('pt', 'en')
        lang_map = {
            'por': 'pt',
            'eng': 'en'
        }
        base_lang = lang_map.get(settings.OCR_LANGUAGE.lower(), 'en')
        
        self.langs = [base_lang]
        if base_lang != 'en':
            self.langs.append('en')
            
        log.info(f"Inicializando EasyOCR com idiomas: {self.langs}")
        try:
            # O parâmetro gpu=True tentará usar CUDA se disponível, senão cai para CPU
            self.reader = easyocr.Reader(self.langs)
            log.info("EasyOCR carregado com sucesso.")
        except Exception as e:
            log.critical(f"Falha ao inicializar EasyOCR: {e}")
            raise e

    def extract_text(self, image: np.ndarray, detail: int = 1) -> List[Any]:
        """
        Extrai o texto da imagem.
        
        Args:
            image: numpy array representando a imagem.
            detail: se 1, retorna [([[x,y],...], text, conf), ...]. Se 0, retorna apenas [text, ...].
            
        Returns:
            Lista de resultados conforme o parâmetro detail.
        """
        if image is None or image.size == 0:
            log.warning("Imagem inválida ou vazia passada para o OCR.")
            return []

        try:
            log.debug("Iniciando extração de texto (readtext)...")
            results = self.reader.readtext(image, detail=detail)
            log.debug(f"Extração concluída. {len(results)} blocos de texto identificados.")
            return results
        except Exception as e:
            log.exception(f"Erro inesperado durante a extração de texto OCR: {e}")
            return []

    def get_full_text(self, image: np.ndarray, separator: str = "\n") -> str:
        """
        Retorna todo o texto extraído concatenado.
        
        Args:
            image: numpy array representando a imagem.
            separator: Caractere usado para separar as quebras de linha ou blocos.
            
        Returns:
            String contendo todo o texto extraído.
        """
        results = self.extract_text(image, detail=0)
        return separator.join(results)