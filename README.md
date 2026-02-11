# 🚀 Sistema Inteligente de Geração de Relatórios SQL

<p align="center">

<img src="https://img.shields.io/badge/Node.js-API-green?style=for-the-badge&logo=node.js" />
<img src="https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge&logo=react" />
<img src="https://img.shields.io/badge/Python-Processing-yellow?style=for-the-badge&logo=python" />
<img src="https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql" />
<img src="https://img.shields.io/badge/Status-Production-success?style=for-the-badge" />

</p>

---

# 📌 Visão Geral

Sistema completo para:

✔ Processar arquivos JSON  
✔ Inserir dados no MySQL  
✔ Executar Query Consolidada  
✔ Gerar relatórios automáticos (CSV, XLS, TXT)  
✔ Disponibilizar download via interface web  

---

# 🏗️ Arquitetura do Sistema

Frontend (React)
↓
API Server (Node.js)
↓
Scripts Python
↓
MySQL Database


---

# 🧩 Componentes do Projeto

---

## 🟢 1️⃣ API Server (Node.js)

📍 Porta: **3001**

Responsável por:

- Servir API REST
- Orquestrar execução dos scripts Python
- Controlar jobs assíncronos
- Gerenciar histórico de relatórios
- Controlar timeout e logs

📂 Localização:
/app/api-server/

---

## 🐍 2️⃣ Backend Python

Responsável por:

- Processar JSONs
- Inserir dados no MySQL
- Trabalhar em batches (5.000 registros)

📂 Localização:
/app/backend/


---

## 🔎 3️⃣ Query Python

Responsável por:

- Executar query SQL consolidada
- Popular tabela `RELATORIO_CONSOLIDADO`

📂 Localização:
/app/query/


---

## 📄 4️⃣ Relatório Python

Responsável por:

- Gerar arquivos:
  - CSV
  - XLS / XLSX
  - TXT
- Ler dados da tabela `RELATORIO_CONSOLIDADO`

📂 Localização:
/app/relatorio/


---

## ⚛️ 5️⃣ Frontend (React)

📍 Porta: **3000**

Responsável por:

- Interface minimalista
- Seleção de formato
- Acompanhamento de progresso
- Histórico de relatórios
- Download de arquivos

📂 Localização:
/app/frontend/


---

# ⚙️ Setup Completo

---

## 🔧 Pré-requisitos

- Node.js 14+
- Python 3.x
- MySQL 5.x
- Yarn

---

# 🚀 ETAPA 1 — Configurar API Server

```bash
cd api-server
yarn install
cp .env.example .env
mkdir downloads
yarn start
```
Configure as credenciais MySQL no .env.

🐍 ETAPA 2 — Configurar Query Python
cd query
pip install -r requirements.txt

📄 ETAPA 3 — Configurar Relatório Python
cd relatorio
pip install -r requirements.txt

⚛️ ETAPA 4 — Configurar Frontend
cd frontend
yarn install
yarn start

🗄️ Configuração MySQL

Edite:

/app/api-server/.env

MYSQL_HOST=seu_servidor
MYSQL_PORT=3306
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=seu_database

▶️ Como Usar

Acesse:

http://localhost:3000


Selecione formato (CSV, XLS ou TXT)

Clique em Gerar Relatório

Aguarde processamento

Faça download

🔄 Fluxo de Processamento
1️⃣ Inserção de Dados (~2 min)

Lê JSONs de /backend/data

Processa em batches

Insere em tabelas MySQL

2️⃣ Query Consolidada (~30s)

Executa query complexa

Consolida dados

Popula RELATORIO_CONSOLIDADO

3️⃣ Geração de Arquivo (~15–45s)

Lê RELATORIO_CONSOLIDADO

Gera arquivo

Salva em /api-server/downloads

4️⃣ Finalização

Atualiza histórico

Libera link para download

📊 Performance Média
Etapa	Tempo
Inserção	~2 min
Query	~30s
CSV	~15s
XLS	~45s
TXT	~20s
Total	3–5 min
🗂️ Estrutura do Projeto
/app/
├── api-server/
├── backend/
├── query/
├── relatorio/
└── frontend/

🛠️ Manutenção
Alterar Query Padrão

Edite:

/app/query/execute_query.py

Adicionar Novo Formato

Criar novo generator em:

/relatorio/generators/


Registrar no generate_report.py

Adicionar opção no frontend

🔐 Segurança

Nunca commitar .env

Usar usuário MySQL com privilégios mínimos

Validar inputs

Controlar timeout

🧪 Troubleshooting
❌ Python não encontrado
which python3


Configure PYTHON_PATH no .env.

❌ MySQL não conecta
mysql -h HOST -u USER -p DATABASE


Verifique credenciais.

❌ Timeout
JOB_TIMEOUT_MINUTES=60

❌ Frontend não conecta
REACT_APP_BACKEND_URL=http://localhost:3001

📌 Resumo Final

✔ Sistema modular
✔ Separação clara de responsabilidades
✔ Escalável
✔ Fácil manutenção
✔ Arquitetura limpa

👨‍💻 Autor

Pedro Henrique Mendes
Projeto profissional de geração automatizada de relatórios SQL
