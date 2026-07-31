"""Módulo de validação dos dados extraídos.

Responsável por verificar a integridade e consistência
dos dados extraídos pelo parser:
- Validação de CPF/CNPJ (dígitos verificadores)
- Validação de datas
- Validação de valores monetários
- Validação de códigos de barras (módulo 10/11)
- Regras de negócio específicas por tipo de documento
"""
