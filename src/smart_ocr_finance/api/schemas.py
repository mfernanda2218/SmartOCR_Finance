from pydantic import BaseModel, Field
from typing import List, Optional

class OCRExtractionResponse(BaseModel):
    """Schema de resposta padrão para extração OCR."""
    cpfs: List[str] = Field(description="Lista de CPFs encontrados")
    cnpjs: List[str] = Field(description="Lista de CNPJs encontrados")
    dates: List[str] = Field(description="Datas encontradas")
    values: List[str] = Field(description="Valores monetários encontrados")
    boleto_lines: List[str] = Field(description="Linhas digitáveis de boleto encontradas")
    raw_text: Optional[str] = Field(default=None, description="Texto bruto extraído pelo OCR")

class ErrorResponse(BaseModel):
    """Schema para mensagens de erro."""
    detail: str
