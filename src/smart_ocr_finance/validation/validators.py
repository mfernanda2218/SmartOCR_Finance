import re
from smart_ocr_finance.utils.logger import log

class DocumentValidator:
    """
    Validadores matemáticos e de integridade para documentos e chaves extraídas (CPF, CNPJ, etc.).
    """

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Valida o dígito verificador do CPF.
        """
        if not cpf or not isinstance(cpf, str):
            return False
            
        cpf_clean = re.sub(r'[^0-9]', '', cpf)
        if len(cpf_clean) != 11 or cpf_clean == cpf_clean[0] * 11:
            log.warning(f"CPF inválido (formato/tamanho incorreto): {cpf}")
            return False

        # Validação do 1º Dígito
        soma = sum(int(cpf_clean[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1

        # Validação do 2º Dígito
        soma = sum(int(cpf_clean[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2

        is_valid = (str(digito1) == cpf_clean[9]) and (str(digito2) == cpf_clean[10])
        if not is_valid:
            log.warning(f"CPF com dígito verificador inválido: {cpf}")
        
        return is_valid

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """
        Valida o dígito verificador do CNPJ.
        """
        cnpj_clean = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_clean) != 14 or cnpj_clean == cnpj_clean[0] * 14:
            log.warning(f"CNPJ inválido (formato/tamanho incorreto): {cnpj}")
            return False

        # Pesos
        peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        soma = sum(int(cnpj_clean[i]) * peso1[i] for i in range(12))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1

        soma = sum(int(cnpj_clean[i]) * peso2[i] for i in range(13))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2

        is_valid = (str(digito1) == cnpj_clean[12]) and (str(digito2) == cnpj_clean[13])
        if not is_valid:
            log.warning(f"CNPJ com dígito verificador inválido: {cnpj}")
            
        return is_valid
