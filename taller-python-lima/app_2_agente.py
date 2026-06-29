"""
CAPA 2 — Un agente que decide 🔵  (la capa para ENTENDER cómo funciona)

Aquí está el corazón del taller. En vez de UNA llamada al modelo (como en la
Capa 1), le damos HERRAMIENTAS (tools) y lo dejamos decidir cuál usar y cuándo.

Una herramienta es, literalmente, una función que el modelo puede llamar.
Le dimos 4 (vienen del SQLDatabaseToolkit de LangChain):

    sql_db_list_tables   -> ver qué tablas existen
    sql_db_schema        -> leer las columnas de una tabla
    sql_db_query_checker -> revisar que el SQL esté bien
    sql_db_query         -> ejecutar el SQL

El agente encadena estos pasos SOLO. A ese bucle se le llama ReAct:
Razona (¿qué hago?) -> Actúa (usa una herramienta) -> Observa (mira el resultado)
-> repite -> responde. Esta app te deja VER ese bucle paso a paso.

Correr:   streamlit run app_2_agente.py
"""

import os
import warnings

# langchain-community avisa con un warning de "sunset"; lo silenciamos para que
# la consola del taller quede limpia.
warnings.filterwarnings("ignore")

import streamlit as st
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from sqlalchemy import create_engine

st.set_page_config(page_title="Capa 2 · Agente SQL", page_icon="🔵")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

MODELO = "llama-3.3-70b-versatile"

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

# Cada herramienta del toolkit, traducida a lenguaje humano para mostrarla en la UI.
HERRAMIENTAS = {
    "sql_db_list_tables": ("🔍", "Ver qué tablas existen en la base"),
    "sql_db_schema": ("📖", "Leer las columnas de una o más tablas"),
    "sql_db_query_checker": ("🔎", "Revisar que el SQL esté bien escrito"),
    "sql_db_query": ("▶️", "Ejecutar el SQL en la base de datos"),
}


@st.cache_resource
def get_agent():
    # Conexión SOLO LECTURA: el agente jamás podrá modificar la bodega.
    engine = create_engine("sqlite:///file:data/bodega.db?mode=ro&uri=true")
    db = SQLDatabase(engine)
    llm = ChatGroq(model=MODELO, temperature=0)
    tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


def texto_de(contenido) -> str:
    """El contenido de un mensaje puede ser texto o una lista de bloques."""
    if isinstance(contenido, str):
        return contenido
    return " ".join(b.get("text", "") for b in contenido if isinstance(b, dict))


def es_error(texto: str) -> bool:
    """¿La herramienta devolvió un error? (clave para mostrar la auto-corrección)"""
    t = texto.lower().strip()
    marcadores = ("no such table", "no such column", "operationalerror", "(sqlite3", "traceback")
    return t.startswith("error") or "error:" in t or any(mk in t for mk in marcadores)


st.title("🔵 Capa 2 — Un agente que decide")
st.caption(
    "El modelo ahora tiene HERRAMIENTAS y decide cuál usar. Mira cómo razona, "
    "paso a paso. Conexión solo-lectura 🔒"
)

# --- Bloque explicativo: ¿qué es una herramienta? (visible de entrada) ---
with st.expander("🧰 ¿Qué es una herramienta (tool)? — léelo antes de empezar", expanded=True):
    st.markdown(
        "Una **herramienta** es una función que el modelo puede **decidir usar** "
        "cuando la necesita. Nosotros no le decimos los pasos: **él elige**. "
        "Le dimos estas 4:"
    )
    for nombre, (emoji, desc) in HERRAMIENTAS.items():
        st.markdown(f"- {emoji} **`{nombre}`** — {desc}")
    st.markdown(
        "\nEl agente repite este bucle (se llama **ReAct**): "
        "**Razona** (¿qué hago?) → **Actúa** (usa una herramienta) → "
        "**Observa** (mira el resultado) → repite → **responde**."
    )

pregunta = st.text_input(
    "Pregunta en español:", "¿Qué distrito de Lima es el que más compra?"
)
st.caption(
    "💡 Pista para el demo: **no existe** una tabla `distritos`. El distrito es una "
    "**columna** de la tabla `clientes`. Observa cómo el agente lo descubre (o se corrige)."
)

if st.button("Preguntar al agente") and pregunta:
    agent = get_agent()
    respuesta_final = ""
    paso = 0

    st.subheader("🧠 Paso a paso del agente")
    entrada = {"messages": [{"role": "user", "content": pregunta}]}

    with st.spinner("El agente está razonando..."):
        for actualizacion in agent.stream(entrada, stream_mode="updates"):
            for _nodo, datos in actualizacion.items():
                for m in datos.get("messages", []):
                    tipo = type(m).__name__
                    tool_calls = getattr(m, "tool_calls", None)

                    # 1) El agente DECIDE usar una o más herramientas (Razona + Actúa)
                    if tool_calls:
                        for c in tool_calls:
                            paso += 1
                            emoji, desc = HERRAMIENTAS.get(c["name"], ("🔧", c["name"]))
                            st.markdown(f"**Paso {paso} · {emoji} El agente decide:** {desc}")
                            # Si la herramienta lleva un SQL, lo mostramos (lo que escribió)
                            sql = (c.get("args") or {}).get("query")
                            if sql:
                                st.code(sql, language="sql")

                    # 2) Resultado que el agente OBSERVA
                    elif tipo == "ToolMessage":
                        contenido = texto_de(m.content).strip()
                        # El checker a veces envuelve el SQL en ```sql ... ```; lo limpiamos.
                        limpio = contenido.replace("```sql", "").replace("```", "").strip()
                        if es_error(contenido):
                            st.error(
                                f"⚠️ La herramienta `{m.name}` devolvió un ERROR. "
                                "El agente lo va a leer y **corregirse solo**:\n\n"
                                f"{contenido[:400]}"
                            )
                        elif len(limpio) <= 300:
                            st.markdown(f"↳ 👀 *observa* (`{m.name}`):")
                            st.code(limpio)
                        else:
                            with st.expander(f"👀 Lo que el agente observa de `{m.name}`"):
                                st.code(limpio[:800] + ("…" if len(limpio) > 800 else ""))

                    # 3) Respuesta final: un AIMessage SIN tool calls
                    elif tipo == "AIMessage" and not tool_calls:
                        respuesta_final = texto_de(m.content)

    st.divider()
    st.subheader("✅ Respuesta final")
    st.success(respuesta_final or "El agente no devolvió una respuesta final.")
