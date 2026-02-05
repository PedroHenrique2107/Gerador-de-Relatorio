#!/bin/bash

echo "=========================================="
echo "  Sistema de Relatórios Sienge"
echo "=========================================="
echo ""

# Verificar se MySQL está configurado
if ! grep -q "MYSQL_HOST=.*[^ ]" /app/api-server/.env 2>/dev/null; then
    echo "⚠️  ATENÇÃO: Configure o MySQL antes de continuar!"
    echo ""
    echo "Edite o arquivo: /app/api-server/.env"
    echo "Preencha: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE"
    echo ""
    echo "Pressione ENTER para continuar mesmo assim..."
    read
fi

echo "1. Verificando dependências..."
echo ""

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Verificar Yarn
if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn não encontrado"
    exit 1
fi
echo "✅ Yarn $(yarn --version)"

echo ""
echo "2. Criando pastas necessárias..."
mkdir -p /app/api-server/downloads
mkdir -p /app/api-server/logs
mkdir -p /app/api-server/data
mkdir -p /app/backend/data
echo "✅ Pastas criadas"

echo ""
echo "3. Iniciando API Server..."
cd /app/api-server
node server.js > logs/api.log 2>&1 &
API_PID=$!
echo "✅ API Server iniciado (PID: $API_PID)"
echo "   Logs em: /app/api-server/logs/api.log"

# Aguardar API iniciar
sleep 3

# Verificar se API está rodando
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo "✅ API Server respondendo em http://localhost:3001"
else
    echo "⚠️  API Server pode não estar respondendo"
fi

echo ""
echo "4. Iniciando Frontend..."
cd /app/frontend
yarn start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "  Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📊 Frontend:    http://localhost:3000"
echo "🔧 API Server:  http://localhost:3001"
echo ""
echo "Logs:"
echo "  API:      tail -f /app/api-server/logs/api.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Para parar os serviços:"
echo "  kill $API_PID $FRONTEND_PID"
echo ""
echo "Pressione CTRL+C para sair (serviços continuarão rodando)"
echo ""

# Manter script rodando
tail -f /app/api-server/logs/api.log
