# 📋 Especificações do Projeto: SmartOCR Finance

Este documento consolida todas as definições, requisitos e decisões arquiteturais estabelecidas para o projeto **SmartOCR Finance** até o momento, servindo como base para as próximas fases de implementação.

---

## 1. Visão Geral e Objetivo
O **SmartOCR Finance** é um sistema inteligente de ponta a ponta focado em processar documentos financeiros brasileiros. O objetivo principal é receber imagens de documentos, aplicar técnicas de **Visão Computacional** e **OCR (Optical Character Recognition)**, e retornar os dados extraídos de forma estruturada (JSON).

## 2. Escopo de Documentos
### 2.1. Suporte Inicial (Fase 1)
*   Boletos Bancários
*   Contas de Energia
*   Contas de Água
*   DARFs

### 2.2. Expansões Futuras
*   Notas Fiscais
*   Documentos de Identidade (CNH, RG, CPF)

---

## 3. Arquitetura e Pipeline de Processamento
O sistema foi concebido usando uma arquitetura de **pipeline sequencial**, onde o dado (imagem) flui através de vários estágios até a extração final:

1.  **Entrada**: Recebimento da imagem bruta.
2.  **Pré-processamento (`src/preprocessing`)**: Preparação da imagem utilizando OpenCV (conversão para tons de cinza, binarização adaptativa, denoising, deskew e redimensionamento inteligente).
3.  **OCR (`src/ocr`)**: Extração de texto bruto das imagens tratadas, abstraindo motores como Tesseract e EasyOCR.
4.  **Parser (`src/parser`)**: Interpretação do texto bruto com expressões regulares (Regex) e heurísticas para mapear texto livre para campos específicos de acordo com o tipo de documento.
5.  **Validação (`src/validation`)**: Garantia de integridade (validação de CPF/CNPJ, datas, valores e módulos 10/11 de códigos de barras).
6.  **Saída (`src/api`)**: Disponibilização via API REST utilizando FastAPI.

---

## 4. Stack Tecnológico e Ferramentas
O projeto segue princípios modernos de desenvolvimento em Python (PEP 621), com as seguintes escolhas tecnológicas:

*   **Linguagem base**: Python 3.10+
*   **Gerenciamento de Pacotes e Ambiente**: `uv` (extremamente rápido e confiável).
*   **Construção/Build**: `hatchling` (configurado via `pyproject.toml`).
*   **Qualidade e Formatação**: `ruff` (linter/formatter unificado) e `mypy` (checagem estática de tipos).
*   **Testes**: `pytest` com `pytest-cov` para cobertura de código.
*   **Visão Computacional e OCR**: OpenCV, Pillow, PyMuPDF, EasyOCR, pytesseract.
*   **Deep Learning**: PyTorch e YOLOv8 (para fases avançadas de detecção de regiões).
*   **API e Infraestrutura**: FastAPI (com Uvicorn), pydantic/pydantic-settings, dotenv.
*   **Banco de Dados (Fases Futuras)**: SQLAlchemy, Alembic, PostgreSQL.
*   **Logging Estruturado**: `loguru`.

---

## 5. Padrões de Projeto e Estrutura
O projeto adota **Separação de Responsabilidades (SoC)** e segue os princípios do **12-Factor App** (configuração no ambiente).

### Estrutura de Diretórios
*   `app/`: Ponto de entrada (entry points) da aplicação (`main.py`).
*   `src/`: Módulos de lógica de negócio (`api`, `ocr`, `parser`, `preprocessing`, `validation`, `utils`).
*   `tests/`: Suíte de testes automatizados.
*   `docs/`: Documentação da arquitetura e das fases do projeto.
*   `data/`: Armazenamento de imagens (raw, processed, samples) - ignorado no git.
*   `models/`: Modelos treinados - ignorado no git.

### Automação (Makefile)
Foram definidos comandos padronizados para facilitar o desenvolvimento:
*   `make install` / `make install-prod`
*   `make lint` / `make format` / `make typecheck` / `make check`
*   `make test` / `make test-cov`
*   `make run` / `make clean`

---

## 6. Status Atual (Roadmap)
A **Fase 1 (Configuração do Projeto)** foi concluída com sucesso. Isso incluiu:
*   Definição da arquitetura e pipeline.
*   Configuração do `pyproject.toml` e `.env`.
*   Estruturação dos diretórios base.
*   Implementação inicial de utils (`config.py` e `logger.py`).

**Próximo Passo (Fase 2)**: Implementação da Leitura de Imagens (carregamento de arquivos base para o pipeline).
