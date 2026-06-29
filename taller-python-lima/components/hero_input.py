"""Componente Hero: título, input de consulta, botón y chips de sugerencias."""

from components.icons import svg_icon
from components.constants import SUGERENCIAS


def render_hero(current_pregunta: str = "", ejecutando: bool = False) -> str:
    """Genera el HTML completo de la sección hero + input + chips."""
    parts = []

    # ── Hero ──
    parts.append(
        '<div class="hero-section">'
        '<div class="hero-title">Pregunta sobre tus datos</div>'
        '<div class="hero-subtitle">'
        'Escribe en español lo que quieras saber de tu bodega peruana'
        '</div>'
        '</div>'
    )

    # ── Query Input ──
    val_attr = f'value="{current_pregunta}"' if current_pregunta else ""
    parts.append(
        '<div class="query-area">'
        '<div class="query-input-wrap">'
        f'<textarea id="query-input" '
        f'placeholder="Ej: ¿Cuáles son los 5 productos más vendidos?" '
        f'maxlength="500" {val_attr}'
        f'oninput="updateCharCount()"></textarea>'
        '<span class="query-char-count" id="char-count">0/500</span>'
        '</div>'
        '<div class="query-submit-wrap">'
        f'<button class="query-submit-btn{" loading" if ejecutando else ""}" '
        f'id="query-submit-btn" '
        f'{"disabled" if ejecutando else ""} '
        f'onclick="submitQuery()">'
        f'{svg_icon("loader", 16) if ejecutando else svg_icon("zap", 16)}'
        f'<span>{"Generando SQL…" if ejecutando else "Consultar"}</span>'
        f'</button>'
        '</div>'
    )

    # ── Chips de sugerencias ──
    parts.append('<div class="chips-wrap">')
    parts.append(
        f'<button class="chip" onclick="fillQuery(\'{SUGERENCIAS[0]}\')">'
        f'{svg_icon("zap", 12)}{SUGERENCIAS[0]}'
        f'</button>'
    )
    for sug in SUGERENCIAS[1:]:
        parts.append(
            f'<button class="chip" onclick="fillQuery(\'{sug}\')">{sug}</button>'
        )
    parts.append("</div>")
    parts.append("</div>")  # query-area

    return "\n".join(parts)
