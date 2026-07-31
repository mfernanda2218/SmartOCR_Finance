# 📄 SmartOCR Finance

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> Sistema inteligente de extração automática de dados de documentos financeiros utilizando **Visão Computacional** e **OCR**.

---

## 🎯 Sobre o Projeto

O **SmartOCR Finance** é um sistema de ponta a ponta para processar documentos financeiros brasileiros, extraindo informações estruturadas automaticamente a partir de imagens.

### Documentos Suportados (Fase Inicial)

| Documento | Status |
|---|---|
| Boletos Bancários | 🔜 Em desenvolvimento |
| Contas de Energia | 🔜 Em desenvolvimento |
| Contas de Água | 🔜 Em desenvolvimento |
| DARFs | 🔜 Em desenvolvimento |

### Expansões Futuras

- Notas Fiscais
- CNH / RG / CPF
- Outros documentos

---

## 🏗️ Arquitetura

```
Imagem → Pré-processamento → OCR → Parsing → Validação → API/JSON
         (OpenCV/NumPy)     (Tesseract/   (Regex/     (CPF/CNPJ/
                             EasyOCR)    Heurísticas)  Barcode)
```

---

## 🛠️ Tecnologias

| Categoria | Tecnologias |
|---|---|
| **Linguagem** | Python 3.10+ |
| **Visão Computacional** | OpenCV, NumPy, Pillow |
| **OCR** | Tesseract, EasyOCR |
| **Deep Learning** | PyTorch, YOLOv8 |
| **API** | FastAPI |
| **Testes** | pytest, pytest-cov |
| **Qualidade** | ruff, mypy, pre-commit |
| **Infraestrutura** | Docker, Git, uv |
| **Logging** | loguru |

---

## 📁 Estrutura do Projeto

```text
smart-ocr-finance/
├── app/                  # Ponto de entrada da aplicação
│   └── main.py           # Entry point principal
├── src/                  # Código-fonte
│   ├── preprocessing/    # Pré-processamento de imagens
│   ├── ocr/              # Engines de OCR
│   ├── parser/           # Extração de campos
│   ├── validation/       # Validação dos dados
│   ├── api/              # Endpoints FastAPI
│   └── utils/            # Utilitários (config, logging)
├── tests/                # Testes automatizados
├── data/                 # Dados do projeto
│   ├── raw/              # Imagens originais
│   ├── processed/        # Imagens processadas
│   └── samples/          # Imagens de exemplo
├── models/               # Modelos treinados
├── notebooks/            # Jupyter notebooks
├── docs/                 # Documentação
├── pyproject.toml        # Configuração do projeto
├── requirements.txt      # Dependências
├── Makefile              # Automação de tarefas
└── README.md             # Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes)

### Passo a passo

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd SmartOCR_Finance

# 2. Crie o ambiente virtual e instale dependências
uv venv
uv pip install -e ".[dev,test]"

# 3. Copie o arquivo de configuração
cp .env.example .env

# 4. Verifique a instalação
python -m app.main
```

### Comandos úteis (Makefile)

```bash
make install    # Instalar dependências
make test       # Rodar testes
make lint       # Verificar código
make format     # Formatar código
make run        # Executar o projeto
make clean      # Limpar temporários
```

---

## 🗺️ Roadmap

| Fase | Tema | Status |
|---|---|---|
| 1 | Configuração do Projeto | ✅ Concluída |
| 2 | Leitura de Imagens | ⏳ Pendente |
| 3 | Pré-processamento | ⏳ Pendente |
| 4 | Correção de Perspectiva | ⏳ Pendente |
| 5 | OCR | ⏳ Pendente |
| 6 | Extração de Campos | ⏳ Pendente |
| 7 | Validação dos Dados | ⏳ Pendente |
| 8 | API (FastAPI) | ⏳ Pendente |
| 9 | Banco de Dados | ⏳ Pendente |
| 10 | Interface Web | ⏳ Pendente |
| 11 | Docker | ⏳ Pendente |
| 12 | Testes End-to-End | ⏳ Pendente |
| 13 | YOLO (Detecção) | ⏳ Pendente |
| 14 | Treinamento de Modelos | ⏳ Pendente |

---

## 📝 Licença

Este projeto está licenciado sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

Desenvolvido como projeto de estudo e portfólio em Visão Computacional e IA.
