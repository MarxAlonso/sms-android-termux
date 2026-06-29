"""
4 · Tu primera app con un LLM 🤖

Mira lo POCO que cuesta: texto entra, texto sale. Con respuesta en vivo (streaming).
Necesita tu GROQ_API_KEY en .streamlit/secrets.toml (la misma del taller).

Correr (desde la raíz del repo):  streamlit run mini-streamlit/4_primer_llm.py
"""

import os

import streamlit as st
from langchain_groq import ChatGroq

st.title("🤖 Tu primera app con un LLM")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]


@st.cache_resource
def get_llm():
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)


prompt = st.text_area(
    "Escribe algo y el modelo responde:",
    "Explícame qué es un agente de IA como si tuviera 12 años.",
)

if st.button("Enviar") and prompt:
    llm = get_llm()
    # st.write_stream muestra la respuesta token por token, en vivo.
    st.write_stream(trozo.content for trozo in llm.stream(prompt))
