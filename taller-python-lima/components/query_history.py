"""Componente de historial de consultas — sidebar."""

from datetime import datetime, timedelta

from components.icons import svg_icon


def render_history(history: list) -> str:
    """Genera HTML del historial de consultas."""
    parts = [
        '<div class="sidebar-section-title">',
        svg_icon("history", 14),
        "<span>Historial</span>",
        "</div>",
    ]

    if not history:
        parts.append('<div class="empty-state-small">Aún no hay consultas.</div>')
        return "\n".join(parts)

    parts.append('<div class="history-list">')
    for entry in reversed(history[-20:]):
        active = " active" if entry.get("active") else ""
        q = entry.get("pregunta", "")
        success = entry.get("success", False)
        rows = entry.get("rows", 0)
        ts = entry.get("timestamp", datetime.now())

        badge = (
            f'<span class="history-badge success">{svg_icon("check", 10)} {rows} filas</span>'
            if success
            else f'<span class="history-badge error">{svg_icon("x", 10)} error</span>'
        )
        q_trunc = q[:50] + "…" if len(q) > 50 else q

        parts.append(
            f'<div class="history-item{active}" onclick="loadHistory(\'{q}\')">'
            f'<div class="history-q">{q_trunc}</div>'
            f'<div class="history-meta">'
            f'<span class="history-time">{_time_ago(ts)}</span>'
            f'{badge}'
            f'</div>'
            f'</div>'
        )

    parts.append("</div>")
    return "\n".join(parts)


def render_saved_queries(saved: list) -> str:
    """Genera HTML de consultas guardadas."""
    parts = [
        '<div class="sidebar-section-title">',
        svg_icon("bookmark", 14),
        "<span>Guardadas</span>",
        "</div>",
    ]

    if not saved:
        parts.append(
            '<div class="empty-state-small">'
            f'{svg_icon("star", 12)} Guarda con Ctrl+S'
            '</div>'
        )
        return "\n".join(parts)

    parts.append('<div class="history-list">')
    for sq in saved:
        q = sq.get("pregunta", "")
        q_trunc = q[:45] + "…" if len(q) > 45 else q
        parts.append(
            f'<div class="history-item" onclick="loadHistory(\'{q}\')">'
            f'<div class="history-q">{q_trunc}</div>'
            f'<div class="history-meta">'
            f'<span class="history-badge badge-saved">{svg_icon("star", 10)} guardada</span>'
            f'</div>'
            f'</div>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def _time_ago(dt: datetime) -> str:
    diff = datetime.now() - dt
    if diff < timedelta(minutes=1):
        return "ahora"
    if diff < timedelta(hours=1):
        m = int(diff.total_seconds() / 60)
        return f"hace {m} min"
    if diff < timedelta(days=1):
        h = int(diff.total_seconds() / 3600)
        return f"hace {h}h"
    return dt.strftime("%d/%m/%Y")
