"""Componente SQL Card — solo HTML estático, sin onclick."""

import re


def render_sql_card(sql: str, execution_time: float = None) -> str:
    """Genera HTML del SQL con syntax highlighting."""
    highlighted = _highlight_sql(sql)
    time_str = f"{execution_time:,.0f} ms" if execution_time is not None else ""

    time_html = f'<span class="sql-time">{time_str}</span>' if time_str else ""

    return (
        '<div class="sql-card">'
        '<div class="sql-header">'
        '<span class="sql-label">⚡ SQL generado</span>'
        f'{time_html}'
        '</div>'
        f'<div class="sql-code">{highlighted}</div>'
        '</div>'
    )


def _highlight_sql(sql: str) -> str:
    keywords = (
        r'\b(SELECT|FROM|WHERE|AND|OR|NOT|IN|LIKE|BETWEEN|IS|NULL|AS|ON|JOIN'
        r'|LEFT|RIGHT|INNER|OUTER|CROSS|FULL|GROUP|BY|HAVING|ORDER|ASC|DESC'
        r'|LIMIT|OFFSET|UNION|ALL|DISTINCT|CASE|WHEN|THEN|ELSE|END|EXISTS'
        r'|WITH|RECURSIVE|CAST|COALESCE|IFNULL)\b'
    )
    functions = (
        r'\b(COUNT|SUM|AVG|MIN|MAX|ROUND|UPPER|LOWER|LENGTH|SUBSTR|REPLACE'
        r'|TRIM|ABS|DATE|STRFTIME|JULIANDAY|GROUP_CONCAT|TYPEOF|INSTR|PRINTF)\b'
    )

    sql = sql.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    sql = re.sub(r"('(?:[^'\\]|\\.)*')", r'<span class="sql-string">\1</span>', sql)
    sql = re.sub(r'(\b\d+(?:\.\d+)?\b)', r'<span class="sql-number">\1</span>', sql)
    sql = re.sub(functions, r'<span class="sql-function">\1</span>', sql, flags=re.IGNORECASE)
    sql = re.sub(keywords, r'<span class="sql-keyword">\1</span>', sql, flags=re.IGNORECASE)
    sql = re.sub(r'(--.*)', r'<span class="sql-comment">\1</span>', sql)
    return sql
