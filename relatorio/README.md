# Relatório - Geração de Arquivos

## Função
Gera arquivos de relatório (CSV, XLS, TXT) a partir de `RELATORIO_CONSOLIDADO`.

## Setup
```bash
pip install -r requirements.txt
```

## Uso
```bash
python generate_report.py --formato csv --output-dir /caminho/downloads
```

## Formatos Suportados

### CSV
- Delimitador: ponto-e-vírgula (;)
- Encoding: UTF-8 com BOM
- Tamanho médio: ~2MB para 19k registros

### XLS
- Formato: XLSX (Excel)
- Modo: write-only (otimizado)
- Tamanho médio: ~3MB para 19k registros

### TXT
- Formato: Tabular com colunas alinhadas
- Largura máxima por coluna: 30 caracteres
- Tamanho médio: ~1.5MB para 19k registros

## Output
Script retorna JSON em stdout:
```json
{
  "fileName": "relatorio_20260205_143346_19234.csv",
  "fileSize": "2.3 MB",
  "recordCount": 19234,
  "formato": "csv"
}
```
