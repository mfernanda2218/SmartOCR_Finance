# SmartOCR Finance

Sistema em Python para extrair dados estruturados de documentos financeiros a partir de imagens, combinando pre-processamento com OpenCV, OCR com EasyOCR e parsing por expressoes regulares.

O projeto esta em fase de desenvolvimento e serve como base de estudo/portfolio em Visao Computacional, OCR, APIs e persistencia de dados.

## Status Atual

Implementado:

- Pipeline de carregamento, validacao e pre-processamento de imagens.
- Correcao de perspectiva quando um contorno de documento e detectado.
- OCR com EasyOCR.
- Parser para CPF, CNPJ, datas, valores monetarios e linhas digitaveis de boleto.
- Validadores matematicos para CPF e CNPJ.
- API FastAPI completa com endpoints de extracao, historico, health check e estatisticas.
- Banco de dados com SQLAlchemy, Repository pattern e Alembic.
- Campos avancados no modelo: tipo de documento, status de processamento, score de confianca, metadados.
- Testes unitarios para configuracao, OCR, processamento de imagem, parser, validadores, API e repositorio.
- Interface web React com Vite e Tailwind CSS.
- Componentes de upload, resultados, estatisticas e historico.
- Integracao completa entre frontend e backend.

Em evolucao:

- Docker, testes end-to-end e modelos customizados.

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes com cobertura
pytest tests/ -v --tb=short --cov=src --cov=app --cov-report=html

# Testes rápidos (sem cobertura)
pytest tests/ -v --tb=short

# Usar scripts
./scripts/run_tests.sh          # Linux/Mac
scripts\run_tests.bat           # Windows
```

### Configuração de Banco de Dados para Testes

**Opção 1: SQLite em Memória (Padrão)**
```bash
# Não precisa de configuração
pytest tests/ -v
```

**Opção 2: PostgreSQL Local**
```bash
# Criar banco
createdb smartocr_test

# Configurar variável
export TEST_DATABASE_URL="postgresql://usuario:senha@localhost:5432/smartocr_test"

# Executar testes
pytest tests/ -v
```

**Opção 3: PostgreSQL com Docker**
```bash
# Iniciar container
docker run -d --name smartocr-test-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=smartocr_test \
  -p 5433:5432 \
  postgres:15-alpine

# Configurar e executar
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5433/smartocr_test"
pytest tests/ -v
```

### Documentação de Testes
- [Guia Completo de Testes](docs/guia_testes.md) - Documentação detalhada de como testar cada módulo
- [README de Testes](tests/README.md) - Guia rápido e referência
- [Template de Testes](tests/test_template.py) - Template para criar novos testes
- [Exemplos PostgreSQL](tests/test_postgres_example.py) - Exemplos práticos com PostgreSQL

## Pipeline

```text
Imagem
  -> carregamento e validacao
  -> pre-processamento / correcao de perspectiva
  -> OCR
  -> parsing de texto
  -> validacao
  -> resposta JSON
  -> historico em banco de dados
```

## Tecnologias

| Area | Ferramentas |
|---|---|
| Linguagem | Python 3.10+ |
| API | FastAPI, Uvicorn, Pydantic |
| Visao Computacional | OpenCV, NumPy, Pillow |
| OCR | EasyOCR, pytesseract |
| Banco de dados | SQLAlchemy, Alembic, SQLite/PostgreSQL |
| Configuracao | python-dotenv, pydantic-settings |
| Logs | loguru |
| Testes | pytest, pytest-cov |
| Qualidade | ruff, black, mypy, pre-commit |
| Pacotes | uv, pyproject.toml |

## Estrutura

```text
SmartOCR_Finance/
|-- app/
|   `-- main.py                    # Ponto de entrada FastAPI
|-- src/
|   |-- smart_ocr_finance/         # Pacote principal do pipeline OCR
|   |   |-- api/                   # Rotas/schemas da API inicial
|   |   |-- config/                # Settings com pydantic-settings
|   |   |-- ocr/                   # Engine EasyOCR
|   |   |-- parser/                # Regex e extracao de campos
|   |   |-- preprocessing/         # Leitura e tratamento de imagens
|   |   |-- services/              # Orquestracao do pipeline
|   |   |-- utils/                 # Logger e configuracoes auxiliares
|   |   `-- validation/            # Validadores de documentos
|   |-- api/                       # API com historico em banco
|   |-- models/                    # Modelos SQLAlchemy
|   |-- repositories/              # CRUD do historico
|   |-- services/                  # Servicos com persistencia
|   |-- preprocessing/             # Modulos de processamento de imagem
|   |-- ocr/                       # Engine OCR
|   |-- parser/                    # Parser de campos
|   |-- utils/                     # Utilitarios e logger
|   `-- config/                    # Configuracoes centralizadas
|-- frontend/                      # Interface web React
|   |-- src/
|   |   |-- components/           # Componentes React
|   |   |-- services/              # Servico de API
|   |   |-- App.jsx               # Componente principal
|   |   `-- main.jsx              # Entry point
|   |-- package.json              # Dependencias Node.js
|   |-- tailwind.config.js        # Configuracao Tailwind
|   `-- vite.config.js            # Configuracao Vite
|-- alembic/                       # Migracoes de banco
|-- data/
|   |-- raw/                       # Imagens originais
|   |-- processed/                 # Saidas processadas
|   `-- samples/                   # Amostras para testes/experimentos
|-- docs/                          # Documentacao complementar
|-- models/                        # Modelos treinados ou baixados
|-- notebooks/                     # Experimentos
|-- tests/                         # Testes automatizados
|-- pyproject.toml                 # Metadados, dependencias e ferramentas
|-- requirements.txt               # Dependencias exportadas
|-- Makefile                       # Comandos de automacao
`-- README.md
```

## Instalacao

Pre-requisitos:

- Python 3.10 ou superior.
- `uv` instalado.
- Dependencias nativas usadas por OCR/visao computacional. No Windows, confirme que as wheels de OpenCV, PyTorch/EasyOCR e Tesseract estao disponiveis para sua versao de Python.

Passos:

```bash
git clone <url-do-repositorio>
cd SmartOCR_Finance

uv venv
uv pip install -e ".[dev,test]"

cp .env.example .env
```

No Windows PowerShell, o equivalente para copiar o `.env` e:

```powershell
Copy-Item .env.example .env
```

## Configuracao

As principais variaveis ficam em `.env`:

```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_DIR=logs
LOG_ROTATION=10 MB
LOG_RETENTION=7 days
OCR_ENGINE=tesseract
OCR_LANGUAGE=por
DATABASE_URL=sqlite:///./smartocr.db
API_HOST=0.0.0.0
API_PORT=8000
```

Observacao: o pipeline atual usa EasyOCR na engine principal. O valor `OCR_LANGUAGE=por` e mapeado para `pt` no EasyOCR, com `en` como idioma auxiliar.

## Uso

### Backend (API)

Executar a aplicacao:

```bash
python -m app.main
```

Ou diretamente com Uvicorn:

```bash
uvicorn app.main:app --reload
```

Quando a API estiver rodando, a documentacao interativa fica disponivel em:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Frontend (Interface Web)

Executar o frontend:

```bash
cd frontend
npm install
npm run dev
```

A interface web ficara disponivel em:

- `http://localhost:5173`

A interface web se comunica automaticamente com a API em `http://localhost:8000`.

### Endpoints

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/` | Status basico da API |
| `POST` | `/api/v1/extract` | Recebe uma imagem e retorna os dados extraidos |
| `GET` | `/api/v1/history` | Lista registros de extracao salvos |
| `GET` | `/api/v1/history/{record_id}` | Busca um registro por ID |
| `DELETE` | `/api/v1/history/{record_id}` | Remove um registro do historico |

Exemplo de upload:

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@data/samples/boleto.png;type=image/png"
```

Resposta esperada:

```json
{
  "cpfs": ["111.222.333-44"],
  "cnpjs": [],
  "dates": ["20/12/2023"],
  "values": ["150,00"],
  "boleto_lines": ["34191.09008 63396.873738 09516.480008 8 91320000015000"],
  "raw_text": "..."
}
```

## Banco de Dados

O projeto tem suporte inicial a persistencia de extracoes:

- Modelo ORM: `ExtractionRecord`.
- Repositorio: `ExtractionRepository`.
- Migracao inicial: `alembic/versions/0001_initial.py`.
- Banco padrao: `sqlite:///./smartocr.db`.

Comandos uteis:

```bash
alembic upgrade head
alembic revision --autogenerate -m "descricao_da_migracao"
```

## Testes e Qualidade

```bash
make test
make test-cov
make lint
make format
make typecheck
make check
```

Sem `make`, os comandos equivalentes sao:

```bash
pytest tests -v
ruff check src app tests
ruff format src app tests
mypy src
```

## Roadmap

| Fase | Tema | Status |
|---|---|---|
| 1 | Configuracao do projeto | Concluida |
| 2 | Leitura e validacao de imagens | Concluida |
| 3 | Pre-processamento | Concluida |
| 4 | Correcao de perspectiva | Concluida |
| 5 | OCR | Concluida |
| 6 | Extracao de campos | Concluida |
| 7 | Validacao de dados | Concluida |
| 8 | API FastAPI | Concluida |
| 9 | Banco de dados e historico | Concluida |
| 10 | Interface web | Concluida |
| 11 | Docker | Pendente |
| 12 | Testes end-to-end | Pendente |
| 13 | Deteccao com YOLO | Pendente |
| 14 | Treinamento de modelos | Pendente |

## Documentacao

Arquivos complementares:

- `docs/arquitetura.md` - Arquitetura do sistema e pipeline
- `docs/especificacoes_do_projeto.md` - Especificações detalhadas do projeto
- `docs/fase_01_configuracao.md` - Documentação da Fase 1
- `docs/fase_08_09_api_banco_completo.md` - Documentação completa das Fases 8 e 9 (API e Banco de Dados)
- `docs/fase_10_interface_web_react.md` - Documentação completa da Fase 10 (Interface Web React)
- `docs/plano_implementacao_fases_restantes.md` - Plano detalhado para fases 11-14

## Licenca

Projeto licenciado sob MIT. Veja `LICENSE`, se disponivel no repositorio.

## Autor

Desenvolvido como projeto de estudo e portfolio em Visao Computacional, OCR e IA aplicada a documentos financeiros.
