# 🏗️ Arquitetura do SmartOCR Finance

## Visão Geral

O SmartOCR Finance segue uma arquitetura de **pipeline sequencial** — cada etapa processa a saída da etapa anterior, formando uma cadeia de transformações desde a imagem bruta até os dados estruturados.

---

## Pipeline de Processamento

```
 ┌─────────────┐     ┌──────────────────┐     ┌─────────┐
 │   ENTRADA   │     │ PRÉ-PROCESSAMENTO│     │   OCR   │
 │  (Imagem)   │────▶│    (OpenCV)      │────▶│(Tesseract│
 │             │     │ • Grayscale      │     │ EasyOCR) │
 │ • Boleto    │     │ • Threshold      │     │          │
 │ • Conta     │     │ • Denoising      │     │ Texto    │
 │ • DARF      │     │ • Deskew         │     │ bruto    │
 └─────────────┘     └──────────────────┘     └────┬────┘
                                                    │
                                                    ▼
 ┌─────────────┐     ┌──────────────────┐     ┌─────────┐
 │   SAÍDA     │     │   VALIDAÇÃO      │     │ PARSER  │
 │  (JSON)     │◀────│                  │◀────│ (Regex) │
 │             │     │ • CPF/CNPJ       │     │         │
 │ Dados       │     │ • Datas          │     │ Campos  │
 │ estruturados│     │ • Valores        │     │ extraídos│
 │             │     │ • Código barras  │     │         │
 └─────────────┘     └──────────────────┘     └─────────┘
```

---

## Responsabilidade dos Módulos

### `src/preprocessing/`
**Missão**: Transformar a imagem de entrada em uma versão otimizada para OCR.

- Conversão para escala de cinza
- Binarização adaptativa (threshold)
- Remoção de ruído (filtros)
- Correção de rotação e perspectiva
- Redimensionamento inteligente

### `src/ocr/`
**Missão**: Extrair texto bruto das imagens pré-processadas.

- Abstração sobre múltiplas engines (Tesseract, EasyOCR)
- Configuração de idioma e parâmetros
- Detecção de regiões de texto (bounding boxes)
- Métricas de confiança

### `src/parser/`
**Missão**: Interpretar o texto bruto e extrair campos significativos.

- Expressões regulares para cada tipo de documento
- Heurísticas de localização de campos
- Mapeamento texto → estrutura de dados
- Suporte a múltiplos tipos de documento

### `src/validation/`
**Missão**: Garantir a integridade dos dados extraídos.

- Validação de CPF/CNPJ (dígitos verificadores)
- Validação de datas (formato e existência)
- Validação de valores monetários
- Validação de códigos de barras (módulo 10/11)

### `src/api/`
**Missão**: Expor os serviços via API REST.

- Upload de documentos (multipart/form-data)
- Processamento e retorno em JSON
- Documentação automática (Swagger/ReDoc)
- Versionamento de API

### `src/utils/`
**Missão**: Fornecer funcionalidades transversais.

- `config.py` — Configurações centralizadas
- `logger.py` — Sistema de logging
- Helpers compartilhados

---

## Decisões Arquiteturais

| Decisão | Alternativas Consideradas | Justificativa |
|---|---|---|
| Pipeline sequencial | Microserviços, event-driven | Simplicidade para projeto de estudo; fácil evolução |
| `src/` separado de `app/` | Tudo em `app/` | Lógica reutilizável independente do entry point |
| Dataclass para Settings | Pydantic, dict, JSON | Leve, nativo, type-safe; Pydantic vem na Fase 8 |
| loguru para logging | logging stdlib | API mais intuitiva, menos boilerplate |
| ruff para linting | flake8 + isort + black | Ferramenta unificada, extremamente rápida |
| uv para pacotes | pip, poetry, conda | Velocidade, simplicidade, boa resolução de deps |

---

## Evolução Planejada

```
Fase 1-7: Pipeline local (CLI)
    ↓
Fase 8-9: API + Banco de Dados
    ↓
Fase 10-11: Interface Web + Docker
    ↓
Fase 12: Testes end-to-end
    ↓
Fase 13-14: YOLO + Modelos customizados
```
