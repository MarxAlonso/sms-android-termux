"""
1 · Widgets y estado 🎛️

La idea MÁS importante de Streamlit: el script se RE-EJECUTA completo, de arriba
a abajo, en CADA interacción (cada clic, cada tecla). Por eso, para "recordar"
algo entre interacciones, usamos st.session_state.

Correr (desde la raíz del repo):  streamlit run mini-streamlit/1_hola_widgets.py
"""

import streamlit as st

st.title("🎛️ Widgets y estado")

nombre = st.text_input("¿Cómo te llamas?")
if nombre:
    st.write(f"¡Hola, **{nombre}**! 👋")

edad = st.slider("Tu edad", 1, 100, 25)
st.write(f"En 10 años tendrás **{edad + 10}** años.")

if st.checkbox("Mostrar un dato"):
    st.info("Streamlit convierte un script de Python en una web app — sin HTML, CSS ni JS.")

st.divider()
st.subheader("El contador: por qué existe `session_state`")

# Sin session_state este número volvería a 0 en cada clic, porque el script
# entero se vuelve a ejecutar. session_state sobrevive entre re-ejecuciones.
if "conteo" not in st.session_state:
    st.session_state.conteo = 0

if st.button("➕ Súmame uno"):
    st.session_state.conteo += 1

st.metric("Clics acumulados", st.session_state.conteo)
st.caption("Prueba a quitar el `session_state`: verás que el contador nunca pasa de 1. Ese es el 'aha'.")
