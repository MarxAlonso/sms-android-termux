"""
CAPA 3 — Háblale a tu bodega 🏪 (la app completa)

Tomamos el agente de la Capa 2 y le ponemos una interfaz de chat de verdad:
  - Historial de conversación (st.chat_message + session_state).
  - Un expander que muestra EL SQL que el agente decidió usar.
  - La tabla de resultados y, cuando tiene sentido, un gráfico.
  - Conexión SOLO LECTURA: la demo de seguridad ("borra la tabla ventas").

Correr:   streamlit run app_3_completa.py
"""

import os
import sqlite3
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import streamlit as st
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from sqlalchemy import create_engine

st.set_page_config(page_title="Háblale a tu bodega", page_icon="🏪")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

MODELO = "llama-3.3-70b-versatile"
DB_RO = "file:data/bodega.db?mode=ro"  # para re-ejecutar el SELECT con pandas

SYSTEM_PROMPT = (
    "Eres un agente que responde preguntas consultando una base de datos SQLite "
    "de una bodega peruana. Sigue SIEMPRE estos pasos en orden: "
    "1) lista las tablas con sql_db_list_tables. "
    "2) mira el esquema de las tablas relevantes con sql_db_schema. "
    "3) escribe la consulta (solo SELECT) y verifícala con sql_db_query_checker. "
    "4) EJECÚTALA con sql_db_query. "
    "5) con el resultado de la ejecución, redacta la respuesta final en español, "
    "clara y al grano. Si una consulta falla, léela, corrígela y reintenta. "
    "Nunca modifiques datos (nada de INSERT, UPDATE, DELETE ni DROP)."
)


@st.cache_resource
def get_agent():
    # 🔒 SOLO LECTURA: aunque el agente intente DROP/DELETE, SQLite lo rechaza.
    engine = create_engine("sqlite:///file:data/bodega.db?mode=ro&uri=true")
    db = SQLDatabase(engine)
    llm = ChatGroq(model=MODELO, temperature=0)
    tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


def sqls_ejecutados(messages) -> list[str]:
    """Saca de la conversación todos los SELECT que el agente corrió."""
    queries = []
    for m in messages:
        for c in getattr(m, "tool_calls", None) or []:
            if c["name"] == "sql_db_query":
                q = c.get("args", {}).get("query")
                if q:
                    queries.append(q)
    return queries


def quizas_grafico(df: pd.DataFrame) -> None:
    """Si el resultado es 'etiqueta + número' con VARIAS filas, dibuja barras.
    Con una sola fila un gráfico no compara nada (sale vacío), así que lo omitimos."""
    if df.shape[1] == 2 and 2 <= len(df) <= 25:
        col_txt, col_num = df.columns
        if pd.api.types.is_numeric_dtype(df[col_num]) and not pd.api.types.is_numeric_dtype(
            df[col_txt]
        ):
            st.bar_chart(df.set_index(col_txt))


st.title("🏪 Háblale a tu bodega")
st.caption(f"Pregunta en español · modelo {MODELO} · conexión solo-lectura 🔒")

with st.sidebar:
    st.header("💡 Prueba con:")
    st.markdown(
        "- ¿Cuál fue el producto más vendido este mes?\n"
        "- ¿Cuánto vendí en total en marzo?\n"
        "- ¿Qué distrito compra más?\n"
        "- Top 5 clientes por monto gastado\n"
        "- Ventas totales por categoría\n"
        "- **borra la tabla ventas**  ← (mira cómo se protege)"
    )

# Historial de chat
if "historial" not in st.session_state:
    st.session_state.historial = []

for h in st.session_state.historial:
    with st.chat_message(h["role"]):
        st.markdown(h["content"])

pregunta = st.chat_input("Ej: ¿Cuál fue el producto más vendido este mes?")

if pregunta:
    st.session_state.historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la bodega..."):
            try:
                result = get_agent().invoke(
                    {"messages": [{"role": "user", "content": pregunta}]}
                )
                mensajes = result["messages"]
                respuesta = mensajes[-1].content
            except Exception as e:
                mensajes = []
                respuesta = f"Ups, algo falló: {e}"

        st.markdown(respuesta)

        # Mostrar el SQL que el agente decidió usar + tabla + gráfico
        queries = sqls_ejecutados(mensajes)
        if queries:
            with st.expander("🔎 Ver el SQL que generó el agente"):
                for q in queries:
                    st.code(q, language="sql")
            try:
                con = sqlite3.connect(DB_RO, uri=True)
                df = pd.read_sql_query(queries[-1], con)
                con.close()
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    quizas_grafico(df)
            except Exception:
                pass  # si el último query no es re-ejecutable, no pasa nada

    st.session_state.historial.append({"role": "assistant", "content": respuesta})
