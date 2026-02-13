"""
Gerador TXT - Formato tabular com colunas alinhadas
"""

import re


def _format_numero_documento(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if re.fullmatch(r"\d+(\.0+)?", s):
        s = str(int(float(s)))
    if s.isdigit():
        return s.zfill(4)
    return s


class TXTGenerator:
    """Gera arquivo TXT em formato tabular."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        headers = list(rows[0].keys())
        has_doc = "NumeroDoDocumento" in headers

        normalized_rows = []
        for row in rows:
            row_out = dict(row)
            if has_doc:
                row_out["NumeroDoDocumento"] = _format_numero_documento(
                    row_out.get("NumeroDoDocumento")
                )
            normalized_rows.append(row_out)

        col_widths = {}
        for header in headers:
            max_len = len(str(header))
            for row in normalized_rows:
                val_len = len(str(row.get(header, "")))
                if val_len > max_len:
                    max_len = val_len
            col_widths[header] = min(max_len + 2, 30)

        with open(filepath, "w", encoding="utf-8") as f:
            header_line = "".join(h.ljust(col_widths[h]) for h in headers)
            f.write(header_line + "\n")
            f.write("=" * len(header_line) + "\n")

            for row in normalized_rows:
                line = "".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
                f.write(line + "\n")
