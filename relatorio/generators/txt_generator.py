"""
Gerador TXT - Formato tabular com colunas alinhadas
"""


class TXTGenerator:
    """Gera arquivo TXT em formato tabular."""

    def generate(self, rows, filepath):
        if not rows:
            raise ValueError("Nenhum dado para exportar")

        headers = list(rows[0].keys())

        col_widths = {}
        for header in headers:
            max_len = len(str(header))
            for row in rows:
                val_len = len(str(row.get(header, "")))
                if val_len > max_len:
                    max_len = val_len
            col_widths[header] = min(max_len + 2, 30)

        with open(filepath, "w", encoding="utf-8") as f:
            header_line = "".join(h.ljust(col_widths[h]) for h in headers)
            f.write(header_line + "\n")
            f.write("=" * len(header_line) + "\n")

            for row in rows:
                line = "".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
                f.write(line + "\n")
