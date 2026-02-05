# 🚀 Início Rápido - Sistema de Relatórios Sienge

## ⚠️ IMPORTANTE - Configuração MySQL

Antes de iniciar, você precisa configurar as credenciais do MySQL:

1. Edite o arquivo `/app/api-server/.env`
2. Preencha as seguintes variáveis:

```bash
MYSQL_HOST=seu_servidor_mysql.com
MYSQL_PORT=3306
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=seu_database
```

## 🔧 Configuração Inicial (Uma vez apenas)

### 1. Instalar dependências do API Server
```bash
cd /app/api-server
yarn install
```

### 2. Instalar dependências Python
```bash
# Query
cd /app/query
pip install -r requirements.txt

# Relatório
cd /app/relatorio
pip install -r requirements.txt

# Backend Scripts
cd /app/backend/scripts
pip install -r requirements.txt
```

### 3. Criar pastas necessárias
```bash
mkdir -p /app/api-server/downloads
mkdir -p /app/api-server/logs
mkdir -p /app/api-server/data
```

## ▶️ Iniciar o Sistema

### Opção 1: Iniciar separadamente

**Terminal 1 - API Server (Node.js):**
```bash
cd /app/api-server
node server.js
```
Servidor rodando em: http://localhost:3001

**Terminal 2 - Frontend (React):**
```bash
cd /app/frontend
yarn start
```
Interface rodando em: http://localhost:3000

### Opção 2: Iniciar tudo em background
```bash
# API Server
cd /app/api-server && node server.js > logs/api.log 2>&1 &

# Frontend
cd /app/frontend && yarn start &
```

## 🎯 Usar o Sistema

1. Acesse http://localhost:3000 no navegador
2. Selecione o formato desejado:
   - **CSV** - Planilha com ponto-e-vírgula
   - **Excel** - Arquivo .xlsx
   - **TXT** - Texto formatado em colunas
3. Clique em "Gerar Relatório Padrão"
4. Aguarde o processamento (3-5 minutos)
5. Faça o download quando concluído

## 🔍 Verificar Status

### Verificar se API está rodando
```bash
curl http://localhost:3001/health
```

Resposta esperada:
```json
{"status":"ok","timestamp":"2026-02-05T..."}
```

### Verificar logs da API
```bash
tail -f /app/api-server/logs/api.log
```

### Testar geração de relatório (via API)
```bash
curl -X POST http://localhost:3001/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"formato":"csv"}'
```

## 📁 Estrutura de Pastas

```
/app/
├── api-server/          # API Node.js (porta 3001)
│   ├── downloads/      # Arquivos gerados aqui
│   ├── data/           # Histórico JSON
│   └── logs/           # Logs da API
├── backend/
│   ├── data/           # JSONs do Sienge aqui
│   └── scripts/        # Scripts Python existentes
├── query/              # Executa query SQL
├── relatorio/          # Gera arquivos CSV/XLS/TXT
└── frontend/           # Interface React (porta 3000)
```

## ❓ Troubleshooting

### Erro: "ECONNREFUSED 127.0.0.1:3001"
- API Server não está rodando
- Inicie: `cd /app/api-server && node server.js`

### Erro: "MySQL connection failed"
- Verifique credenciais em `/app/api-server/.env`
- Teste conexão: `mysql -h HOST -u USER -p DATABASE`

### Erro: "Python not found"
- Configure `PYTHON_PATH` em `/app/api-server/.env`
- Exemplo: `PYTHON_PATH=/usr/bin/python3`

### Frontend não carrega
- Verifique se está rodando: `curl http://localhost:3000`
- Reinicie: `cd /app/frontend && yarn start`

### Relatório não gera
- Verifique logs: `tail -f /app/api-server/logs/api.log`
- Verifique se JSONs existem em `/app/backend/data/`

## 🛠️ Arquivos de Configuração

### `/app/api-server/.env`
```bash
# Configure suas credenciais MySQL aqui
MYSQL_HOST=
MYSQL_PORT=3306
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
```

### `/app/frontend/.env`
```bash
# URL da API (não alterar)
REACT_APP_BACKEND_URL=http://localhost:3001
```

## 📊 Arquivos JSON Esperados

Coloque seus arquivos JSON na pasta `/app/backend/data/`:
- EXTRATO_CLIENTE_HISTORICO.json
- PARCELAS_CONTARECEBER_DATACOMPETPARCELAS.json
- PARCELAS_CONTARECEBER_DATAPAGTO.json

Formato esperado:
```json
{
  "data": [
    {
      "billReceivableId": 2,
      "company": { "id": 3, "name": "..." },
      "customer": { "id": 889, "name": "...", "document": "..." },
      "installments": [...]
    }
  ]
}
```

## 🎓 Próximos Passos

1. ✅ Configure MySQL em `/app/api-server/.env`
2. ✅ Coloque seus JSONs em `/app/backend/data/`
3. ✅ Inicie API Server: `cd /app/api-server && node server.js`
4. ✅ Inicie Frontend: `cd /app/frontend && yarn start`
5. ✅ Acesse http://localhost:3000 e gere seu primeiro relatório!

## 📚 Documentação Completa

- `/app/README.md` - Documentação geral do sistema
- `/app/api-server/README.md` - Documentação da API
- `/app/query/README.md` - Documentação do módulo Query
- `/app/relatorio/README.md` - Documentação do módulo Relatório
