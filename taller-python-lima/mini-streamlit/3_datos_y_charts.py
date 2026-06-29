"""
3 · Datos y gráficos 📊

Streamlit dibuja tablas y gráficos directo desde un DataFrame de pandas.
Incluye un cargador de CSV para que el usuario suba sus propios datos.

Correr (desde la raíz del repo):  streamlit run mini-streamlit/3_datos_y_charts.py
"""

import pandas as pd
import streamlit as st

st.title("📊 Datos y gráficos")

# Un DataFrame de ejemplo: ventas por día de una bodega.
df = pd.DataFrame(
    {
        "dia": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
        "ventas": [320, 290, 410, 380, 520, 760, 640],
    }
).set_index("dia")

st.subheader("Tabla")
st.dataframe(df, use_container_width=True)

st.subheader("Gráfico de barras (una línea de código)")
st.bar_chart(df)

st.divider()
st.subheader("Sube tu propio CSV")
archivo = st.file_uploader("Arrastra un archivo .csv", type="csv")
if archivo:
    tuyo = pd.read_csv(archivo)
    st.dataframe(tuyo.head(), use_container_width=True)
    st.caption(f"{len(tuyo)} filas · {len(tuyo.columns)} columnas")
