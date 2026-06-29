"""Explorador de esquema de base de datos — sidebar."""

from components.icons import svg_icon


def render_schema_tree(schema: dict, search: str = "", expanded: dict = None) -> str:
    """Genera HTML del árbol de esquema con búsqueda."""
    if expanded is None:
        expanded = {}

    parts = [
        '<div class="sidebar-section-title">',
        svg_icon("database", 14),
        "<span>Esquema de la BD</span>",
        "</div>",
    ]

    # Search bar
    search_icon = svg_icon("search", 14)
    parts.append(
        f'<div class="schema-search">'
        f'<div class="schema-search-wrap">'
        f'<span class="schema-search-icon">{search_icon}</span>'
        f'<input type="text" id="schema-search-input" placeholder="Buscar columna..." '
        f'value="{search}" oninput="filterSchema(this.value)"/>'
        f'</div></div>'
    )

    parts.append('<div id="schema-tree">')

    for tname, columns in schema.items():
        # Filter
        if search:
            filtered = [c for c in columns if search.lower() in c["name"].lower()]
            show_table = bool(filtered)
        else:
            filtered = columns
            show_table = True

        hide = "" if show_table else ' style="display:none"'
        parts.append(f'<div class="schema-table"{hide}>')

        # Table header button
        exp_key = f"schema_{tname}"
        is_expanded = expanded.get(exp_key, False)
        chev = svg_icon("chevron-down" if is_expanded else "chevron-right", 14)
        col_count = len(columns)

        parts.append(
            f'<button class="schema-table-btn" '
            f'onclick="toggleSchema(\'{exp_key}\')">'
            f'{chev}{tname}'
            f'<span class="schema-table-count">{col_count}</span>'
            f'</button>'
        )

        # Columns
        cols_style = "" if is_expanded else ' style="display:none"'
        parts.append(f'<div class="schema-columns" id="{exp_key}"{cols_style}>')

        for c in filtered:
            tag, tag_cls = _type_tag(c["type"])
            pk_mark = f'<span class="schema-col-pk">{svg_icon("key", 10)}</span>' if c.get("pk") else ""
            parts.append(
                f'<div class="schema-col" '
                f'onclick="insertColumn(\'{tname}.{c["name"]}\')" '
                f'title="Insertar {tname}.{c["name"]}">'
                f'<span class="schema-type-badge {tag_cls}">{tag}</span>'
                f'<span class="schema-col-name">{c["name"]}</span>'
                f'{pk_mark}'
                f'</div>'
            )

        parts.append("</div>")  # schema-columns
        parts.append("</div>")  # schema-table

    parts.append("</div>")  # schema-tree

    return "\n".join(parts)


def _type_tag(t: str) -> tuple:
    """Devuelve (etiqueta, clase_css) para un tipo de columna."""
    t = t.upper()
    if "INT" in t:
        return "INT", "type-int"
    if "TEXT" in t or "VARCHAR" in t or "CHAR" in t:
        return "TEXT", "type-text"
    if "REAL" in t or "FLOAT" in t or "DOUBLE" in t or "DECIMAL" in t or "NUMERIC" in t:
        return "REAL", "type-real"
    if "DATE" in t or "TIME" in t:
        return "DATE", "type-date"
    return t[:4], "type-int"
