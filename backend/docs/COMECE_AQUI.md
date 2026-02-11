# 🚀 INÍCIO RÁPIDO - 5 MINUTOS

## ⚡ TL;DR - Comece AGORA

```powershell
# 1. Ativar Virtual Environment (OBRIGATÓRIO!)
.venv\Scripts\activate

# 2. Testar se tudo funciona
python PROVA_SIMPLES.py

# 3. Usar a aplicação
python scripts/main.py --file dados/arquivo.json --table tabela

# 4. Sair da venv
deactivate
```

---

## ✅ Checklist Rápido

- [ ] Git clonado/baixado?
- [ ] Pasta `json-mysql-bulk` aberta no terminal?
- [ ] `.venv` existe? (Se não, veja [GUIA_VENV.md](GUIA_VENV.md#configuração-inicial))
- [ ] Pronto! Execute os comandos acima.

---

## 📍 O que está pronto

✅ Virtual Environment (.venv) com todas as dependências  
✅ Código refatorado para arquitetura profissional  
✅ CLI funcionando (`scripts/main.py`)  
✅ Validação obrigatória de venv  
✅ 7 scripts de teste/demonstração  
✅ Documentação completa  

---

## 🎯 Usar a Aplicação

### Carregar um arquivo JSON

```bash
# Ativar venv primeiro
.venv\Scripts\activate

# Depois rodar
python scripts/main.py --file dados/seu_arquivo.json --table tabela
```

### Carregar múltiplos arquivos

```bash
python scripts/main.py --dir dados/ --pattern "*.json"
```

### Ver todas as opções

```bash
python scripts/main.py --help
```

---

## 📚 Próximas Leituras

1. **[GUIA_VENV.md](GUIA_VENV.md)** - Tudo sobre virtual environment (5 min)
2. **[MAPA_NAVEGACAO.md](MAPA_NAVEGACAO.md)** - Mapa da documentação (5 min)
3. **[DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md)** - Guia detalhado (30 min)
4. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura técnica (30 min)

---

## ⚠️ Erro Comum

```
❌ ModuleNotFoundError: No module named 'sqlalchemy'
```

**Solução:** Você esqueceu de ativar a venv!

```powershell
.venv\Scripts\activate  # Add this!
python scripts/main.py --file dados/arquivo.json
```

---

## 💬 Dúvidas?

- **Sobre venv?** → [GUIA_VENV.md](GUIA_VENV.md)
- **Como usar?** → [DOCUMENTACAO_COMPLETA_V2.md](DOCUMENTACAO_COMPLETA_V2.md)
- **Navegar docs?** → [MAPA_NAVEGACAO.md](MAPA_NAVEGACAO.md)
- **Arquitetura?** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Status:** ✅ Pronto para usar agora mesmo!
