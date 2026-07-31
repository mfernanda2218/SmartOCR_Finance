"""Módulo de parsing (extração de campos).

Responsável por interpretar o texto extraído pelo OCR e
estruturar os dados em campos significativos como:
- Valor do documento
- Data de vencimento
- Código de barras
- Nome do beneficiário
- CNPJ/CPF

Utiliza expressões regulares e heurísticas específicas
para cada tipo de documento.
"""
