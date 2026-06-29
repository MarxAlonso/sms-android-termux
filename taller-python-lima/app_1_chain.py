"""
CAPA 1 — El LLM escribe el SQL (todavía SIN agente) 🟢

Correr:   streamlit run app_1_chain.py
"""

import os
import re
import sqlite3
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq

from components.styles import generate_css
from components.sql_display import render_sql_card
from components.right_panel import render_empty_state, render_results_summary, render_preview, render_structure
from components.results_tabs import render_table_tab, render_chart_tab, render_stats_tab

# ─── Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Text-to-SQL · Capa 1", page_icon="🟢", layout="wide")
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

DB = "file:data/bodega.db?mode=ro"
MODELO = "llama-3.3-70b-versatile"

PROMPT = """Eres un experto en SQL para SQLite. Esta es la estructura de la base de datos:

{schema}

Escribe UNA sola consulta SQL (solo SELECT) que responda la pregunta del usuario.
Devuelve ÚNICAMENTE el SQL, sin explicaciones ni ```.

Pregunta: {pregunta}
SQL:"""

SUGERENCIAS = [
    "¿Cuáles son los 5 productos más vendidos?",
    "¿Qué distrito de Lima compra más?",
    "Top 5 clientes por monto gastado",
    "Ventas totales por categoría",
    "¿Cuánto vendí en total este mes?",
    "Productos con stock < 30",
]

# ─── Session State ───────────────────────────────────────────────────────
for k, v in {
    "query_history": [], "saved_queries": [], "current_pregunta": "",
    "last_result": None, "last_sql": None, "last_error": None,
    "ejecutando": False, "active_tab": "Tabla", "execution_time": None,
    "theme": "light", "schema_expanded": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Cached ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(model=MODELO, temperature=0)


@st.cache_data
def get_schema() -> str:
    con = sqlite3.connect(DB, uri=True)
    rows = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    con.close()
    return "\n\n".join(r[0] for r in rows if r[0])


@st.cache_data
def get_schema_parsed():
    con = sqlite3.connect(DB, uri=True)
    tables = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    schema = {}
    for (tname,) in tables:
        cols = con.execute(f"PRAGMA table_info('{tname}')").fetchall()
        schema[tname] = [
            {"name": c[1], "type": c[2].upper(), "pk": bool(c[5])} for c in cols
        ]
    con.close()
    return schema


def limpiar_sql(t):
    return re.sub(r"```sql|```", "", t).strip()


def ejecutar_consulta(sql):
    t0 = time.time()
    try:
        con = sqlite3.connect(DB, uri=True)
        df = pd.read_sql_query(sql, con)
        con.close()
        return df, None, (time.time() - t0) * 1000
    except Exception as e:
        return None, str(e), (time.time() - t0) * 1000


# ═══════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(generate_css(st.session_state.theme), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Header
    st.markdown(
        '<div class="sidebar-header">'
        '<div class="sidebar-logo-box">⚡</div>'
        '<div><div class="sidebar-title">Text-to-SQL</div>'
        '<div class="sidebar-sub">Capa 1 · Chain directo</div></div></div>',
        unsafe_allow_html=True,
    )

    # ── Tema ──
    tema_label = "🌙 Modo Oscuro" if st.session_state.theme == "light" else "☀️ Modo Claro"
    if st.button(tema_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

    st.divider()

    # ── Esquema ──
    st.markdown('<div class="section-title">🗄️ Esquema de la BD</div>', unsafe_allow_html=True)
    schema = get_schema_parsed()
    search = st.text_input("Buscar columna", "", key="schema_search", label_visibility="collapsed",
                           placeholder="Buscar columna...")

    for tname, columns in schema.items():
        if search:
            filtered = [c for c in columns if search.lower() in c["name"].lower()]
        else:
            filtered = columns

        ek = f"sch_{tname}"
        if ek not in st.session_state.schema_expanded:
            st.session_state.schema_expanded[ek] = True

        expanded = st.checkbox(
            f"**{tname}** ({len(columns)})",
            value=st.session_state.schema_expanded[ek],
            key=ek,
        )
        st.session_state.schema_expanded[ek] = expanded

        if expanded and filtered:
            for c in filtered:
                tag = c["type"][:4]
                cls = "type-int"
                for k, c_cls in [("INT", "type-int"), ("TEXT", "type-text"), ("REAL", "type-real"), ("CHAR", "type-text"), ("VARC", "type-text"), ("DATE", "type-date"), ("FLOA", "type-real"), ("DECI", "type-real")]:
                    if k in c["type"].upper():
                        cls = c_cls
                        break
                pk = " 🔑" if c["pk"] else ""
                st.markdown(
                    f'<div class="schema-col">'
                    f'<span class="schema-type-badge {cls}">{tag}</span>'
                    f'<span>{c["name"]}{pk}</span></div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Historial ──
    st.markdown('<div class="section-title">📜 Historial</div>', unsafe_allow_html=True)
    if not st.session_state.query_history:
        st.caption("Aún no hay consultas.")
    else:
        for entry in reversed(st.session_state.query_history[-20:]):
            q = entry.get("pregunta", "")[:55]
            ok = entry.get("success", False)
            rows = entry.get("rows", 0)
            ts = entry.get("timestamp", datetime.now())
            d = datetime.now() - ts
            t_str = ("ahora" if d.seconds < 60 else
                     f"hace {d.seconds//60} min" if d.seconds < 3600 else
                     f"hace {d.seconds//3600}h" if d.days < 1 else
                     ts.strftime("%d/%m"))

            badge = (f'<span class="hist-badge hist-ok">✓ {rows}</span>'
                     if ok else f'<span class="hist-badge hist-err">✗</span>')

            st.markdown(
                f'<div class="hist-item">'
                f'<div class="hist-q">{q}</div>'
                f'<div class="hist-meta">{t_str} {badge}</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown('<div class="section-title">⭐ Guardadas</div>', unsafe_allow_html=True)
    if not st.session_state.saved_queries:
        st.caption("Usa Ctrl+S para guardar.")
    else:
        for sq in st.session_state.saved_queries:
            st.markdown(f'<div class="hist-item">⭐ {sq["pregunta"][:40]}…</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN LAYOUT — 2 columnas (centro + derecha)
# ═══════════════════════════════════════════════════════════════════════════
col_main, col_right = st.columns([7, 3], gap="medium")

# ═══════════════════════════════════════════════════════════════════════════
#  COLUMNA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════
with col_main:
    # ── Hero ──
    st.markdown(
        '<div class="hero-title">Pregunta sobre tus datos</div>'
        '<div class="hero-sub">Escribe en español lo que quieras saber de tu bodega</div>',
        unsafe_allow_html=True,
    )

    # ── Input ──
    pregunta = st.text_area(
        "Query",
        value=st.session_state.current_pregunta,
        placeholder="Ej: ¿Cuáles son los 5 productos más vendidos?",
        key="query_input",
        label_visibility="collapsed",
        max_chars=500,
        height=56,
    )

    # ── Botón ──
    _, c_btn, _ = st.columns([1, 1, 1])
    with c_btn:
        ejecutar = st.button(
            "⚡ Consultar",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.ejecutando or not pregunta.strip(),
        )

    # ── Chips ──
    st.markdown('<div class="chip-wrap">', unsafe_allow_html=True)
    for sug in SUGERENCIAS:
        if st.button(sug, key=f"ch_{sug}"):
            st.session_state.current_pregunta = sug
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════
    #  EJECUCIÓN
    # ═══════════════════════════════════════════════════════════════════════
    if ejecutar and pregunta.strip():
        st.session_state.current_pregunta = pregunta
        st.session_state.ejecutando = True
        st.rerun()

    if st.session_state.ejecutando:
        st.markdown(
            '<div style="padding:16px;">'
            '<div class="skel skel-line" style="width:25%"></div>'
            '<div class="skel skel-line" style="width:90%"></div>'
            '<div class="skel skel-line" style="width:55%"></div>'
            '<div class="skel skel-line" style="width:35%"></div>'
            '<div style="height:8px;"></div>'
            '<div class="skel skel-block"></div></div>',
            unsafe_allow_html=True,
        )
        try:
            respuesta = get_llm().invoke(
                PROMPT.format(schema=get_schema(), pregunta=st.session_state.current_pregunta)
            )
            sql = limpiar_sql(respuesta.content)

            if not sql.lower().lstrip().startswith("select"):
                st.session_state.last_error = "Solo ejecutamos consultas SELECT."
                st.session_state.last_sql = sql
                st.session_state.last_result = None
            else:
                df, err, elapsed = ejecutar_consulta(sql)
                st.session_state.last_sql = sql
                st.session_state.execution_time = elapsed
                st.session_state.last_result = df if not err else None
                st.session_state.last_error = err if err else None

            st.session_state.query_history.append({
                "pregunta": st.session_state.current_pregunta,
                "sql": sql, "success": st.session_state.last_error is None,
                "rows": len(st.session_state.last_result) if st.session_state.last_result is not None else 0,
                "timestamp": datetime.now(), "active": True,
            })
        except Exception as e:
            st.session_state.last_error = str(e)
            st.session_state.last_sql = None
            st.session_state.last_result = None

        st.session_state.ejecutando = False
        st.rerun()

    # ═══════════════════════════════════════════════════════════════════════
    #  RESULTADOS
    # ═══════════════════════════════════════════════════════════════════════
    if st.session_state.last_sql:
        st.markdown(
            render_sql_card(st.session_state.last_sql, st.session_state.execution_time),
            unsafe_allow_html=True,
        )

    if st.session_state.last_error:
        st.markdown(
            f'<div class="err-card">'
            f'<div class="err-title">⚠️ Error al ejecutar</div>'
            f'<div class="err-msg">{st.session_state.last_error}</div></div>',
            unsafe_allow_html=True,
        )

    elif st.session_state.last_result is not None:
        df = st.session_state.last_result

        # ── Tabs ──
        tb1, tb2, tb3 = st.columns(3)
        with tb1:
            if st.button("📊 Tabla", key="tab_tabla",
                         type="primary" if st.session_state.active_tab == "Tabla" else "secondary",
                         use_container_width=True):
                st.session_state.active_tab = "Tabla"
                st.rerun()
        with tb2:
            if st.button("📈 Gráfico", key="tab_grafico",
                         type="primary" if st.session_state.active_tab == "Gráfico" else "secondary",
                         use_container_width=True):
                st.session_state.active_tab = "Gráfico"
                st.rerun()
        with tb3:
            if st.button("📋 Estadísticas", key="tab_stats",
                         type="primary" if st.session_state.active_tab == "Estadísticas" else "secondary",
                         use_container_width=True):
                st.session_state.active_tab = "Estadísticas"
                st.rerun()

        if st.session_state.active_tab == "Tabla":
            render_table_tab(df)
        elif st.session_state.active_tab == "Gráfico":
            render_chart_tab(df)
        elif st.session_state.active_tab == "Estadísticas":
            render_stats_tab(df)

    # ── Footer ──
    st.markdown(
        '<div class="app-footer">'
        'Text-to-SQL · Capa 1 · Streamlit · LangChain · Groq (Llama 3.3 70B)</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  COLUMNA DERECHA
# ═══════════════════════════════════════════════════════════════════════════
with col_right:
    if st.session_state.last_result is not None:
        st.markdown(render_results_summary(st.session_state.last_result, st.session_state.execution_time),
                    unsafe_allow_html=True)
        st.markdown(render_preview(st.session_state.last_result), unsafe_allow_html=True)
        st.markdown(render_structure(st.session_state.last_result), unsafe_allow_html=True)
    elif st.session_state.last_error:
        st.markdown(
            '<div class="empty-state">'
            '<div style="font-size:28px;color:var(--text3);">⚠️</div>'
            '<div class="empty-title">Error</div>'
            '<div class="empty-text">Revisa el panel central.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(render_empty_state(), unsafe_allow_html=True)
