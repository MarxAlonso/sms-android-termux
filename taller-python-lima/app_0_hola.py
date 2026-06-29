"""
CAPA 0 — Hola, Streamlit 👋

Objetivo: una primera app para ver Streamlit funcionando y, de paso,
conocer la base de datos de la bodega que luego consultaremos con el agente.

Correr:   streamlit run app_0_hola.py
"""

import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Capa 0 · Hola", page_icon="👋")

# Conexión SOLO LECTURA a la bodega (mode=ro => nadie puede modificarla)
DB = "file:data/bodega.db?mode=ro"

st.title("👋 Hola, Python Lima")

# --- Conozcamos la base de datos ---------------------------------------------
st.subheader("Nuestra base de datos: la bodega 🏪")

con = sqlite3.connect(DB, uri=True)
tablas = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", con
)
st.write("**Tablas disponibles:**", ", ".join(tablas["name"]))

tabla = st.selectbox("Elige una tabla para curiosear:", tablas["name"])
df = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 50", con)
con.close()

st.dataframe(df, use_container_width=True)
st.caption(
    "👉 En las siguientes apps, en vez de elegir la tabla a mano, le vamos a "
    "**preguntar en español** y un agente de IA escribirá el SQL por nosotros."
)
