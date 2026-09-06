import re

# CPF: 000.000.000-00, 00000000000
CPF_PATTERN = re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b')

# CNPJ: 00.000.000/0000-00, 00000000000000
CNPJ_PATTERN = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b')

# Data: dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy (Anos 19xx, 20xx)
DATE_PATTERN = re.compile(r'\b(?:0[1-9]|[12][0-9]|3[01])[-/.\s](?:0[1-9]|1[0-2])[-/.\s](?:19|20)\d{2}\b')

# Valores Financeiros: R$ 1.000,00, R$100,00, 100,00
# O grupo captura exatamente a parte numérica e as casas decimais.
MONEY_PATTERN = re.compile(r'(?:R\$?\s?)?(\d{1,3}(?:\.\d{3})*,\d{2})')

# Linha digitável de boleto bancário brasileiro (aprox. 47 a 48 caracteres numéricos, podendo conter espaços ou pontos)
# Estrutura base: 5 blocos -> XXXXX.XXXXX XXXXX.XXXXXX XXXXX.XXXXXX X XXXXXXXXXXXXXX
BOLETO_PATTERN = re.compile(r'\b\d{5}\.?\d{5}\s?\d{5}\.?\d{6}\s?\d{5}\.?\d{6}\s?\d\s?\d{14}\b')