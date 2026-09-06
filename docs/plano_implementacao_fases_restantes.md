# 📋 Plano de Implementação - Fases Restantes

## 🎯 Visão Geral

Este documento apresenta o plano de implementação para as fases restantes do projeto **SmartOCR Finance**, baseado no estado atual do desenvolvimento e nas especificações originais do projeto.

---

## 📊 Status Atual do Projeto

### Fases Concluídas ✅

| Fase | Descrição | Status | Observações |
|------|-----------|--------|-------------|
| **Fase 1** | Configuração do projeto | ✅ Concluída | Estrutura de diretórios, pyproject.toml, ambiente virtual, configurações iniciais |
| **Fase 2** | Leitura de imagens | ✅ Concluída | ImageLoader implementado com validação de formato e dimensões |
| **Fase 3** | Pré-processamento | ✅ Concluída | Conversão grayscale, threshold, denoising, deskew |
| **Fase 4** | Correção de perspectiva | ✅ Concluída | Detecção de contornos e transformação de perspectiva |
| **Fase 5** | OCR | ✅ Concluída | Engine EasyOCR implementada com suporte a múltiplos idiomas |
| **Fase 6** | Extração dos campos | ✅ Concluída | Parser com regex para CPF, CNPJ, datas, valores e linhas digitáveis |
| **Fase 7** | Validação dos dados | ✅ Concluída | Validadores matemáticos para CPF/CNPJ implementados |

### Fases em Andamento 🚧

| Fase | Descrição | Status | Observações |
|------|-----------|--------|-------------|
| **Fase 8** | API | 🚧 Em andamento | FastAPI implementada com endpoints básicos, histórico funcional |
| **Fase 9** | Banco de dados | 🚧 Em andamento | SQLAlchemy, Alembic configurados, modelo ExtractionRecord criado |

### Fases Pendentes ⏳

| Fase | Descrição | Prioridade | Complexidade |
|------|-----------|------------|--------------|
| **Fase 10** | Interface Web | Alta | Média |
| **Fase 11** | Docker | Alta | Baixa |
| **Fase 12** | Testes | Alta | Média |
| **Fase 13** | YOLO para localização | Média | Alta |
| **Fase 14** | Treinamento de modelos | Baixa | Alta |

---

## 🚀 Plano Detalhado por Fase

### Fase 10: Interface Web

**Objetivo:** Criar uma interface web amigável para upload e visualização de resultados.

#### Tecnologias
- **Frontend:** HTML/CSS/JavaScript (Vanilla ou framework leve)
- **Comunicação:** Fetch API para comunicação com a API FastAPI
- **Design:** Bootstrap ou Tailwind CSS para estilização rápida

#### Implementação

##### 10.1 Estrutura do Frontend
```
frontend/
├── index.html           # Página principal
├── upload.html          # Página de upload
├── results.html         # Página de resultados
├── history.html         # Página de histórico
├── css/
│   └── styles.css       # Estilos customizados
├── js/
│   ├── api.js           # Comunicação com API
│   ├── upload.js        # Lógica de upload
│   └── results.js       # Exibição de resultados
└── assets/
    └── images/          # Imagens estáticas
```

##### 10.2 Funcionalidades Principais
- **Upload Drag & Drop:** Interface intuitiva para arrastar e soltar imagens
- **Preview de Imagem:** Visualização da imagem antes do processamento
- **Feedback Visual:** Loading spinners, progress bars, mensagens de erro/sucesso
- **Exibição de Resultados:** Formatação bonita dos dados extraídos (CPF, CNPJ, valores, etc.)
- **Histórico Visual:** Tabela com cards para visualizar extrações anteriores
- **Responsividade:** Funcionamento em desktop e mobile

##### 10.3 Integração com API
```javascript
// Exemplo de chamada API
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/api/v1/extract', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

##### 10.4 Configuração no FastAPI
```python
# Adicionar rota para servir arquivos estáticos
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="frontend"), name="frontend")

# Redirecionar root para frontend
@app.get("/")
async def root():
    return FileResponse('frontend/index.html')
```

#### Deliverables
- [ ] Estrutura de diretórios do frontend
- [ ] Página principal com navegação
- [ ] Página de upload funcional
- [ ] Página de resultados formatada
- [ ] Página de histórico com tabela
- [ ] Integração completa com API
- [ ] Estilização responsiva
- [ ] Tratamento de erros e feedback visual

#### Tempo Estimado: 3-5 dias

---

### Fase 11: Docker

**Objetivo:** Containerizar a aplicação para facilitar deployment e reprodução de ambiente.

#### Tecnologias
- **Docker:** Containerização
- **Docker Compose:** Orquestração de múltiplos containers
- **Multi-stage build:** Otimização de imagem final

#### Implementação

##### 11.1 Dockerfile
```dockerfile
# Stage 1: Build
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de runtime apenas
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências do builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/raw data/processed data/samples logs models

# Expor porta
EXPOSE 8000

# Comando de启动
CMD ["python", "-m", "app.main"]
```

##### 11.2 Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/smartocr
      - LOG_LEVEL=INFO
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=smartocr
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

##### 11.3 Scripts Auxiliares
```bash
# scripts/docker-build.sh
#!/bin/bash
docker-compose build

# scripts/docker-up.sh
#!/bin/bash
docker-compose up -d

# scripts/docker-down.sh
#!/bin/bash
docker-compose down

# scripts/docker-logs.sh
#!/bin/bash
docker-compose logs -f app
```

##### 11.4 .dockerignore
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.git/
.gitignore
.env
data/raw/*
data/processed/*
logs/*.log
models/*.pt
models/*.onnx
```

#### Deliverables
- [ ] Dockerfile otimizado
- [ ] docker-compose.yml com serviços app e db
- [ ] Scripts de automação Docker
- [ ] .dockerignore configurado
- [ ] Documentação de uso
- [ ] Testes de container local

#### Tempo Estimado: 2-3 dias

---

### Fase 12: Testes

**Objetivo:** Implementar testes end-to-end e aumentar cobertura de testes existentes.

#### Tecnologias
- **pytest:** Framework de testes
- **pytest-cov:** Cobertura de código
- **httpx:** Cliente HTTP assíncrono para testes de API
- **pytest-asyncio:** Suporte a testes assíncronos
- **factory-boy:** Factory para criação de dados de teste

#### Implementação

##### 12.1 Testes End-to-End (E2E)
```python
# tests/test_e2e.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_extraction_flow():
    """Testa o fluxo completo de extração"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Upload de imagem
        with open("tests/fixtures/sample_boleto.png", "rb") as f:
            response = await client.post(
                "/api/v1/extract",
                files={"file": ("boleto.png", f, "image/png")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validar estrutura da resposta
        assert "cpfs" in data
        assert "cnpjs" in data
        assert "dates" in data
        assert "values" in data
        assert "boleto_lines" in data
        assert "raw_text" in data
        
        # Validar que dados foram persistidos
        history_response = await client.get("/api/v1/history")
        assert history_response.status_code == 200
        assert len(history_response.json()["records"]) > 0
```

##### 12.2 Testes de Integração
```python
# tests/test_integration.py
import pytest
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.services.ocr_service import OCRService

def test_ocr_service_with_database():
    """Testa integração do serviço OCR com banco de dados"""
    # Setup: criar sessão de teste
    db = next(get_db())
    
    # Test: processar imagem com persistência
    service = OCRService()
    with open("tests/fixtures/sample.png", "rb") as f:
        result = service.process_image(f.read(), filename="test.png", db=db)
    
    # Assert: validar resultado
    assert result["cpfs"] is not None
    assert result["raw_text"] is not None
    
    # Assert: validar persistência
    from src.repositories.extraction_repository import ExtractionRepository
    repo = ExtractionRepository(db)
    records = repo.get_all()
    assert len(records) > 0
```

##### 12.3 Fixtures Compartilhadas
```python
# tests/conftest.py (extendido)
import pytest
from PIL import Image
import io

@pytest.fixture
def sample_image_bytes():
    """Cria uma imagem de teste em bytes"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()

@pytest.fixture
def sample_boleto_image():
    """Carrega uma imagem de boleto real para testes"""
    with open("tests/fixtures/real_boleto.png", "rb") as f:
        return f.read()

@pytest.fixture
def clean_database():
    """Limpa o banco de dados antes e depois do teste"""
    db = next(get_db())
    db.query(ExtractionRecord).delete()
    db.commit()
    yield db
    db.query(ExtractionRecord).delete()
    db.commit()
```

##### 12.4 Testes de Performance
```python
# tests/test_performance.py
import pytest
import time
from src.services.ocr_service import OCRService

def test_ocr_performance():
    """Valida que o OCR processa imagem em tempo aceitável"""
    service = OCRService()
    
    with open("tests/fixtures/sample.png", "rb") as f:
        start_time = time.time()
        result = service.process_image(f.read())
        elapsed_time = time.time() - start_time
    
    # OCR deve completar em menos de 10 segundos
    assert elapsed_time < 10, f"OCR demorou {elapsed_time:.2f}s (limite: 10s)"
```

##### 12.5 Configuração de Cobertura
```ini
# pytest.ini (extendido)
[tool:pytest]
addopts = 
    -v 
    --tb=short
    --cov=src
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

#### Deliverables
- [ ] Testes E2E do fluxo principal
- [ ] Testes de integração API + Banco
- [ ] Fixtures compartilhadas
- [ ] Testes de performance
- [ ] Cobertura de código >= 80%
- [ ] Documentação de testes
- [ ] Scripts de execução de testes

#### Tempo Estimado: 4-6 dias

---

### Fase 13: YOLO para Localizar Automaticamente o Documento

**Objetivo:** Implementar detecção automática de documentos em imagens usando YOLO para melhorar a precisão do OCR.

#### Tecnologias
- **YOLOv8:** Modelo de detecção de objetos
- **Ultralytics:** Biblioteca para treinar e usar YOLO
- **OpenCV:** Processamento de imagens
- **PyTorch:** Backend do YOLO

#### Implementação

##### 13.1 Estrutura de Módulo YOLO
```
src/yolo/
├── __init__.py
├── detector.py           # Detector YOLO principal
├── model_trainer.py      # Treinamento de modelos customizados
├── preprocessor.py      # Pré-processamento para YOLO
└── utils.py              # Utilitários YOLO
```

##### 13.2 Detector YOLO
```python
# src/yolo/detector.py
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple, Optional

class DocumentDetector:
    """Detecta documentos em imagens usando YOLO"""
    
    def __init__(self, model_path: str = "models/document_detector.pt"):
        """Inicializa detector com modelo pré-treinado"""
        self.model = YOLO(model_path)
        
    def detect_documents(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta documentos na imagem e retorna bounding boxes.
        Retorna lista de (x1, y1, x2, y2)
        """
        results = self.model(image)
        
        bboxes = []
        for result in results:
            for box in result.boxes:
                # Filtrar apenas classe "document"
                if box.cls == 0:  # Assumindo classe 0 = documento
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bboxes.append((int(x1), int(y1), int(x2), int(y2)))
        
        return bboxes
    
    def crop_document(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Recorta o documento da imagem baseado no bounding box"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]
    
    def detect_and_crop(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta o documento principal e retorna o recorte.
        Retorna None se nenhum documento for detectado.
        """
        bboxes = self.detect_documents(image)
        
        if not bboxes:
            return None
        
        # Retornar o maior bounding box (documento principal)
        main_bbox = max(bboxes, key=lambda b: (b[2]-b[0]) * (b[3]-b[1]))
        return self.crop_document(image, main_bbox)
```

##### 13.3 Integração com Pipeline OCR
```python
# src/services/ocr_service.py (modificado)
from src.yolo.detector import DocumentDetector

class OCRService:
    def __init__(self):
        self.engine = OCREngine()
        self.document_detector = DocumentDetector()  # Novo
        
    def process_image(self, image_bytes: bytes, filename: str = None, db: Session = None) -> Dict[str, Any]:
        # 1. Carregamento
        image = ImageLoader.load_image_from_bytes(image_bytes)
        
        # 2. Detecção de documento com YOLO (NOVO)
        detected_document = self.document_detector.detect_and_crop(image)
        if detected_document is not None:
            image = detected_document
            log.info("Documento detectado automaticamente com YOLO")
        else:
            log.warning("Nenhum documento detectado, usando imagem original")
        
        # 3. Pré-processamento
        warped_image = ImageProcessor.fix_perspective(image)
        
        # ... restante do pipeline
```

##### 13.4 Dataset para Treinamento
```
data/yolo_dataset/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── data.yaml
```

##### 13.5 Configuração de Treinamento
```yaml
# data/yolo_dataset/data.yaml
path: ../data/yolo_dataset
train: train/images
val: val/images

names:
  0: document
  1: boleto
  2: conta
  3: darf
```

##### 13.6 Script de Treinamento
```python
# src/yolo/model_trainer.py
from ultralytics import YOLO

class ModelTrainer:
    """Treina modelos YOLO customizados"""
    
    def __init__(self, model_size: str = "n"):
        """
        model_size: n (nano), s (small), m (medium), l (large), x (extra large)
        """
        self.model = YOLO(f"yolov8{model_size}.pt")
        
    def train(self, data_yaml: str, epochs: int = 100, imgsz: int = 640):
        """Treina o modelo com dataset customizado"""
        results = self.model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=16,
            device="0",  # GPU se disponível
            project="models",
            name="document_detector"
        )
        return results
    
    def export(self, format: str = "onnx"):
        """Exporta modelo para formato específico"""
        self.model.export(format=format)
```

#### Deliverables
- [ ] Módulo detector YOLO implementado
- [ ] Integração com pipeline OCR
- [ ] Dataset de treinamento organizado
- [ ] Script de treinamento funcional
- [ ] Modelo pré-treinado para detecção de documentos
- [ ] Documentação de uso e treinamento
- [ ] Testes de detecção

#### Tempo Estimado: 7-10 dias

---

### Fase 14: Treinamento de Modelos Próprios

**Objetivo:** Desenvolver e treinar modelos customizados para tarefas específicas do domínio financeiro.

#### Tecnologias
- **PyTorch:** Framework de deep learning
- **Transformers:** Modelos de NLP para parsing avançado
- **Custom Vision API:** Treinamento de modelos de visão customizados
- **TensorFlow/ONNX:** Alternativas para deployment

#### Implementação

##### 14.1 Tipos de Modelos Customizados

###### 14.1.1 Modelo de Classificação de Documentos
```python
# src/models/document_classifier.py
import torch
import torch.nn as nn
from torchvision import models, transforms

class DocumentClassifier(nn.Module):
    """Classifica tipo de documento (boleto, conta, darf, etc)"""
    
    def __init__(self, num_classes: int = 4):
        super().__init__()
        # Usar ResNet pré-treinada
        self.base_model = models.resnet50(pretrained=True)
        
        # Modificar última camada
        num_features = self.base_model.fc.in_features
        self.base_model.fc = nn.Linear(num_features, num_classes)
        
    def forward(self, x):
        return self.base_model(x)
```

###### 14.1.2 Modelo de Extração de Campos com NLP
```python
# src/models/field_extractor.py
from transformers import AutoTokenizer, AutoModelForTokenClassification

class FieldExtractor:
    """Extrai campos específicos usando NLP"""
    
    def __init__(self, model_name: str = "bert-base-portuguese-cased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        
    def extract_fields(self, text: str) -> Dict[str, str]:
        """Extrai campos usando NER (Named Entity Recognition)"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        
        # Processar outputs para extrair entidades
        # Implementar lógica de NER customizada
        return self._process_ner_outputs(outputs)
```

##### 14.2 Pipeline de Treinamento
```python
# src/models/training_pipeline.py
import torch
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import os

class DocumentDataset(Dataset):
    """Dataset para treinamento de classificação"""
    
    def __init__(self, data_dir: str, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.classes = os.listdir(data_dir)
        self.samples = self._load_samples()
        
    def _load_samples(self):
        samples = []
        for class_name in self.classes:
            class_dir = os.path.join(self.data_dir, class_name)
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                samples.append((img_path, self.classes.index(class_name)))
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        return image, label

def train_classifier():
    """Pipeline completo de treinamento"""
    # Configurações
    batch_size = 32
    learning_rate = 0.001
    epochs = 50
    
    # Transformações
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Dataset e DataLoader
    train_dataset = DocumentDataset("data/training/train", transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Modelo
    model = DocumentClassifier(num_classes=4)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Treinamento
    for epoch in range(epochs):
        model.train()
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
    
    # Salvar modelo
    torch.save(model.state_dict(), "models/document_classifier.pth")
```

##### 14.3 Fine-tuning de Modelos Pré-treinados
```python
# src/models/fine_tuning.py
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments

def fine_tune_bert():
    """Fine-tune BERT para classificação de documentos"""
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-portuguese-cased", 
        num_labels=4
    )
    
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset
    )
    
    trainer.train()
```

##### 14.4 Avaliação de Modelos
```python
# src/models/evaluation.py
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

def evaluate_model(model, test_loader):
    """Avalia modelo e gera métricas"""
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Métricas
    print(classification_report(all_labels, all_preds))
    
    # Matriz de confusão
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, cmap='Blues')
    plt.title('Matriz de Confusão')
    plt.colorbar()
    plt.savefig('models/confusion_matrix.png')
```

##### 14.5 Dataset para Treinamento
```
data/training/
├── train/
│   ├── boletos/
│   ├── contas/
│   ├── darfs/
│   └── outros/
├── val/
│   ├── boletos/
│   ├── contas/
│   ├── darfs/
│   └── outros/
└── test/
    ├── boletos/
    ├── contas/
    ├── darfs/
    └── outros/
```

#### Deliverables
- [ ] Modelo de classificação de documentos
- [ ] Modelo de extração de campos com NLP
- [ ] Pipeline de treinamento implementado
- [ ] Script de fine-tuning
- [ ] Sistema de avaliação de modelos
- [ ] Dataset organizado e documentado
- [ ] Modelos treinados e salvos
- [ ] Documentação de treinamento e uso

#### Tempo Estimado: 10-15 dias

---

## 🔄 Consolidação de Namespaces

### Problema Identificado
O projeto atual possui dois namespaces paralelos:
- `src/smart_ocr_finance/*` - Implementação original do pipeline
- `src/*` - Nova implementação com API e banco de dados

### Solução Proposta
Consolidar tudo em `src/*` e remover o namespace antigo:

#### Passos de Migração
1. **Mover módulos do `smart_ocr_finance` para `src`**
   - `smart_ocr_finance/preprocessing/*` → `src/preprocessing/*`
   - `smart_ocr_finance/ocr/*` → `src/ocr/*`
   - `smart_ocr_finance/parser/*` → `src/parser/*`
   - `smart_ocr_finance/validation/*` → `src/validation/*`
   - `smart_ocr_finance/utils/*` → `src/utils/*`

2. **Atualizar imports em todo o projeto**
   - Substituir `from smart_ocr_finance.X import Y` por `from src.X import Y`

3. **Remover diretório antigo**
   - Deletar `src/smart_ocr_finance/` após migração completa

4. **Atualizar testes**
   - Ajustar imports nos arquivos de teste

5. **Validação**
   - Executar testes para garantir funcionamento
   - Verificar não haver referências ao namespace antigo

#### Benefícios
- Código mais limpo e organizado
- Manutenção simplificada
- Eliminação de duplicidade
- Imports mais consistentes

---

## 📈 Cronograma Sugerido

### Sprint 1: Interface Web (Fase 10)
- **Semana 1:** Estrutura e upload funcional
- **Semana 2:** Páginas de resultados e histórico
- **Semana 3:** Integração completa e testes

### Sprint 2: Docker (Fase 11)
- **Semana 4:** Dockerfile e docker-compose
- **Semana 5:** Scripts e documentação

### Sprint 3: Testes (Fase 12)
- **Semana 6:** Testes E2E e integração
- **Semana 7:** Cobertura e performance

### Sprint 4: YOLO (Fase 13)
- **Semana 8-9:** Detector YOLO e integração
- **Semana 10:** Dataset e treinamento básico

### Sprint 5: Modelos Customizados (Fase 14)
- **Semana 11-13:** Desenvolvimento de modelos
- **Semana 14:** Treinamento e avaliação

### Sprint 6: Consolidação
- **Semana 15:** Migração de namespaces
- **Semana 16:** Testes finais e documentação

---

## 🎯 Critérios de Sucesso

### Por Fase

#### Fase 10 (Interface Web)
- [ ] Interface funcional e responsiva
- [ ] Integração completa com API
- [ ] Experiência de usuário intuitiva
- [ ] Feedback visual adequado

#### Fase 11 (Docker)
- [ ] Aplicação roda em container
- [ ] Build otimizado (< 1GB)
- [ ] docker-compose funcional
- [ ] Documentação clara de uso

#### Fase 12 (Testes)
- [ ] Cobertura de código >= 80%
- [ ] Testes E2E funcionando
- [ ] Testes de performance implementados
- [ ] Pipeline de CI configurado

#### Fase 13 (YOLO)
- [ ] Detecção de documentos funcionando
- [ ] Integração com pipeline OCR
- [ ] Modelo treinado com dataset próprio
- [ ] Melhoria na precisão do OCR

#### Fase 14 (Modelos Customizados)
- [ ] Modelo de classificação treinado
- [ ] Modelo de extração NLP funcional
- [ ] Pipeline de treinamento automatizado
- [ ] Avaliação e métricas documentadas

### Gerais
- [ ] Código limpo e bem documentado
- [ ] Seguidas as convenções do projeto
- [ ] Testes passando
- [ ] Performance aceitável
- [ ] Documentação atualizada

---

## 🛠️ Dependências e Pré-requisitos

### Para Fase 10 (Interface Web)
- Navegador moderno (Chrome, Firefox, Edge)
- Servidor de desenvolvimento local
- Conhecimento básico de HTML/CSS/JavaScript

### Para Fase 11 (Docker)
- Docker Desktop instalado
- Conhecimento básico de containers
- Acesso a internet para download de imagens

### Para Fase 12 (Testes)
- Pytest e plugins instalados
- Ambiente de teste configurado
- Dados de teste disponíveis

### Para Fase 13 (YOLO)
- GPU NVIDIA (opcional, mas recomendado)
- CUDA instalado (se usando GPU)
- Dataset de documentos para treinamento
- Ultralytics instalado

### Para Fase 14 (Modelos Customizados)
- PyTorch instalado
- GPU com memória suficiente (8GB+)
- Dataset grande e diversificado
- Transformers instalado (para NLP)

---

## 📚 Recursos e Referências

### Documentação Oficial
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)

### Tutoriais e Guias
- [FastAPI CRUD Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/best-practices.html)
- [YOLO Training Guide](https://docs.ultralytics.com/modes/train/)

### Comunidades
- [FastAPI Discord](https://discord.com/invite/fastapi)
- [PyTorch Forums](https://discuss.pytorch.org/)
- [Stack Overflow](https://stackoverflow.com/)

---

## 🚨 Riscos e Mitigações

### Riscos Identificados

#### Fase 10 (Interface Web)
- **Risco:** Complexidade de integração frontend-backend
- **Mitigação:** Começar com interface simples, evoluir gradualmente

#### Fase 11 (Docker)
- **Risco:** Imagem final muito grande
- **Mitigação:** Usar multi-stage builds, otimizar dependências

#### Fase 12 (Testes)
- **Risco:** Baixa cobertura de código
- **Mitigação:** Estabelecer metas de cobertura desde o início

#### Fase 13 (YOLO)
- **Risco:** Dataset insuficiente para treinamento
- **Mitigação:** Usar data augmentation, modelos pré-treinados

#### Fase 14 (Modelos Customizados)
- **Risco:** Overfitting no treinamento
- **Mitigação:** Validação cruzada, regularização, dropout

### Mitigações Gerais
- Desenvolvimento iterativo com validação constante
- Testes automatizados em cada fase
- Documentação detalhada de decisões
- Code review entre fases

---

## 📝 Conclusão

Este plano fornece um roadmap claro e detalhado para completar as fases restantes do projeto SmartOCR Finance. A implementação deve seguir uma abordagem iterativa, com validação constante e foco em qualidade e manutenibilidade.

As fases estão organizadas por complexidade e dependências, permitindo um fluxo natural de desenvolvimento. A consolidação de namespaces é recomendada para ser realizada antes das fases avançadas (YOLO e Modelos Customizados) para simplificar a base de código.

Sucesso na implementação! 🚀