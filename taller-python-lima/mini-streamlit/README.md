# 🧪 Mini-taller: MVPs rápidos con Streamlit

Cinco apps cortas que muestran lo rápido que se construye una app web real —
**incluso con un LLM**— usando solo Python. De widgets a un chatbot funcional.

## Cómo correrlas

**Siempre desde la raíz del repo** (para que tomen tu `.streamlit/secrets.toml`):

```bash
streamlit run mini-streamlit/1_hola_widgets.py
streamlit run mini-streamlit/2_layout.py
streamlit run mini-streamlit/3_datos_y_charts.py
streamlit run mini-streamlit/4_primer_llm.py
streamlit run mini-streamlit/5_mvp_chat.py
```

## Qué muestra cada una

| App | Qué aprendes | ¿Usa LLM? |
|---|---|---|
| `1_hola_widgets.py` | Widgets + el modelo de re-ejecución + `session_state` | No |
| `2_layout.py` | Columnas, pestañas, sidebar, métricas, expander | No |
| `3_datos_y_charts.py` | `st.dataframe`, `st.bar_chart` y cargar un CSV | No |
| `4_primer_llm.py` | La primera llamada a un LLM, con streaming en vivo | ✅ Groq |
| `5_mvp_chat.py` | Un chatbot completo con memoria, en ~30 líneas | ✅ Groq |

## Requisitos

- El mismo entorno del taller (`pip install -r requirements.txt`).
- Para las apps 4 y 5: tu `GROQ_API_KEY` en `.streamlit/secrets.toml`
  (la misma del taller principal). Sácala gratis en https://console.groq.com/keys.

## La idea

> Streamlit convierte un script de Python en una web app. Sin HTML, sin JS, sin
> frontend. Es la forma más rápida de poner una idea —o un LLM— frente a un usuario.
