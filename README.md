# Sistema de Geração de Relatórios Sienge

Sistema completo para geração automatizada de relatórios financeiros a partir de dados do Sienge.

## Arquitetura

```
Frontend (React) → API Server (Node.js) → Python Scripts
                                           ↓
                                       MySQL Database
```

## Componentes

### 1. API Server (Node.js)
- Servidor REST API intermediário
- Orquestra execução de scripts Python
- Gerencia jobs assíncronos
- Porta: 3001

### 2. Backend Python (Existente)
- Processa JSONs do Sienge
- Insere dados no MySQL
- Localização: `/app/backend/`

### 3. Query (Python)
- Executa query SQL consolidada
- Popula tabela RELATORIO_CONSOLIDADO
- Localização: `/app/query/`

### 4. Relatório (Python)
- Gera arquivos CSV, XLS, TXT
- Lê dados de RELATORIO_CONSOLIDADO
- Localização: `/app/relatorio/`

### 5. Frontend (React)
- Interface web minimalista
- Seleção de formato
- Acompanhamento de progresso
- Histórico de relatórios
- Porta: 3000

## Setup Completo

### Pré-requisitos
- Node.js 14+
- Python 3.14.2
- MySQL 5.x
- Yarn

### 1. API Server
```bash
cd api-server
yarn install
cp .env.example .env
# Configure credenciais MySQL no .env
mkdir downloads
yarn start
```

### 2. Query (Python)
```bash
cd query
pip install -r requirements.txt
```

### 3. Relatório (Python)
```bash
cd relatorio
pip install -r requirements.txt
```

### 4. Frontend
```bash
cd frontend
yarn install
yarn start
```

## Configuração MySQL

Edite `/app/api-server/.env`:
```bash
MYSQL_HOST=seu_servidor_mysql
MYSQL_PORT=3306
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=seu_database
```

## Uso

1. Acesse http://localhost:3000
2. Selecione formato (CSV, XLS ou TXT)
3. Clique em "Gerar Relatório Padrão"
4. Aguarde processamento (~3-5 minutos)
5. Faça download do arquivo

## Fluxo de Processamento

1. **Inserção de Dados** (~2 min)
   - Lê JSONs de `/app/backend/data/`
   - Processa em chunks de 5.000 registros
   - Insere em 4 tabelas MySQL

2. **Query Consolidada** (~30s)
   - Executa query SQL complexa
   - Consolida dados de 4 tabelas
   - Popula RELATORIO_CONSOLIDADO

3. **Geração de Arquivo** (~15-45s)
   - Lê RELATORIO_CONSOLIDADO
   - Gera arquivo no formato solicitado
   - Salva em `/app/api-server/downloads/`

4. **Finalização**
   - Atualiza histórico
   - Disponibiliza link de download

## Estrutura de Dados

### Tabelas MySQL
- `SI_EXTRATO_CLIENTE_HISTORICO` - Histórico de extratos
- `SI_DATACOMPETPARCELAS` - Parcelas por competência
- `SI_DATAPAGTO_receipts` - Recebimentos
- `SI_DATAPAGTO_receiptsCategories` - Categorias
- `RELATORIO_CONSOLIDADO` - Resultado da query

### Arquivos JSON
Localização: `/app/backend/data/`
- EXTRATO_CLIENTE_HISTORICO.json
- PARCELAS_CONTARECEBER_DATACOMPETPARCELAS.json
- PARCELAS_CONTARECEBER_DATAPAGTO.json

## Performance

- Inserção: ~2 minutos (5.000 registros/batch)
- Query: ~30 segundos
- CSV: ~15 segundos
- XLS: ~45 segundos
- TXT: ~20 segundos

**Total: 3-5 minutos por relatório**

## Troubleshooting

### Erro: "Python não encontrado"
```bash
which python3
# Configure PYTHON_PATH no api-server/.env
```

### Erro: "Conexão MySQL falhou"
```bash
# Teste conexão
mysql -h HOST -u USER -p DATABASE

# Verifique credenciais em api-server/.env
```

### Erro: "Timeout"
```bash
# Aumente timeout em api-server/.env
JOB_TIMEOUT_MINUTES=60
```

### Frontend não conecta no backend
```bash
# Verifique REACT_APP_BACKEND_URL em frontend/.env
REACT_APP_BACKEND_URL=http://localhost:3001
```

## Manutenção

### Alterar Query Padrão
Edite `/app/query/execute_query.py` → constante `QUERY_PADRAO`

### Adicionar Novo Formato
1. Crie `/app/relatorio/generators/novo_generator.py`
2. Adicione em `GENERATORS` em `generate_report.py`
3. Adicione opção no frontend `FormatSelector.js`

### Logs
- API Server: console output
- Python scripts: stderr
- Histórico: `/app/api-server/data/history.json`

## Estrutura do Projeto
```
/app/
├── api-server/          # Node.js API
│   ├── server.js
│   ├── routes/
│   ├── controllers/
│   ├── services/
│   ├── utils/
│   └── downloads/
├── backend/             # Python existente
│   ├── scripts/
│   └── data/
├── query/               # Python query
│   └── execute_query.py
├── relatorio/           # Python relatório
│   ├── generate_report.py
│   └── generators/
└── frontend/            # React
    ├── src/
    │   ├── components/
    │   ├── hooks/
    │   └── services/
    └── public/
```

## Segurança

- Não commitar arquivos `.env`
- Usar credenciais MySQL com privilégios mínimos
- Validar inputs no frontend e backend
- Limitar tamanho de arquivos de download

## Suporte

Para problemas ou dúvidas:
1. Verifique logs da API Server
2. Verifique logs dos scripts Python (stderr)
3. Consulte documentação específica de cada componente
