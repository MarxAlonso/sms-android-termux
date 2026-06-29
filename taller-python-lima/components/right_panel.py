"""Panel derecho — solo HTML estático para st.markdown."""


def render_empty_state() -> str:
    return (
        '<div class="empty-state">'
        '<div style="font-size:28px;margin-bottom:8px;color:var(--text3);">🔍</div>'
        '<div class="empty-title">Esperando tu consulta</div>'
        '<div class="empty-text">'
        'Escribe una pregunta en español<br/>y el LLM generará el SQL.'
        '</div></div>'
    )


def render_results_summary(df, execution_time: float = None) -> str:
    nrows, ncols = df.shape
    nnum = len(df.select_dtypes(include=["number"]).columns)

    parts = ['<div class="rp-section">📋 Resumen</div>']

    parts.append(
        '<div class="rp-card">'
        '<div class="rp-label">Filas obtenidas</div>'
        f'<div class="rp-value">{nrows:,}</div></div>'
    )

    parts.append('<div class="rp-mini">')
    parts.append(
        '<div class="rp-mini-card">'
        '<div class="rp-label">Columnas</div>'
        f'<div class="rp-value-sm">{ncols}</div></div>'
    )
    parts.append(
        '<div class="rp-mini-card">'
        '<div class="rp-label">Numéricas</div>'
        f'<div class="rp-value-sm">{nnum}</div></div>'
    )
    parts.append("</div>")

    if execution_time is not None:
        c = "var(--success)" if execution_time < 1000 else "var(--accent)"
        parts.append(
            '<div class="rp-card">'
            '<div class="rp-label">Tiempo ejecución</div>'
            f'<div class="rp-value-sm" style="color:{c};">{execution_time:,.0f} ms</div></div>'
        )

    return "\n".join(parts)


def render_preview(df) -> str:
    preview = df.head(5)
    cols = df.columns[:5].tolist()

    parts = ['<div class="rp-section">👁️ Vista previa</div>']
    parts.append('<div style="overflow-x:auto;"><table style="width:100%;font-family:var(--mono);font-size:0.7rem;border-collapse:collapse;">')

    parts.append("<tr>")
    for c in cols:
        parts.append(f'<th style="text-align:left;padding:3px 4px;border-bottom:1px solid var(--border);color:var(--text3);font-size:0.6rem;text-transform:uppercase;">{c}</th>')
    parts.append("</tr>")

    for _, row in preview.iterrows():
        parts.append("<tr>")
        for c in cols:
            val = str(row[c])[:18]
            parts.append(f'<td style="padding:2px 4px;border-bottom:1px solid var(--border-lt);color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:80px;">{val}</td>')
        parts.append("</tr>")

    parts.append("</table></div>")
    return "\n".join(parts)


def render_structure(df) -> str:
    parts = ['<div class="rp-section">📑 Estructura</div>']
    parts.append('<div style="overflow-x:auto;"><table style="width:100%;font-family:var(--mono);font-size:0.7rem;border-collapse:collapse;">')
    parts.append("<tr><th style='text-align:left;padding:3px 4px;border-bottom:1px solid var(--border);color:var(--text3);font-size:0.6rem;text-transform:uppercase;'>Columna</th><th style='text-align:left;padding:3px 4px;border-bottom:1px solid var(--border);color:var(--text3);font-size:0.6rem;text-transform:uppercase;'>Tipo</th></tr>")

    for col, dtype in zip(df.columns, df.dtypes):
        parts.append(f"<tr><td style='padding:2px 4px;border-bottom:1px solid var(--border-lt);color:var(--text2);'>{col}</td><td style='padding:2px 4px;border-bottom:1px solid var(--border-lt);color:var(--text3);'>{dtype}</td></tr>")

    parts.append("</table></div>")
    return "\n".join(parts)
