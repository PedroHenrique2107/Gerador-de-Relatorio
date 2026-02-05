# API Server - Relatórios Sienge

## Descrição
API intermediária REST que orquestra a geração de relatórios financeiros do Sienge.

## Funcionalidades
- Recebe solicitações do frontend
- Executa scripts Python sequencialmente
- Gerencia jobs assíncronos
- Disponibiliza arquivos para download
- Mantém histórico de relatórios

## Setup

### 1. Instalar dependências
```bash
cd api-server
yarn install
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:
- Credenciais MySQL (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
- Caminho do Python (PYTHON_PATH)
- Caminhos dos scripts Python

### 3. Criar pasta de downloads
```bash
mkdir downloads
```

## Executar

### Desenvolvimento
```bash
yarn dev
```

### Produção
```bash
yarn start
```

Servidor rodará em: http://localhost:3001

## Endpoints

### POST /api/reports/generate
Gera um novo relatório.

**Request:**
```json
{
  "formato": "csv" | "xls" | "txt"
}
```

**Response:**
```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Relatório sendo gerado...",
  "createdAt": "2026-02-05T14:30:22.123Z"
}
```

### GET /api/reports/jobs/:jobId
Retorna status de um job.

**Response:**
```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing" | "completed" | "failed",
  "currentStep": {
    "number": 3,
    "total": 4,
    "description": "Processando query consolidada..."
  },
  "progress": {
    "percentage": 67.5,
    "recordsProcessed": 12800,
    "totalRecords": 19000
  },
  "timing": {
    "startTime": "2026-02-05T14:30:22.123Z",
    "endTime": null,
    "elapsedSeconds": 135
  },
  "result": {
    "downloadUrl": "/downloads/relatorio_20260205_143346_19234.csv",
    "fileName": "relatorio_20260205_143346_19234.csv",
    "fileSize": "2.3 MB",
    "recordCount": 19234
  },
  "error": null
}
```

### GET /api/reports/history
Retorna histórico dos últimos 10 relatórios.

### GET /downloads/:filename
Faz download de um arquivo gerado.

## Estrutura de Arquivos
```
api-server/
├── server.js              # Servidor Express principal
├── routes/
│   ├── reports.js         # Rotas de relatórios
│   └── downloads.js       # Rota de downloads
├── controllers/
│   └── reportController.js
├── services/
│   ├── jobManager.js     # Gerenciamento de jobs
│   ├── pythonRunner.js   # Executor de scripts Python
│   └── historyManager.js # Persistência de histórico
├── utils/
│   ├── logger.js         # Sistema de logs
│   └── formatters.js     # Formatação de dados
├── downloads/           # Arquivos gerados
├── logs/               # Logs da API
└── data/
    └── history.json     # Histórico persistido
```

## Troubleshooting

### Erro: "Python não encontrado"
- Configure `PYTHON_PATH` no `.env` com o caminho completo do Python
- Teste: `python3 --version`

### Erro: "Conexão MySQL falhou"
- Verifique credenciais em `.env`
- Teste conexão: `mysql -h HOST -u USER -p`

### Erro: "Timeout"
- Aumente `JOB_TIMEOUT_MINUTES` no `.env`
- Verifique logs em `logs/`

## Logs
Logs são salvos no console e podem ser redirecionados para arquivo:
```bash
node server.js > logs/api.log 2>&1
```

## Produção com PM2
```bash
npm install -g pm2
pm2 start server.js --name "api-relatorios"
pm2 logs api-relatorios
pm2 restart api-relatorios
```
