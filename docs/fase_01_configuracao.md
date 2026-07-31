# 📖 Fase 1 — Configuração do Projeto

## Objetivo

Estabelecer a fundação do projeto SmartOCR Finance com qualidade profissional, criando a estrutura de diretórios, configuração de ferramentas, sistema de logging e testes iniciais.

---

## Conceitos Aprendidos

### 1. Estrutura de Projeto Python

Um projeto Python bem organizado separa responsabilidades em módulos. A estrutura segue o princípio da **Separação de Responsabilidades (SoC)** — cada diretório e arquivo tem uma função clara e única.

**Na indústria**: Projetos como `scikit-learn`, `transformers` e `FastAPI` seguem padrões similares.

### 2. pyproject.toml (PEP 621)

O `pyproject.toml` é o arquivo padrão moderno para configurar projetos Python, substituindo o antigo `setup.py`. Ele centraliza:
- Metadados do projeto (nome, versão, autor)
- Dependências organizadas em grupos
- Configuração de ferramentas (pytest, ruff, mypy)

**Por que substituiu o setup.py?** O setup.py era um script Python executável, o que trazia riscos de segurança e complexidade. O pyproject.toml é declarativo (descreve O QUE, não COMO), mais seguro e fácil de ler.

### 3. Gerenciador de Pacotes `uv`

O `uv` é um gerenciador de pacotes Python ultrarrápido (escrito em Rust) criado pela Astral (mesma empresa do `ruff`). Ele é 10-100x mais rápido que o `pip` tradicional.

**Comparação**:
| Aspecto | pip | uv |
|---|---|---|
| Velocidade | Lento | 10-100x mais rápido |
| Resolução de deps | Básica | Avançada (backtracking) |
| Lock file | Não nativo | `uv.lock` |
| Linguagem | Python | Rust |

### 4. 12-Factor App — Configuração por Ambiente

Um dos 12 fatores para aplicações modernas é: **"Armazene configuração no ambiente"**. Isso significa:
- Nunca hardcodar valores que mudam entre ambientes
- Usar variáveis de ambiente (`.env`)
- O mesmo código roda em dev, staging e produção

### 5. Logging Estruturado com loguru

Logging é como "printf debugging" profissional. Em vez de `print()`, usamos um logger que:
- Adiciona timestamp, nível (INFO, ERROR, etc.), e localização no código
- Grava em arquivo com rotação automática
- Permite filtrar por nível (em produção, só WARNING+)
- É thread-safe

### 6. `.gitignore` para Projetos de IA/CV

Projetos de Visão Computacional e IA geram arquivos especiais que NÃO devem ser versionados:
- Modelos treinados (`.pt`, `.onnx`) — muito grandes
- Datasets (`data/raw/`) — muito grandes e potencialmente sensíveis
- Checkpoints de notebooks (`.ipynb_checkpoints/`)
- Caches de ferramentas (`.ruff_cache/`, `.mypy_cache/`)

### 7. Testes com pytest

Testes automatizados garantem que o código funciona como esperado. O pytest é o framework de teste mais popular em Python por ser:
- Conciso (sem classes obrigatórias)
- Expressivo (assertions claras)
- Extensível (plugins, fixtures)

---

## Fluxograma

```
┌──────────────────┐
│  pyproject.toml   │ ← Define o projeto e dependências
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    .env.example   │ ← Template de configuração
│        .env       │ ← Configuração local (não versionada)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  src/utils/       │
│  ├── config.py    │ ← Carrega .env → Settings dataclass
│  └── logger.py    │ ← Configura loguru com Settings
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   app/main.py     │ ← Entry point que usa config + logger
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  tests/           │ ← Valida que tudo funciona
└──────────────────┘
```

---

## Principais Funções

| Módulo | Função/Classe | Descrição |
|---|---|---|
| `config.py` | `Settings` (dataclass) | Configurações centralizadas e imutáveis |
| `config.py` | `settings` (instância) | Singleton importável diretamente |
| `config.py` | `BASE_DIR`, `DATA_DIR`, etc. | Caminhos absolutos do projeto |
| `logger.py` | `setup_logger()` | Configura sinks do loguru |
| `logger.py` | `logger` (re-export) | Logger pronto para uso |
| `main.py` | `display_banner()` | Banner ASCII do projeto |
| `main.py` | `display_config()` | Log das configurações |

---

## Melhorias Futuras

- [ ] Migrar para `pydantic-settings` na Fase 8 (integração com FastAPI)
- [ ] Adicionar `pre-commit` hooks para validação automática
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Adicionar `uv.lock` para reprodutibilidade exata
- [ ] Implementar configuração por perfil (dev/staging/prod com arquivos separados)
