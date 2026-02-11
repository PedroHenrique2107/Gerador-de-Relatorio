# 🗺️ MAPA DE NAVEGAÇÃO - Como Usar a Nova Arquitetura

## 📌 Você está aqui: Nova Estrutura Profissional

Bem-vindo à versão 2.0 refatorada! Aqui está como navegar tudo.

---

## 🎯 PRIMEIRO ACESSO - O que ler?

### 1️⃣ Entender o Big Picture (10 min)
   **Arquivo:** [ARQUITETURA_SUMMARY.txt](ARQUITETURA_SUMMARY.txt)
   - Visual rápido do que foi feito
   - Mudanças principais
   - Checklist de implementação

### 2️⃣ Começar a Usar (15 min)
   **Arquivo:** [DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md)
   - Instalação e configuração
   - Primeiros 5 exemplos
   - Troubleshooting rápido

### 3️⃣ Entender a Arquitetura (30 min)
   **Arquivo:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
   - Padrões de design
   - Componentes principais
   - Como estender

---

## 🔍 BUSCAR COISA ESPECÍFICA?

### Quero carregar um arquivo JSON
```
Opção 1: CLI (recomendado para batch)
  python scripts/main.py --file data/seu_arquivo.json --table tabela

Opção 2: Python (recomendado para integração)
  from app.application import JSONMySQLApplication
  app = JSONMySQLApplication()
  result = app.load_json(Path('data/arquivo.json'), 'tabela')

Docs: [DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md#como-usar)
```

### Quero validar meus dados antes de carregar
```
from app.validators import DataValidator
valid, errors = DataValidator.validate_no_nulls(df, ['id', 'email'])

Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#2-domain-layer)
```

### Quero normalizar JSON aninhado
```
from app.utils import normalize_nested
normalized = normalize_nested(data, {'items': 'orders'})

Docs: [docs/EXAMPLES.md](docs/EXAMPLES.md)
```

### Quero inferir schema automaticamente
```
from app.utils import SchemaInferencer
ddl = SchemaInferencer.generate_create_table('tabela', df)

Docs: [docs/API.md](docs/API.md#schemainferencer)
```

### Quero usar logging estruturado
```
from app.core import get_logger
logger = get_logger(__name__)
logger.info("Minha mensagem")

Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#logger-estruturado)
```

### Quero gerenciar conexões do banco
```
from app.core import DatabaseManager
DatabaseManager.initialize('mysql+pymysql://...')
engine = DatabaseManager.get_engine()

Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#databasemanager-singleton)
```

### Quero criar um novo Loader
```
from app.loaders import BaseLoader, LoadResult

class MeuLoader(BaseLoader):
    def load(self, file_path, table_name, **kwargs) -> LoadResult:
        # Sua implementação
        pass

Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#criar-um-novo-loader)
```

### Quero fazer deploy em produção
```
Leia: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
```

### Quero rodar os testes
```
make test              # Todos os testes
make test-coverage     # Com cobertura
pytest tests/ -v       # Verbose

Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#-testes)
```

### Quero entender os padrões de design usados
```
Leia: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#-padrões-de-design)

Padrões implementados:
- Singleton (DatabaseManager)
- Factory (JSONParser)
- Strategy (Loaders)
- Repository (DatabaseManager)
- Decorator (setup_logger)
```

### Quero contribuir com código
```
Leia: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
```

---

## 📂 ESTRUTURA RÁPIDA

```
app/
├── core/           → Logger, Database, Exceptions
├── loaders/        → Estratégias de carregamento (Quick, Load, Upsert)
├── validators/     → Validação de dados
├── normalizers/    → Normalização JSON
├── utils/          → JSON Parser, Schema Manager
└── application.py  → Classe orquestradora (USE ESTA!)

config/
└── settings.py     → Configuração centralizada

scripts/
└── main.py         → CLI principal

docs/
├── ARCHITECTURE.md  → Padrões e design
├── API.md           → Referência de API
├── EXAMPLES.md      → Exemplos práticos
├── DEPLOYMENT.md    → Deploy
└── CONTRIBUTING.md  → Contribuição
```

---

## 🚀 QUICK START

### CLI (Linha de Comando)
```bash
python scripts/main.py --file data/seu_arquivo.json --table tabela
```

### Python
```python
from app.application import JSONMySQLApplication
app = JSONMySQLApplication()
result = app.load_json(Path('data/arquivo.json'), 'tabela')
print(result)
```

### Docker
```bash
docker-compose up -d
```

---

## 📚 DOCUMENTAÇÃO POR NÍVEL

### Iniciante
1. [DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md) - Comece aqui
2. [README_V2.md](README_V2.md) - Overview
3. [docs/EXAMPLES.md](docs/EXAMPLES.md) - Exemplos

### Intermediário
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura
2. [docs/API.md](docs/API.md) - API reference
3. Código fonte (`app/application.py`)

### Avançado
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#-extensibilidade) - Estender
2. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Produção
3. Código fonte (todo o `app/`)

---

## 🎯 COMUM: COMO FAZER?

### Como carregar múltiplos arquivos?
```python
results = app.load_multiple([Path('f1.json'), Path('f2.json')])
```
[Mais detalhes](DOCUMENTACAO_COMPLETA_V2.md#exemplo-5-iterar-em-chunks-economiza-memória)

### Como validar integridade referencial?
```python
from app.validators import ReferentialValidator
valid, errors = ReferentialValidator.validate_foreign_key(
    child_df, 'customer_id', parent_df, 'id'
)
```
[Mais detalhes](docs/API.md#validators)

### Como usar diferentes modos de carregamento?
```bash
python scripts/main.py --file data/arquivo.json --table tab --mode load
```
[Mais detalhes](DOCUMENTACAO_COMPLETA_V2.md#-performance)

### Como iterar em chunks para economizar memória?
```python
for chunk in JSONParser.iterate_file('arquivo.json', chunk_size=5000):
    process(chunk)
```
[Mais detalhes](DOCUMENTACAO_COMPLETA_V2.md#exemplo-5-iterar-em-chunks-economiza-memória)

### Como normalizar JSON aninhado?
```python
normalized = normalize_nested(data, {'items': 'orders'})
```
[Mais detalhes](DOCUMENTACAO_COMPLETA_V2.md#exemplo-4-normalizar-json-aninhado)

---

## 🆘 PRECISA DE AJUDA?

### Erro ao conectar no banco
→ [Troubleshooting](DOCUMENTACAO_COMPLETA_V2.md#-troubleshooting)

### Como debugar?
→ Adicione `--debug` ao CLI ou `app_config.debug = True` no Python

### Documentação não responde sua dúvida?
→ Veja [docs/EXAMPLES.md](docs/EXAMPLES.md) para mais exemplos

### Quer contribuir?
→ Leia [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 📊 PERFORMANCE E ESCALABILIDADE

| Métrica | Valor | Docs |
|---------|-------|------|
| Modo Quick | 940 linhas/seg | [Perf](DOCUMENTACAO_COMPLETA_V2.md#-performance) |
| Modo Load | 3.900 linhas/seg | [Perf](DOCUMENTACAO_COMPLETA_V2.md#-performance) |
| Pool de conexões | 10 padrão | [Config](config/settings.py) |
| Chunk padrão | 5.000 | [Config](config/settings.py) |

---

## ✨ ESTATÍSTICAS DO PROJETO

- **Linhas de código**: ~2.000+
- **Arquivos Python**: 20+
- **Classes principais**: 10+
- **Padrões implementados**: 5+
- **Documentação**: 5 arquivos
- **Testes**: Estrutura pronta
- **Performance**: Até 3.900 linhas/seg

---

## 🏆 QUALIDADE

✅ Type hints completos  
✅ Docstrings em português  
✅ Padrões SOLID  
✅ Clean Code  
✅ 12-factor app  
✅ Logging estruturado  
✅ Tratamento de erros robusto  
✅ Gerenciamento de recursos  

---

## 🔗 LINKS RÁPIDOS

- 📖 [Documentação Completa](DOCUMENTACAO_COMPLETA_V2.md)
- 🏗️ [Arquitetura Detalhada](docs/ARCHITECTURE.md)
- 💡 [Exemplos Práticos](docs/EXAMPLES.md)
- 📚 [API Reference](docs/API.md)
- 🚀 [Deploy em Produção](docs/DEPLOYMENT.md)
- 🤝 [Como Contribuir](docs/CONTRIBUTING.md)
- 🗺️ [Este Mapa](MAPA_NAVEGACAO.md)

---

**Status:** ✅ Pronto para Usar e Produção  
**Data:** 28 de janeiro de 2026  
**Versão:** 2.0.0

Bem-vindo ao mundo da arquitetura profissional! 🚀
