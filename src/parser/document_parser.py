from typing import Dict, Any, List
from src.parser import regex_patterns
from src.utils.logger import log


class DocumentParser:
    """
    Parser responsável por aplicar heurísticas e expressões regulares
    para extrair dados estruturados a partir do texto bruto advindo do OCR.
    """
    
    @staticmethod
    def extract_all(text: str) -> Dict[str, Any]:
        """
        Aplica todas as extrações de forma automatizada e devolve um dicionário.
        """
        log.debug("Iniciando extração de campos via Regex...")
        
        # Limpar o texto removendo quebras excessivas para buscas lineares mais fáceis
        clean_text = " ".join(text.split())
        
        extracted_data = {
            "cpfs": DocumentParser.extract_cpfs(clean_text),
            "cnpjs": DocumentParser.extract_cnpjs(clean_text),
            "dates": DocumentParser.extract_dates(clean_text),
            "values": DocumentParser.extract_monetary_values(clean_text),
            "boleto_lines": DocumentParser.extract_boleto_lines(clean_text)
        }
        
        log.debug(f"Extração concluída: {extracted_data}")
        return extracted_data

    @staticmethod
    def extract_cpfs(text: str) -> List[str]:
        return regex_patterns.CPF_PATTERN.findall(text)

    @staticmethod
    def extract_cnpjs(text: str) -> List[str]:
        return regex_patterns.CNPJ_PATTERN.findall(text)

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        return regex_patterns.DATE_PATTERN.findall(text)

    @staticmethod
    def extract_monetary_values(text: str) -> List[str]:
        # Retorna apenas o valor capturado no grupo (ex: '1.200,50' de 'R$ 1.200,50')
        return regex_patterns.MONEY_PATTERN.findall(text)

    @staticmethod
    def extract_boleto_lines(text: str) -> List[str]:
        return regex_patterns.BOLETO_PATTERN.findall(text)