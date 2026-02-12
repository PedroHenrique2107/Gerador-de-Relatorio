# ðŸ“Š NormalizaÃ§Ã£o do ExtratoClienteHistÃ³rico

## O Problema

O JSON original `ExtratoClienteHistorico.json` tem uma estrutura **aninhada/hierÃ¡rquica**:

```
1 documento
  â””â”€â”€ 10 parcelas (array colapsado no DBForge)
      â””â”€â”€ N pagamentos (array colapsado no DBForge)
```

Quando importado no DBForge, os arrays ficam "colapsados" - vocÃª nÃ£o consegue ver cada parcela como uma linha separada, dificultando anÃ¡lises e relatÃ³rios.

## A SoluÃ§Ã£o

O script `scripts/normalize_extrato.py` **desnormaliza** o JSON em **3 tabelas relacionadas**:

### 1. **billsReceivables** (Contas a Receber)
Cada documento/empresa como uma linha:
```
billReceivableId | companyId | companyName | customerId | customerName | emissionDate
2                | 3         | SC1 FUNDO...| 889        | JHONY...     | 2024-08-10
3                | 3         | SC1 FUNDO...| 890        | EZEQUIEL...  | 2024-08-09
```

### 2. **installments** (Parcelas - CADA UMA COMO LINHA!)
Cada parcela como uma linha separada:
```
billReceivableId | installmentId | installmentNumber | dueDate     | originalValue
2                | 1             | 1/10              | 2024-08-13  | 3000.0
2                | 2             | 2/10              | 2024-09-13  | 3000.0
2                | 3             | 3/10              | 2024-10-13  | 3000.0
```

### 3. **receipts** (Pagamentos - CADA UM COMO LINHA!)
Cada pagamento como uma linha separada:
```
receiptId | billReceivableId | installmentId | date       | value
1         | 2                | 1             | 2024-08-10 | 3000.0
2         | 2                | 2             | 2024-08-30 | 3000.0
3         | 2                | 3             | 2024-09-23 | 3000.0
```

## Como Usar

### 1ï¸âƒ£ Teste Primeiro (Sem MySQL)

```bash
# Ativa a venv
.venv\Scripts\activate

# Testa a normalizaÃ§Ã£o sem inserir no MySQL
python test_normalize.py
```

**SaÃ­da esperada:**
```
âœ“ NORMALIZAÃ‡ÃƒO CONCLUÃDA COM SUCESSO!

ðŸ“Š RESULTADO:
  â€¢ billsReceivables: 7,039 documentos
  â€¢ installments:     18,885 parcelas
  â€¢ receipts:         18,900 pagamentos
```

### 2ï¸âƒ£ Execute com MySQL

```bash
.venv\Scripts\activate
python scripts/normalize_extrato.py
```

**SaÃ­da esperada:**
```
======================================================================
NORMALIZANDO ExtratoClienteHistorico.json
======================================================================

âœ“ Carregado: 7039 registros
âœ“ NormalizaÃ§Ã£o completa:
  â€¢ billsReceivables: 7039 registros
  â€¢ installments: 18885 registros
  â€¢ receipts: 18900 registros

======================================================================
âœ… NORMALIZAÃ‡ÃƒO CONCLUÃDA COM SUCESSO!
======================================================================

ðŸ“Š RESULTADO:
  â€¢ billsReceivables: 7,039 documentos
  â€¢ installments:     18,885 parcelas (VISÃVEIS NO DBFORGE)
  â€¢ receipts:         18,900 pagamentos

ðŸ”— RELACIONAMENTOS:
  â€¢ installments â†’ billsReceivables (billReceivableId)
  â€¢ receipts â†’ billsReceivables (billReceivableId)

ðŸ’¡ NO DBFORGE, AGORA VOCÃŠ VÃŠ:
  âœ“ Cada parcela como UMA LINHA separada (nÃ£o mais colapsada)
  âœ“ Cada pagamento como UMA LINHA separada
  âœ“ Todos os 7,039 clientes com dados desnormalizados
```

## Resultado no DBForge

### Antes (Aninhado)
```
billReceivableId | companyName | installments (COLAPSADO)
2                | SC1 FUNDO...| [{"installmentNumber":"1/10"...}, {"installmentNumber":"2/10"...}, ...]
```

### Depois (Normalizado - VISÃVEL)
```
installments view (expandida):
billReceivableId | installmentNumber | dueDate    | originalValue
2                | 1/10              | 2024-08-13 | 3000.0
2                | 2/10              | 2024-09-13 | 3000.0
2                | 3/10              | 2024-10-13 | 3000.0
...
```

## EstatÃ­sticas do Dataset

| MÃ©trica | Quantidade |
|---------|-----------|
| Documentos (billsReceivables) | 7.039 |
| Parcelas (installments) | 18.885 |
| Pagamentos (receipts) | 18.900 |
| MÃ©dia de parcelas por documento | 2,7 |

## Campos DisponÃ­veis

### billsReceivables
- `billReceivableId`: ID Ãºnico do documento
- `companyId`, `companyName`: Fundo de investimento
- `costCenterId`, `costCenterName`: Centro de custo
- `customerId`, `customerName`, `customerDocument`: Dados do cliente
- `emissionDate`: Data de emissÃ£o
- `document`: NÃºmero do documento
- `privateArea`: Ãrea privada
- `oldestInstallmentDate`: Data da parcela mais antiga
- `revokedBillReceivableDate`: Data de revogaÃ§Ã£o (se houver)

### installments
- `billReceivableId`: FK para billsReceivables
- `installmentId`: ID Ãºnico da parcela
- `installmentNumber`: NÃºmero da parcela (ex: "1/10", "2/10")
- `baseDate`: Data base para cÃ¡lculo
- `dueDate`: Data de vencimento
- `originalValue`: Valor original
- `currentBalance`: Saldo atual
- `currentBalanceWithAddition`: Saldo com adiÃ§Ãµes
- `installmentSituation`: SituaÃ§Ã£o da parcela
- `generatedBillet`: Se gerou boleto

### receipts
- `receiptId`: ID Ãºnico do pagamento
- `billReceivableId`: FK para billsReceivables
- `installmentId`: FK para installments
- `date`: Data do pagamento
- `value`: Valor pago
- `discount`: Desconto concedido
- `extra`: Juros/multa
- `netReceipt`: Valor lÃ­quido recebido
- `type`: Tipo de recebimento

## Consultas Ãšteis

### Parcelas pendentes de pagamento
```sql
SELECT 
  b.customerName,
  i.installmentNumber,
  i.dueDate,
  i.currentBalance
FROM installments i
JOIN billsReceivables b ON i.billReceivableId = b.billReceivableId
WHERE i.currentBalance > 0
ORDER BY i.dueDate ASC
LIMIT 10;
```

### Pagamentos por cliente
```sql
SELECT 
  b.customerName,
  COUNT(r.receiptId) AS totalPagamentos,
  SUM(r.value) AS valorTotal,
  MAX(r.date) AS ultimoPagamento
FROM receipts r
JOIN billsReceivables b ON r.billReceivableId = b.billReceivableId
GROUP BY b.billReceivableId, b.customerName
ORDER BY valorTotal DESC
LIMIT 10;
```

### Parcelas atrasadas
```sql
SELECT 
  b.customerName,
  i.installmentNumber,
  i.dueDate,
  i.originalValue,
  i.currentBalance
FROM installments i
JOIN billsReceivables b ON i.billReceivableId = b.billReceivableId
WHERE i.currentBalance > 0 
  AND i.dueDate < CURDATE()
ORDER BY i.dueDate ASC;
```

## Troubleshooting

### Erro: "Arquivo nÃ£o encontrado: data/ExtratoClienteHistorico.json"
- Verifique se o arquivo estÃ¡ em `./data/`
- O caminho Ã© relativo ao diretÃ³rio do projeto

### Erro: "Falha ao conectar no banco de dados"
- Verifique o arquivo `.env` com as credenciais do MySQL
- Teste a conexÃ£o: `python scripts/main.py --help`

### Erro: "ModuleNotFoundError: No module named 'app'"
- Verifique se a venv estÃ¡ ativada: `source .venv/bin/activate`
- Execute do diretÃ³rio raiz do projeto

## PrÃ³ximas Etapas

1. âœ… Testar normalizaÃ§Ã£o (test_normalize.py)
2. âœ… Carregar em MySQL (scripts/normalize_extrato.py)
3. ðŸ”„ Criar Ã­ndices para performance
4. ðŸ”„ Visualizar em DBForge (agora com dados normalizados)
5. ðŸ”„ Criar reports e dashboards

---

**Criado em:** 28/01/2026  
**Ãšltima atualizaÃ§Ã£o:** 28/01/2026  
**Status:** âœ… ProduÃ§Ã£o
