# 🛠️ Recursos y tecnologías — Taller Python Lima

> Brief técnico del taller práctico: **construir un agente de IA que responde
> preguntas en lenguaje natural consultando una base de datos**.

## Arquitectura en una línea

**Agente text-to-SQL (NL→SQL)** sobre una base **relacional**, orquestado con
LangChain/LangGraph y servido en una UI Streamlit local.
**No es RAG ni base de datos vectorial** — el modelo genera SQL, no recupera por similitud.

```
Usuario (pregunta en español)
        │
        ▼
Streamlit (UI local)
        │
        ▼
Agente ReAct  ──(tool calls)──►  Herramientas SQL  ──►  SQLite (read-only)
   (LangChain / LangGraph)                                   ▲
        │                                                    │
        └── LLM: Llama 3.3 70B vía Groq ─────────────────────┘
                (decide qué tool usar, escribe el SQL, lee el resultado, responde)
```

---

## Base de datos

- **Motor: SQLite 3** — **relacional**, embebida, sin servidor (un único archivo
  `data/bodega.db` que viaja dentro del repo).
- **No es vectorial.** No hay embeddings, vector store ni retrieval semántico.
- **Esquema** (bodega peruana, datos generados con Faker, semilla fija):

  | Tabla | Filas aprox. | Contenido |
  |---|---|---|
  | `productos` | 36 | catálogo (categoría, precio, stock) |
  | `clientes` | 90 | nombre, **distrito** (columna, no tabla), fecha de registro |
  | `ventas` | 700 | cabecera (cliente, fecha, total) |
  | `detalle_ventas` | 2 118 | líneas de cada venta (cantidad, subtotal) |

---

## Conexión a la base (cómo se conecta en el taller)

- **SQLAlchemy 2.x** como capa de acceso:
  ```python
  create_engine("sqlite:///file:data/bodega.db?mode=ro&uri=true")
  ```
- **Read-only por diseño** (`mode=ro`): es el *guardrail* de seguridad del agente.
  No puede `INSERT/UPDATE/DELETE/DROP` — SQLite rechaza la escritura a nivel de conexión.
- LangChain envuelve el engine con `SQLDatabase`; de ahí se derivan las herramientas.
- Para la tabla/gráfico final, la app re-ejecuta el `SELECT` con `pandas.read_sql_query`
  sobre la misma conexión read-only.
- **Sin infraestructura de red para la DB**: todo es local. La única llamada saliente
  es a la API del LLM (Groq).

---

## Modelo (¿simple o razonador? ¿qué hace?)

- **Proveedor: Groq** (motor de inferencia, API compatible con OpenAI) vía `langchain-groq`.
- **Modelo: `llama-3.3-70b-versatile`**, `temperature=0` (determinista).
- Es un **instruct model con tool-calling nativo**, **NO** un "reasoner" dedicado
  tipo o1/o3 (no hay *reasoning tokens* internos). El razonamiento que se observa es el
  **bucle ReAct a nivel de agente** (multi-paso con herramientas), no chain-of-thought
  interno del modelo.
- **Qué hace**: recibe la pregunta + los *schemas* de las tools → **decide qué tool
  llamar** → inspecciona el esquema → **redacta el SQL** → lo ejecuta → **lee el
  resultado** → redacta la respuesta en lenguaje natural.
- **¿Consulta la DB?** Sí, pero **indirectamente**: el modelo no ejecuta SQL por sí
  mismo — **emite tool calls** y el runtime (LangGraph) ejecuta la herramienta contra
  SQLite y le devuelve el resultado. El loop se repite hasta poder responder.

---

## Técnicas usadas

- **Tool calling / function calling** — el modelo elige qué función invocar.
- **Agente ReAct** (Reason → Act → Observe) vía `langchain.agents.create_agent`,
  que construye un grafo LangGraph por debajo.
- **Text-to-SQL** con **inyección de esquema en contexto** (las tools `list_tables`
  y `schema` le aportan el DDL).
- **System prompt engineering** — forzamos el orden: listar tablas → ver schema →
  verificar SQL → ejecutar → responder.
- **Self-correction / retry** — si el SQL falla, el agente lee el error y reintenta
  (se demuestra en vivo con la pregunta de "distrito", que lo lleva a asumir una tabla
  inexistente y corregirse usando la columna `distrito` de `clientes`).
- **Read-only sandboxing** — control de seguridad del agente a nivel de conexión.

---

## Las 4 herramientas del agente (`SQLDatabaseToolkit`)

| Tool | Función |
|---|---|
| `sql_db_list_tables` | lista las tablas de la base |
| `sql_db_schema` | devuelve el DDL/columnas de las tablas indicadas |
| `sql_db_query_checker` | valida el SQL (usa el LLM) antes de ejecutarlo |
| `sql_db_query` | ejecuta el `SELECT` y devuelve las filas |

---

## Stack y versiones exactas (`requirements.txt`, Python 3.11)

```
streamlit==1.58.0            # UI web local (re-ejecución de script + session_state)
langchain==1.3.10            # orquestación del agente (create_agent)
langchain-core==1.4.8
langchain-community==0.4.2   # SQLDatabase + SQLDatabaseToolkit
langchain-groq==1.1.3        # conector al LLM en Groq
langgraph==1.2.6             # grafo/estado del bucle ReAct (debajo de create_agent)
SQLAlchemy==2.0.51           # acceso a la DB (engine read-only)
pandas==3.0.3                # re-ejecutar el SELECT + dataframe/gráfico
Faker==40.23.0               # generar los datos de la bodega
```

---

## Requisitos para los asistentes

- **Python 3.11** (o 3.10+).
- **API key gratuita de Groq** — https://console.groq.com/keys (login con Google o
  GitHub; **sin tarjeta, sin crear proyecto**). Límites free tier: ~30 req/min y
  ~1 000 req/día por cuenta (suficiente: cada pregunta del agente son ~4-5 llamadas).
- Saber **Python básico**. No se requiere experiencia previa en LLMs.

## Estructura del repo (por etapas)

| Archivo | Qué demuestra |
|---|---|
| `app_0_hola.py` | Streamlit base (re-ejecución, `session_state`) |
| `app_1_chain.py` | LLM genera SQL en **una sola llamada** (sin agente) |
| `app_2_agente.py` | **Agente** con herramientas: explora, ejecuta y se auto-corrige |
| `app_3_completa.py` | App final: chat + SQL visible + tabla + gráfico + read-only |
| `data/generar_db.py` | genera `bodega.db` con Faker |
| `probar_setup.py` | prueba de humo end-to-end (verifica key + stack + agente) |
