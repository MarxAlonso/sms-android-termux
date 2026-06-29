"""
2 · Layout: columnas, pestañas, sidebar 🧱

Con muy pocas líneas armas una interfaz ordenada y profesional.

Correr (desde la raíz del repo):  streamlit run mini-streamlit/2_layout.py
"""

import streamlit as st

st.title("🧱 Layout en Streamlit")

# Barra lateral: ideal para filtros, selectores, configuración.
with st.sidebar:
    st.header("Barra lateral")
    tema = st.radio("Tema favorito", ["Datos", "IA", "Web"])
    st.write(f"Elegiste: **{tema}**")

# Columnas: KPIs uno al lado del otro.
c1, c2, c3 = st.columns(3)
c1.metric("Usuarios", "1,204", "+12%")
c2.metric("Ventas", "S/ 8,430", "+4%")
c3.metric("Churn", "2.1%", "-0.3%")

st.divider()

# Pestañas: separar contenido sin recargar.
tab1, tab2 = st.tabs(["📊 Resumen", "📝 Detalle"])
with tab1:
    st.write("Las **pestañas** organizan secciones en el mismo espacio.")
with tab2:
    st.write("Y los **expanders** esconden lo secundario hasta que se necesita:")
    with st.expander("Ver más"):
        st.write("Contenido colapsable. Justo lo que usamos para 'Ver el SQL' en el agente.")
