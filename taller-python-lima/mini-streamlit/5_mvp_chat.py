"""
5 · Un MVP completo: mini-chat 💬

Junta todo lo anterior: widgets de chat + estado (session_state) + un LLM.
~30 líneas = un chatbot funcional con memoria de conversación.

Correr (desde la raíz del repo):  streamlit run mini-streamlit/5_mvp_chat.py
"""

import os

import streamlit as st
from langchain_groq import ChatGroq

st.title("💬 Mini-chat (un MVP en ~30 líneas)")

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]


@st.cache_resource
def get_llm():
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)


# El historial vive en session_state; si no, se borraría en cada mensaje.
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "¡Hola! Soy un bot hecho en Streamlit. ¿En qué te ayudo?"}
    ]

# Pinta todo el historial en cada re-ejecución.
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Caja de chat (queda fija abajo).
if texto := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user"):
        st.markdown(texto)

    with st.chat_message("assistant"):
        # Convertimos el historial al formato de LangChain: ("human"/"ai", texto).
        historial = [
            ("human" if m["role"] == "user" else "ai", m["content"])
            for m in st.session_state.mensajes
        ]
        respuesta = st.write_stream(
            trozo.content for trozo in get_llm().stream(historial)
        )

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
