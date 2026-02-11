# 🔒 GUIA DE VIRTUAL ENVIRONMENT

## ⚠️ IMPORTANTE - LEIA PRIMEIRO!

Esta aplicação **OBRIGATORIAMENTE** deve ser executada dentro de uma **Virtual Environment (.venv)**.

**SEM a venv ativada, o código NÃO FUNCIONARÁ!**

---

## 🚀 Como Ativar a Virtual Environment

### Windows (PowerShell/CMD)

```powershell
# Método 1: Ativar direto (RECOMENDADO)
.venv\Scripts\activate

# Depois execute
python scripts/main.py --file dados/arquivo.json --table tabela

# Para sair da venv depois
deactivate
```

### Windows (Batch/CMD)

```batch
REM Ativar
.venv\Scripts\activate.bat

REM Depois execute
python scripts/main.py --file dados/arquivo.json --table tabela

REM Para sair
.venv\Scripts\deactivate.bat
```

### macOS / Linux

```bash
# Ativar
source .venv/bin/activate

# Depois execute
python scripts/main.py --file dados/arquivo.json --table tabela

# Para sair da venv depois
deactivate
```

---

## ⚡ Atalho Rápido (Automático)

Não quer ativar manualmente? Use os scripts de ativação automática:

### Windows
```powershell
.\activate-venv.bat scripts/main.py --file dados/arquivo.json
```

### macOS/Linux
```bash
./activate-venv.sh scripts/main.py --file dados/arquivo.json
```

---

## ✅ Como Verificar se está Ativado

Quando a venv está **ativada**, você verá algo assim no terminal:

```
(.venv) C:\Users\...> _
```

Ou no PowerShell:
```
(.venv) PS C:\Users\...> _
```

**Sem o `(.venv)` no início, a venv NÃO está ativada!**

---

## 📦 Verificar Dependências Instaladas

Quando dentro da venv, execute:

```bash
pip list
```

Você deve ver:
- ✅ pandas 3.0.0+
- ✅ SQLAlchemy 2.0.46+
- ✅ PyMySQL 1.1.2+
- ✅ python-dotenv 1.2.1+
- ✅ python-dateutil 2.9.0+
- ✅ pytest 9.0.2+
- ✅ ujson 5.11.0+

Se alguma faltar, instale com:

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuração Inicial (Primeira Vez)

1. **Ativar venv:**
   ```powershell
   .venv\Scripts\activate
   ```

2. **Instalar/Atualizar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Criar arquivo .env com credenciais MySQL:**
   ```bash
   echo DB_HOST=localhost > .env
   echo DB_PORT=3306 >> .env
   echo DB_USER=seu_usuario >> .env
   echo DB_PASSWORD=sua_senha >> .env
   echo DB_NAME=seu_database >> .env
   ```

4. **Testar a instalação:**
   ```bash
   python PROVA_SIMPLES.py
   ```

---

## ❌ O que NÃO fazer

```bash
# ❌ ERRADO - Sem ativar venv
python scripts/main.py --file dados/arquivo.json

# ❌ ERRADO - Usando Python do sistema
C:\Python310\python.exe scripts/main.py

# ❌ ERRADO - Terminal diferente sem reativar venv
# Se abrir um novo terminal, SEMPRE reative a venv!
```

---

## 🆘 Troubleshooting

### Erro: "No module named 'sqlalchemy'"

**Causa:** Venv não está ativada  
**Solução:**
```powershell
.venv\Scripts\activate
pip list  # Verifique se packages aparecem
```

### Erro: "ModuleNotFoundError: No module named 'app'"

**Causa:** Executando fora da pasta raiz do projeto  
**Solução:** Certifique-se que está na pasta raiz (`json-mysql-bulk`) ao executar

### A venv não ativa no PowerShell

**Cause:** Política de execução restritiva  
**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

### Comando 'deactivate' não funciona

**Causa:** Usando bash no Windows  
**Solução:** Use `deactivate.bat` ou `deactivate.ps1`

---

## 📋 Checklist Pré-Uso

Antes de usar a aplicação, verifique:

- [ ] Venv está ativada? `(.venv)` aparece no terminal?
- [ ] Dependências instaladas? `pip list` mostra tudo?
- [ ] Arquivo .env configurado?
- [ ] Banco de dados acessível? `python test_conexao.py`
- [ ] Prova passa? `python PROVA_SIMPLES.py`

---

## 🎯 Próximos Passos

Depois de ativar a venv:

1. Veja o [MAPA_NAVEGACAO.md](MAPA_NAVEGACAO.md) para começar
2. Leia [DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md)
3. Execute exemplos em [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## 💡 Pro Tips

### 1. Configurar VS Code para usar venv automaticamente

Edite `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe"
}
```

### 2. Criar alias para ativar rápido

**PowerShell** (adicione ao `$PROFILE`):
```powershell
function activate-app { & .\.venv\Scripts\Activate.ps1 }
```

Depois use: `activate-app`

### 3. Rodar múltiplos scripts mantendo venv ativa

```powershell
.venv\Scripts\activate
python PROVA_SIMPLES.py
python scripts/main.py --file dados/arquivo.json
deactivate
```

---

**Última atualização:** 28 de janeiro de 2026  
**Status:** ✅ Obrigatório - Sem venv, nada funciona!
