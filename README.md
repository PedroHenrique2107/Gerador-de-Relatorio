🚀 Sistema Inteligente de Geração de Relatórios SQL
<p align="center"> <img src="https://img.shields.io/badge/Node.js-API-green?style=for-the-badge&logo=node.js" /> <img src="https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge&logo=react" /> <img src="https://img.shields.io/badge/Python-Processing-yellow?style=for-the-badge&logo=python" /> <img src="https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql" /> <img src="https://img.shields.io/badge/Status-Production-success?style=for-the-badge" /> </p>
✨ Sobre o Projeto

Sistema completo para geração automatizada de relatórios consolidados a partir do MySQL, com:

⚡ Processamento assíncrono

📊 Consolidação SQL otimizada

📁 Exportação em múltiplos formatos

📜 Histórico de relatórios

🖥️ Interface web moderna

🏗️ Arquitetura do Sistema
Diagrama
flowchart LR
    A[Frontend - React] --> B[API Server - Node.js]
    B --> C[Python Scripts]
    C --> D[(MySQL Database)]


Ou de forma simplificada:

Frontend → API Server → Python → MySQL

🧩 Componentes
🟢 1. API Server (Node.js)

🔁 Orquestra execução dos scripts Python

📦 Gerencia Jobs assíncronos

📜 Mantém histórico

📂 Disponibiliza downloads

📍 Porta: 3001

🐍 2. Backend Python

📥 Processa arquivos JSON

🗄️ Insere dados no MySQL

⚙️ Trabalha em chunks (5.000 registros)

📁 /app/backend/

🧠 3. Query Engine

🧮 Executa query SQL consolidada

🏗️ Popula tabela RELATORIO_CONSOLIDADO

📁 /app/query/

📄 4. Gerador de Relatórios

Gera arquivos:

📊 CSV

📈 XLS/XLSX

📜 TXT

📁 /app/relatorio/

🎨 5. Frontend (React)

🎛️ Seleção de formato

📡 Acompanhamento em tempo real

📚 Histórico de relatórios

🌙 Suporte a tema moderno

📍 Porta: 3000

⚙️ Setup Completo
📌 Pré-requisitos

Node.js 14+

Python 3.x

MySQL 5.x+

Yarn

🔹 1. API Server
cd api-server
yarn install
cp .env.example .env
mkdir downloads
yarn start

🔹 2. Query (Python)
cd query
pip install -r requirements.txt

🔹 3. Relatório (Python)
cd relatorio
pip install -r requirements.txt

🔹 4. Frontend
cd frontend
yarn install
yarn start

🔹 5. Rodar tudo junto (modo dev)
npm run dev

🛠 Configuração MySQL

Edite:

/app/api-server/.env

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=usuario
MYSQL_PASSWORD=senha
MYSQL_DATABASE=database

🚀 Como Usar

Acesse → http://localhost:3000

Escolha formato (CSV, XLS ou TXT)

Clique em Gerar Relatório

Aguarde (~3-5 minutos)

Faça download 🎉

🔄 Fluxo de Processamento
🧾 1. Inserção de Dados (~2 min)

Lê JSONs

Processa em chunks

Insere no MySQL

🧮 2. Query Consolidada (~30s)

Consolida dados

Popula RELATORIO_CONSOLIDADO

📁 3. Geração de Arquivo (~15–45s)

Lê tabela consolidada

Gera arquivo

Salva em /downloads

✅ 4. Finalização

Atualiza histórico

Disponibiliza download

📊 Performance
Etapa	Tempo Médio
Inserção	~2 min
Query	~30s
CSV	~15s
XLS	~45s
TXT	~20s
⏱ Total: 3–5 minutos por relatório
🗂 Estrutura do Projeto
/app/
├── api-server/
│   ├── routes/
│   ├── controllers/
│   ├── services/
│   └── downloads/
├── backend/
├── query/
├── relatorio/
└── frontend/

🧱 Estrutura de Dados
🗄️ Tabelas

Tabelas auxiliares

RELATORIO_CONSOLIDADO ← tabela final

🛡 Segurança

❌ Nunca commitar .env

🔐 Usuário MySQL com privilégios mínimos

📏 Limitação de tamanho de arquivo

🔍 Validação de inputs

🩺 Troubleshooting
❌ Python não encontrado
which python3


Configure:

PYTHON_PATH=/caminho/python

❌ MySQL falhou
mysql -h HOST -u USER -p DATABASE

❌ Timeout
JOB_TIMEOUT_MINUTES=60

❌ Frontend não conecta
REACT_APP_BACKEND_URL=http://localhost:3001

🔧 Manutenção
Alterar Query

Editar:

/app/query/execute_query.py

Adicionar novo formato

Criar novo generator

Registrar em GENERATORS

Adicionar no frontend

📜 Logs

API → Console

Python → stderr

Histórico → /api-server/data/history.json

💎 Diferenciais do Projeto

✔ Arquitetura modular
✔ Processamento assíncrono
✔ Alta escalabilidade
✔ Separação clara de responsabilidades
✔ Fácil manutenção futura

👨‍💻 Autor

Desenvolvido por Pedro Henrique
💼 Sistema profissional de geração de relatórios empresariais
