"""
Loader Rápido - Modo INSERT simples.

Ideal para datasets pequenos/médios. ~940 linhas/segundo.
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
import pandas as pd
import sqlalchemy as sa

from app.loaders.base import BaseLoader, LoadResult
from app.core import get_logger
from app.core.database import DatabaseManager
from app.utils.json_handler import JSONParser
from app.core.exceptions import LoaderError

logger = get_logger(__name__)


class QuickLoader(BaseLoader):
    """Loader usando pandas.to_sql() com método 'multi'."""

    @staticmethod
    def _infer_sql_type(series: pd.Series) -> str:
        if pd.api.types.is_integer_dtype(series):
            return "BIGINT"
        if pd.api.types.is_float_dtype(series):
            return "DOUBLE"
        if pd.api.types.is_bool_dtype(series):
            return "TINYINT(1)"
        if pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"
        return "TEXT"

    @staticmethod
    def _ensure_table_columns(engine, table_name: str, df: pd.DataFrame) -> None:
        inspector = sa.inspect(engine)
        if not inspector.has_table(table_name):
            return

        existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
        missing = [c for c in df.columns if c not in existing_cols]
        if not missing:
            return

        if not missing:
            return

        with engine.begin() as conn:
            for col in missing:
                col_type = QuickLoader._infer_sql_type(df[col])
                stmt = sa.text(
                    f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {col_type}"
                )
                conn.execute(stmt)

    @staticmethod
    def _split_nested(
        data: list,
        keep_dict_fields: Optional[set] = None,
        list_fields: Optional[Dict[str, str]] = None,
        flatten_dict_fields: Optional[set] = None,
        explode_fields: Optional[set] = None,
    ) -> Dict[str, list]:
        """
        Separa campos aninhados em tabelas filhas.

        - Campos em keep_dict_fields são serializados em JSON e permanecem na tabela principal.
        - Campos em list_fields são movidos para tabelas filhas.
        """
        keep_dict_fields = keep_dict_fields or set()
        list_fields = list_fields or {}
        flatten_dict_fields = flatten_dict_fields or set()
        explode_fields = explode_fields or set()

        def _sanitize_value(value):
            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False, default=str)
            return value

        def _sanitize_row(row: Dict[str, Any]) -> Dict[str, Any]:
            return {k: _sanitize_value(v) for k, v in row.items()}

        def _flatten_dict(prefix: str, value: Dict[str, Any]) -> Dict[str, Any]:
            return {f"{prefix}{k[0].upper() + k[1:]}": v for k, v in value.items()}

        main_rows = []
        child_rows = {table: [] for table in list_fields.values()}

        for row in data:
            if not isinstance(row, dict):
                # Se não for dict, serializa e mantém
                main_rows.append({"_value": json.dumps(row, ensure_ascii=False, default=str)})
                continue

            row_id = row.get("_row_id") or str(uuid4())
            main_row = dict(row)
            main_row["_row_id"] = row_id

            # Achata dicts em colunas na tabela principal (ex: company -> companyId)
            for field in list(flatten_dict_fields):
                if field in main_row and isinstance(main_row[field], dict):
                    main_row.update(_flatten_dict(field, main_row.pop(field)))

            # paymentTerm: explode em colunas (id e nome) na tabela principal
            payment_term = None
            if "paymentTerm" in main_row:
                payment_term = main_row.pop("paymentTerm")
            elif "paymentsTerm" in main_row:
                payment_term = main_row.pop("paymentsTerm")
            if isinstance(payment_term, dict):
                main_row["paymentTermId"] = payment_term.get("id")
                main_row["paymentTermName"] = (
                    payment_term.get("descrition")
                    or payment_term.get("description")
                    or payment_term.get("name")
                )
            # Se não for dict, descartamos para manter apenas paymentTermId/Name

            # Chaves de relacionamento para tabelas filhas
            link_keys = {}
            for key in (
                "companyId",
                "billId",
                "installmentId",
                "billReceivableId",
                "customerId",
            ):
                if key in main_row:
                    link_keys[key] = main_row.get(key)

            # Explode listas direto na tabela principal (sem tabelas filhas)
            exploded_rows = []
            for field in list(explode_fields):
                value = main_row.pop(field, None)
                if isinstance(value, list) and value:
                    for item in value:
                        row_copy = dict(main_row)
                        if isinstance(item, dict):
                            # Se houver receipts dentro do item, explode também
                            receipts_nested = None
                            if "receipts" in item and isinstance(item["receipts"], list):
                                receipts_nested = item.pop("receipts")

                            expanded = {}
                            for k, v in item.items():
                                if isinstance(v, dict):
                                    expanded.update(_flatten_dict(k, v))
                                else:
                                    expanded[k] = v

                            if receipts_nested:
                                for receipt in receipts_nested:
                                    row_nested = dict(row_copy)
                                    row_nested.update(expanded)
                                    if isinstance(receipt, dict):
                                        receipt_expanded = {}
                                        for rk, rv in receipt.items():
                                            if isinstance(rv, dict):
                                                receipt_expanded.update(_flatten_dict("receipt", {rk: rv}) )
                                            else:
                                                receipt_expanded[f"receipt{rk[0].upper()+rk[1:]}"] = rv
                                        row_nested.update(receipt_expanded)
                                    else:
                                        row_nested["receiptValue"] = _sanitize_value(receipt)
                                    exploded_rows.append(row_nested)
                                continue

                            row_copy.update(expanded)
                        else:
                            row_copy[field] = _sanitize_value(item)
                        exploded_rows.append(row_copy)

            if exploded_rows:
                for r in exploded_rows:
                    # Evita erros do to_sql: serializa quaisquer dict/list restantes
                    for key, value in list(r.items()):
                        if isinstance(value, (dict, list)):
                            r[key] = _sanitize_value(value)
                    main_rows.append(_sanitize_row(r))
                continue

            for field, child_table in list_fields.items():
                value = main_row.pop(field, None)
                if isinstance(value, list):
                    for item in value:
                        child_row = {"_parent_id": row_id, **link_keys}
                        if isinstance(item, dict):
                            # Achata dicts de 1 nível (ex: bankMovements)
                            expanded = {}
                            for k, v in item.items():
                                if isinstance(v, dict):
                                    expanded.update(_flatten_dict(k, v))
                                else:
                                    expanded[k] = v
                            child_row.update(_sanitize_row(expanded))
                        else:
                            child_row["_value"] = _sanitize_value(item)
                        child_rows[child_table].append(_sanitize_row(child_row))

            # Serializa dicts que devem ficar na tabela principal
            for field in keep_dict_fields:
                if field in main_row and isinstance(main_row[field], dict):
                    main_row[field] = _sanitize_value(main_row[field])

            # Evita erros do to_sql: serializa quaisquer dict/list restantes
            for key, value in list(main_row.items()):
                if isinstance(value, (dict, list)):
                    main_row[key] = _sanitize_value(value)

            main_rows.append(_sanitize_row(main_row))

        return {"main": main_rows, **child_rows}
    
    def load(
        self,
        file_path: Path,
        table_name: str,
        lines: bool = False,
        if_exists: str = 'append',
        chunk_size: Optional[int] = None,
        normalize: bool = False,
        **kwargs,
    ) -> LoadResult:
        """
        Carrega JSON com INSERT simples.
        
        Args:
            file_path: Caminho do arquivo
            table_name: Nome da tabela
            lines: Se True, trata como NDJSON
            if_exists: fail, replace ou append
            chunk_size: Tamanho do chunk (padrão: 5000)
            normalize: Normaliza JSON aninhado
            **kwargs: Argumentos adicionais
        
        Returns:
            LoadResult: Resultado do carregamento
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Iniciando QuickLoader para {file_path} → {table_name}")
            
            # Parse JSON
            data = JSONParser.parse_file(file_path, lines=lines)
            logger.info(f"✓ Parseado: {len(data)} registros")
            
            if not data:
                raise LoaderError("Arquivo está vazio")

            # Separa listas aninhadas em tabelas filhas e mantém paymentTerm na principal
            # Configura dinamicamente campos aninhados
            first_row = next((r for r in data if isinstance(r, dict)), {})

            list_fields = {}
            if "receipts" in first_row:
                list_fields["receipts"] = f"{table_name}_receipts"
            if "receiptsCategories" in first_row:
                list_fields["receiptsCategories"] = f"{table_name}_receiptsCategories"
            if "installments" in first_row:
                list_fields["installments"] = f"{table_name}_installments"
            if "units" in first_row:
                list_fields["units"] = f"{table_name}_units"

            flatten_dict_fields = set()
            for fld in ("company", "costCenter", "customer"):
                if fld in first_row:
                    flatten_dict_fields.add(fld)

            table_name_upper = table_name.upper()
            explode_fields = set()
            if "EXTRATO_CLIENTE" in table_name_upper:
                explode_fields.add("installments")
                explode_fields.add("receipts")
            if "DATACOMPETPARCELAS" in table_name_upper or "DATA_COMPETENCIA" in table_name_upper:
                explode_fields.add("receipts")
                explode_fields.add("receiptsCategories")

            split = self._split_nested(
                data,
                keep_dict_fields={"paymentTerm"},
                list_fields=list_fields,
                flatten_dict_fields=flatten_dict_fields,
                explode_fields=explode_fields,
            )

            # Converte para DataFrame (tabela principal)
            df = pd.DataFrame(split["main"])
            logger.info(f"✓ DataFrame principal: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Carrega com pandas
            engine = DatabaseManager.get_engine()
            chunk_size = chunk_size or 5000
            
            rows_inserted = 0
            rows_failed = 0
            
            try:
                # Garante colunas antes de inserir (preserva dados existentes)
                self._ensure_table_columns(engine, table_name, df)

                df.to_sql(
                    table_name,
                    con=engine,
                    if_exists=if_exists,
                    index=False,
                    method='multi',
                    chunksize=chunk_size,
                )
                rows_inserted = len(df)
                logger.info(f"✓ Inseridos: {rows_inserted} registros")

                # Insere tabelas filhas
                for child_table, rows in split.items():
                    if child_table == "main":
                        continue
                    if not rows:
                        continue
                    child_df = pd.DataFrame(rows)
                    self._ensure_table_columns(engine, child_table, child_df)
                    child_df.to_sql(
                        child_table,
                        con=engine,
                        if_exists=if_exists,
                        index=False,
                        method='multi',
                        chunksize=chunk_size,
                    )
                    logger.info(
                        f"✓ Inseridos: {len(child_df)} registros em {child_table}"
                    )
            
            except Exception as e:
                logger.error(f"✗ Erro na inserção: {e}")
                rows_failed = len(df)
                raise LoaderError(str(e))
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            result = LoadResult(
                success=True,
                table=table_name,
                rows_inserted=rows_inserted,
                rows_failed=rows_failed,
                execution_time=execution_time,
                errors=[],
                started_at=start_time,
                finished_at=end_time,
            )
            
            logger.info(f"✓ {result}")
            return result
        
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.error(f"✗ Erro no QuickLoader: {e}")
            
            return LoadResult(
                success=False,
                table=table_name,
                rows_inserted=0,
                rows_failed=0,
                execution_time=execution_time,
                errors=[str(e)],
                started_at=start_time,
                finished_at=end_time,
            )
