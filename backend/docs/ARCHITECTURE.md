# 📚 JSON → MySQL BULK LOADER - ARQUITETURA PROFISSIONAL

**Versão:** 2.0.0 (Refatorado)  
**Arquitetura:** Camadas com Separação de Responsabilidades  
**Status:** ✅ Pronto para Produção  
**Data:** 28 de janeiro de 2026

---

## 📑 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura](#-arquitetura)
3. [Estrutura de Diretórios](#-estrutura-de-diretórios)
4. [Componentes Principais](#-componentes-principais)
5. [Padrões de Design](#-padrões-de-design)
6. [Como Usar](#-como-usar)
7. [Exemplos](#-exemplos)
8. [Extensibilidade](#-extensibilidade)

---

## 🎯 Visão Geral

Aplicação profissional Python para carregar arquivos JSON em MySQL, construída com:

✅ **Separação de responsabilidades** - Cada camada tem seu propósito  
✅ **Configuração centralizada** - 12-factor app compliant  
✅ **Logging estruturado** - Rastreamento completo de operações  
✅ **Type hints** - Code autocomplete e verificação em tempo de escrita  
✅ **Padrões SOLID** - Extensível e testável  
✅ **Tratamento de erros** - Exceções customizadas e sensatas  
✅ **Gerenciamento de recursos** - Pool de conexões otimizado  
✅ **Alta performance** - Múltiplos modos de carregamento  

---

## 🏗️ Arquitetura

A aplicação segue arquitetura em **camadas** com padrão **Singleton** para recursos compartilhados:

```
┌─────────────────────────────────────────────┐
│         PRESENTATION LAYER                  │
│  (Scripts CLI, Interfaces de Usuário)       │
│  scripts/main.py                            │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│         APPLICATION LAYER                   │
│  (Lógica de Negócio, Orquestra componentes) │
│  app/application.py                         │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│         DOMAIN LAYER                        │
│  (Loaders, Validators, Normalizers)         │
│  app/loaders/, app/validators/              │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│         INFRASTRUCTURE LAYER                │
│  (Database, Logger, Config, Utils)          │
│  app/core/, app/utils/, config/             │
└─────────────────────────────────────────────┘
```

### Padrões Utilizados

| Padrão | Implementação | Benefício |
|--------|---------------|-----------|
| **Singleton** | `DatabaseManager`, `config()` | Uma única instância de recursos |
| **Factory** | `ApplicationConfig`, `JSONParser` | Criação flexível de objetos |
| **Strategy** | `BaseLoader` + `QuickLoader` | Múltiplas estratégias de carregamento |
| **Repository** | `DatabaseManager` | Isolação da lógica de acesso ao DB |
| **Decorator** | `setup_logger` | Logging transparente |

---

## 📁 Estrutura de Diretórios

```
json-mysql-bulk/
│
├── 📁 app/                    ← Código da aplicação
│   ├── 📁 core/               ← Componentes fundamentais
│   │   ├── logger.py          ← Logging estruturado com cores
│   │   ├── database.py        ← Gerenciador de conexões (Singleton)
│   │   ├── exceptions.py      ← Exceções customizadas
│   │   └── __init__.py        ← Exports
│   │
│   ├── 📁 loaders/            ← Estratégias de carregamento
│   │   ├── base.py            ← Classe base abstrata
│   │   ├── quick_loader.py    ← Loader rápido (INSERT)
│   │   ├── load_loader.py     ← Loader LOAD DATA (rápido)
│   │   ├── upsert_loader.py   ← Loader UPSERT (inteligente)
│   │   └── __init__.py        ← Exports
│   │
│   ├── 📁 normalizers/        ← Normalização de dados
│   │   ├── json_normalizer.py ← Normaliza JSON aninhado
│   │   ├── field_normalizer.py← Normaliza campos
│   │   └── __init__.py
│   │
│   ├── 📁 validators/         ← Validação de dados
│   │   └── __init__.py        ← DataValidator, ReferentialValidator
│   │
│   ├── 📁 utils/              ← Utilitários
│   │   ├── json_handler.py    ← Parser e processamento JSON
│   │   ├── schema_manager.py  ← Inferência e gestão de schema
│   │   ├── formatters.py      ← Formatadores de dados
│   │   └── __init__.py        ← Exports
│   │
│   ├── 📁 interfaces/         ← Interfaces do sistema
│   │   ├── cli.py             ← Interface de linha de comando
│   │   ├── api.py             ← Interface REST (futuro)
│   │   └── __init__.py
│   │
│   ├── application.py         ← Classe principal (Orquestrador)
│   └── __init__.py            ← Exports principais
│
├── 📁 config/                 ← Configuração
│   ├── settings.py            ← Configuração centralizada (12-factor)
│   ├── logging_config.py      ← Configuração de logging
│   └── __init__.py            ← Exports
│
├── 📁 scripts/                ← Scripts executáveis
│   ├── main.py                ← CLI principal
│   ├── migrate.py             ← Normalização de JSON
│   ├── validate.py            ← Validação de dados
│   └── infer_schema.py        ← Inferência de schema
│
├── 📁 tests/                  ← Testes
│   ├── test_loaders.py        ← Testes de loaders
│   ├── test_validators.py     ← Testes de validadores
│   ├── test_json_handler.py   ← Testes de JSON
│   ├── test_database.py       ← Testes de BD
│   ├── fixtures/              ← Dados de teste
│   │   ├── sample_ndjson.json
│   │   └── sample_array.json
│   └── conftest.py            ← Configuração pytest
│
├── 📁 docs/                   ← Documentação
│   ├── ARCHITECTURE.md        ← Esse arquivo
│   ├── API.md                 ← API Reference
│   ├── DEPLOYMENT.md          ← Deploy guide
│   ├── CONTRIBUTING.md        ← Guia de contribuição
│   └── EXAMPLES.md            ← Exemplos de uso
│
├── 📁 data/                   ← Arquivos de entrada
│   ├── DataPagto.json
│   └── ExtratoClienteHistorico.json
│
├── 📁 output/                 ← Arquivos de saída
│   └── .gitkeep
│
├── 📁 logs/                   ← Arquivos de log
│   └── .gitkeep
│
├── .env                       ← Variáveis de ambiente (gitignored)
├── .env.example               ← Template de .env
├── .gitignore                 ← Git exclusions
├── README.md                  ← Documentação principal
├── DOCUMENTACAO_COMPLETA.md   ← Documentação detalhada
├── pyproject.toml             ← Configuração do projeto Python
├── requirements.txt           ← Dependências Python
├── setup.py                   ← Setup script (se necessário)
├── Makefile                   ← Automação (make test, make run, etc)
├── Dockerfile                 ← Containerização
├── docker-compose.yml         ← Orquestração (app + MySQL)
├── LICENSE                    ← Licença MIT
└── .github/
    └── workflows/
        └── tests.yml          ← CI/CD (GitHub Actions)
```

---

## 🔧 Componentes Principais

### 1. **Core Layer** (`app/core/`)

#### DatabaseManager (Singleton)
```python
from app.core import DatabaseManager

# Inicializa uma única vez
DatabaseManager.initialize(database_url)

# Usa em qualquer lugar
engine = DatabaseManager.get_engine()
DatabaseManager.test_connection()
DatabaseManager.table_exists('my_table')

# Context managers
with DatabaseManager.connection() as conn:
    result = conn.execute(text("SELECT 1"))

with DatabaseManager.session() as session:
    # auto-commit ao sair
    pass
```

#### Logger Estruturado
```python
from app.core import setup_logger, get_logger

# Setup inicial
logger = setup_logger(__name__)

# Uso posterior
logger = get_logger(__name__)
logger.info("Operação bem-sucedida")
logger.error("Erro crítico", exc_info=True)
```

#### Exceções Customizadas
```python
from app.core import (
    JSONMySQLException,
    ConfigurationError,
    DatabaseError,
    ValidationError,
    LoaderError,
)

try:
    app.load_json(...)
except LoaderError as e:
    handle_loader_error(e)
except DatabaseError as e:
    handle_database_error(e)
```

### 2. **Domain Layer** (`app/loaders/`, `app/validators/`)

#### Loaders (Strategy Pattern)
```python
from app.loaders import QuickLoader, LoadResult

loader = QuickLoader(config)
result: LoadResult = loader.load(
    file_path='data/arquivo.json',
    table_name='minha_tabela',
    lines=False,
    if_exists='append',
)

print(f"Sucesso: {result.success}")
print(f"Registros: {result.rows_inserted}")
print(f"Taxa de sucesso: {result.success_rate}%")
```

#### Validators
```python
from app.validators import DataValidator, ReferentialValidator

# Validação de dados
valid, errors = DataValidator.validate_no_nulls(
    df, required_columns=['id', 'name']
)

# Validação de integridade referencial
valid, errors = ReferentialValidator.validate_foreign_key(
    child_df, 'customer_id',
    parent_df, 'id'
)
```

### 3. **Utils Layer** (`app/utils/`)

#### JSONParser
```python
from app.utils import JSONParser

# Parse arquivo
data = JSONParser.parse_file(
    'data/arquivo.json',
    lines=True,  # NDJSON
    sample_size=100  # Primeiras 100 linhas
)

# Itera em chunks (economiza memória)
for chunk in JSONParser.iterate_file('data/arquivo.json', chunk_size=5000):
    process(chunk)
```

#### SchemaInferencer
```python
from app.utils import SchemaInferencer
import pandas as pd

df = pd.DataFrame(data)
types = SchemaInferencer.infer_types(df)
# {'id': 'BIGINT(20)', 'name': 'VARCHAR(255)', ...}

ddl = SchemaInferencer.generate_create_table(
    'my_table', df,
    indexes=['created_at']
)
# CREATE TABLE my_table (...)
```

### 4. **Application Layer** (`app/application.py`)

```python
from app.application import JSONMySQLApplication, ApplicationConfig

# Config
app_config = ApplicationConfig(
    env='production',
    debug=False,
    loader_mode='quick',
    chunk_size=5000,
)

# Aplicação
app = JSONMySQLApplication(app_config)

# Carregar um arquivo
result = app.load_json(
    Path('data/arquivo.json'),
    'minha_tabela',
    if_exists='replace'
)

# Carregar múltiplos
results = app.load_multiple(
    [Path('data/file1.json'), Path('data/file2.json')]
)

# Inferir schema
ddl = app.infer_schema(Path('data/arquivo.json'))

# Info da tabela
info = app.get_table_info('minha_tabela')
```

### 5. **Configuration** (`config/settings.py`)

```python
from config import get_config, Environment, LoaderMode

# Carrega automaticamente
cfg = get_config('production')

# Ou cria explicitamente
from config import AppConfig, DatabaseConfig

db_config = DatabaseConfig(
    host='localhost',
    port=3306,
    user='root',
    password='senha',
    database='meu_banco',
)

app_cfg = AppConfig(
    env=Environment.PRODUCTION,
    database=db_config,
)
```

---

## 🎨 Padrões de Design

### Singleton Pattern
```python
# DatabaseManager é singleton
db1 = DatabaseManager.get_engine()
db2 = DatabaseManager.get_engine()
assert db1 is db2  # Mesma instância
```

### Factory Pattern
```python
# JSONParser é factory
data = JSONParser.parse_file(file_path)  # Factory method

# Retorna diferentes tipos conforme formato
```

### Strategy Pattern
```python
# Loaders seguem strategy
loaders = {
    'quick': QuickLoader(),
    'load': LoadLoader(),
    'upsert': UpsertLoader(),
}

result = loaders['quick'].load(file, table)
```

### Repository Pattern
```python
# DatabaseManager funciona como repository
DatabaseManager.table_exists(table)
DatabaseManager.get_table_columns(table)
DatabaseManager.execute(query)
```

---

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone e setup
git clone ...
cd json-mysql-bulk
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Copie o template
cp .env.example .env

# Edite .env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=seu_banco
```

### 3. Uso via CLI

```bash
# Arquivo único
python scripts/main.py --file data/arquivo.json --table minha_tabela

# Diretório
python scripts/main.py --dir data/ --pattern "*.json"

# Modo load (mais rápido)
python scripts/main.py --file data/arquivo.json --table tab --mode load

# Debug
python scripts/main.py --file data/arquivo.json --table tab --debug
```

### 4. Uso via Python

```python
from app.application import JSONMySQLApplication
from pathlib import Path

app = JSONMySQLApplication()
result = app.load_json(Path('data/arquivo.json'), 'minha_tabela')

print(result)  # ✓ minha_tabela: 1000 registros (100% sucesso) em 5.23s
```

---

## 📖 Exemplos

### Exemplo 1: Carregar arquivo simples

```python
from app.application import JSONMySQLApplication

app = JSONMySQLApplication()
result = app.load_json(
    Path('data/customers.json'),
    'customers',
    if_exists='replace'
)

print(f"Carregados: {result.rows_inserted} registros")
```

### Exemplo 2: Inferir schema automaticamente

```python
from app.application import JSONMySQLApplication

app = JSONMySQLApplication()

# Infer
ddl = app.infer_schema(Path('data/pedidos.json'))
print(ddl)

# Criar tabela
app.create_table('pedidos', ddl)

# Carregar dados
app.load_json(Path('data/pedidos.json'), 'pedidos')
```

### Exemplo 3: Validar dados antes de carregar

```python
from app.utils import JSONParser, SchemaInferencer
from app.validators import DataValidator
import pandas as pd

# Parse
data = JSONParser.parse_file('data/arquivo.json')
df = pd.DataFrame(data)

# Validar
valid, errors = DataValidator.validate_no_nulls(
    df, required_columns=['id', 'email']
)

if valid:
    app.load_json(...)
else:
    print(f"Erros: {errors}")
```

### Exemplo 4: Normalizar JSON aninhado

```python
from app.utils import normalize_nested

data = JSONParser.parse_file('data/pedidos.json')

normalized = normalize_nested(data, {
    'itens': 'order_items',
    'categorias': 'item_categories',
})

# Agora temos:
# normalized['main'] - tabela principal
# normalized['order_items'] - itens do pedido
# normalized['item_categories'] - categorias
```

---

## 🔧 Extensibilidade

### Criar um novo Loader

```python
from app.loaders import BaseLoader, LoadResult
from datetime import datetime

class CustomLoader(BaseLoader):
    """Loader customizado."""
    
    def load(self, file_path, table_name, **kwargs) -> LoadResult:
        """Implementa sua lógica."""
        start = datetime.now()
        
        try:
            # Sua implementação aqui
            rows = self._custom_load(file_path, table_name)
            
            return LoadResult(
                success=True,
                table=table_name,
                rows_inserted=rows,
                rows_failed=0,
                execution_time=(datetime.now() - start).total_seconds(),
                errors=[],
                started_at=start,
                finished_at=datetime.now(),
            )
        except Exception as e:
            return LoadResult(
                success=False,
                table=table_name,
                rows_inserted=0,
                rows_failed=0,
                execution_time=(datetime.now() - start).total_seconds(),
                errors=[str(e)],
                started_at=start,
                finished_at=datetime.now(),
            )
    
    def _custom_load(self, file_path, table_name):
        # Implementação customizada
        pass
```

### Criar um novo Validator

```python
from app.validators import DataValidator

class CustomValidator:
    @staticmethod
    def validate_custom_rule(df, rule_param):
        """Implementa validação customizada."""
        errors = []
        
        # Sua lógica
        if not rule_matches(df, rule_param):
            errors.append(f"Regra falhou: {rule_param}")
        
        return len(errors) == 0, errors
```

---

## 📊 Performance

| Modo | Velocidade | Quando Usar |
|------|-----------|------------|
| **Quick** | 940 linhas/seg | Desenvolvimento, arquivos pequenos |
| **Load** | 3.900 linhas/seg | Produção, arquivos grandes |
| **Upsert** | 800 linhas/seg | Atualizar registros existentes |

---

## 🧪 Testes

```bash
# Todos os testes
make test

# Com cobertura
make test-coverage

# Específico
pytest tests/test_loaders.py -v
```

---

## 📞 Suporte

- 📖 Documentação: [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)
- 🏗️ Arquitetura: Este arquivo
- 🐛 Issues: GitHub Issues
- 💡 Discussões: GitHub Discussions

---

**Status:** ✅ Pronto para Produção  
**Mantido por:** Pedro Mendes  
**Licença:** MIT  

---

*Construído seguindo princípios de clean code, SOLID e 12-factor app.*
