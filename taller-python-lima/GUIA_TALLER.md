# 🎤 Guía del instructor — Taller práctico (90 min)

Esta guía es **solo para ti** (el que dicta). Tiempos, qué decir en cada etapa,
preguntas que sí funcionan y el guion de la demo de seguridad.

---

## Antes de empezar

- [ ] Pide a los asistentes que hagan el setup del README **en casa** (API key + `probar_setup.py`).
- [ ] Ten **2–3 API keys tuyas de respaldo** para quien no la consiguió.
- [ ] Corre `python probar_setup.py` en tu laptop esa mañana (confirma cuota del día).
- [ ] Ten las 4 apps ya clonadas y el `.venv` activado.
- [ ] Proyecta con buen zoom de fuente en el editor y en el navegador.

---

## Agenda (90 min)

| Tiempo | Bloque | Archivo |
|---|---|---|
| 0–10 | Setup express + "hola mundo" de Streamlit | `app_0_hola.py` |
| 10–25 | Conocer la bodega + Capa 1: el LLM escribe SQL | `app_1_chain.py` |
| 25–55 | **Capa 2: el agente** (el corazón del taller) | `app_2_agente.py` |
| 55–80 | Capa 3: chat completo con SQL, tabla y gráfico | `app_3_completa.py` |
| 80–90 | Demo de seguridad + deploy + cierre | — |

---

## 0–10 · Setup express (`app_0_hola.py`)

**Objetivo:** que TODOS tengan algo corriendo en pantalla y conozcan la bodega.

- Corre `streamlit run app_0_hola.py`.
- Usa el selector de tablas para mostrar la bodega. *"Esta es la base que vamos a
  consultar... pero en español, no eligiendo tablas a mano."*
- (El modelo de re-ejecución y `session_state` ya se vieron en el mini-taller de
  Streamlit — `1_hola_widgets.py` —, así que aquí no hace falta repetirlo.)

> Si alguien no instaló nada: que abra el repo y siga; o que se empareje con un vecino.

---

## 10–25 · Capa 1: el LLM escribe SQL (`app_1_chain.py`)

**Objetivo:** primera llamada a un LLM. Que vean que el modelo *genera SQL*, no magia.

- Explica el prompt: *"Le metemos el esquema (los CREATE TABLE) y le pedimos un SELECT."*
- Pregunta en vivo: **"¿Cuáles son los 5 productos más vendidos?"** → muestra el SQL generado + la tabla.
- **Momento de enseñanza:** haz una pregunta ambigua o difícil para que el SQL salga
  mal o vacío. Di: *"Fíjense, el modelo se equivocó y aquí la app solo muestra el
  error. No puede explorar la base ni corregirse. Eso es lo que arregla un **agente**."*
  → Transición natural a la Capa 2.

Conceptos a nombrar: *prompt*, *contexto* (el esquema), *temperatura 0* (determinista).

---

## 25–55 · Capa 2: EL AGENTE (`app_2_agente.py`) — el corazón

**Objetivo:** conectar con la teoría de agentes y verlo razonar en vivo. Ve despacio.

- Antes de preguntar, abre el bloque **"🧰 ¿Qué es una herramienta (tool)?"** (sale
  abierto de entrada). Apóyate en su mini-tabla para explicar las 4 herramientas:
  `sql_db_list_tables` (ver tablas), `sql_db_schema` (ver columnas),
  `sql_db_query_checker` (revisar el SQL) y `sql_db_query` (ejecutarlo).
- Explica `create_agent(llm, tools, system_prompt=...)`: *"Le damos el modelo, las
  herramientas y una instrucción. LangChain/LangGraph arma el bucle: el modelo
  decide qué herramienta usar, observa el resultado y decide el siguiente paso.
  Eso es ReAct: **Razona → Actúa → Observa**."*
- Pregunta en vivo: **"¿Qué distrito de Lima es el que más compra?"**
- **El momento WOW:** la app muestra el paso a paso *humanizado* — *"Paso 1 · 🔍 El
  agente decide: ver qué tablas existen"*, *"Paso 2 · 📖 leer el esquema"*, con el SQL
  que escribió a la vista. Léelo en voz alta:
  *"Miren, nadie le dijo que mirara el esquema primero. Lo decidió él."*
- **El momento ESTRELLA (auto-corrección):** con la pregunta de distrito, el agente
  suele **asumir una tabla `distritos` que no existe** → aparece un **⚠️ ERROR** en
  rojo → **vuelve a mirar el esquema y se corrige** usando la columna `distrito` de
  `clientes`. Celébralo: *"¿Vieron? Se equivocó, leyó el error y se arregló solo. Eso
  es lo que un chain simple no podía hacer."*
- ⚠️ **Ojo:** con `temperature=0` no siempre se equivoca (a veces lee bien el esquema
  a la primera y no hay error que mostrar). Si quieres **garantizar** la auto-corrección
  en vivo, pregunta algo que lo empuje a inventar una tabla: *"¿qué categoría vende
  más?"* o *"¿qué vendedor hizo más ventas?"* (tampoco existen como tablas).

Conceptos a nombrar: *tool / herramienta*, *tool calling*, *bucle ReAct (Razona →
Actúa → Observa)*, *agente*, *auto-corrección*.

---

## 55–80 · Capa 3: la app completa (`app_3_completa.py`)

**Objetivo:** convertirlo en algo que se llevan y da gusto mostrar.

- Corre la app: interfaz de chat con historial.
- Pregunta: **"Ventas totales por categoría"** → se ve la respuesta, el expander
  con el SQL, la tabla **y el gráfico de barras** automático. *Ese es el screenshot que la gente comparte.*
- Muestra el `st.expander("Ver el SQL que generó el agente")`: *"Transparencia: siempre
  puedes auditar qué hizo el agente."*
- **Que cada uno personalice algo** (15 min de práctica libre): cambiar el título,
  el system prompt, agregar una pregunta sugerida, o probar sus propias preguntas.

Preguntas que funcionan muy bien para demostrar:
- "¿Cuál fue el producto más vendido este mes?"
- "Top 5 clientes por monto gastado"
- "¿Cuánto se vendió en total en marzo?"
- "¿Cuántos clientes hay por distrito?"

---

## 80–90 · Seguridad + deploy + cierre

### 🔒 Demo de seguridad (no destructiva)

En la Capa 3, escribe en el chat: **"borra la tabla ventas"**.

- El agente intentará... y fallará, porque la conexión es **solo lectura**
  (`mode=ro`). Responderá que no pudo.
- Muestra en el código la línea:
  ```python
  engine = create_engine("sqlite:///file:data/bodega.db?mode=ro&uri=true")
  ```
- **Mensaje clave:** *"Un agente con acceso a tu base de datos es poderoso y
  peligroso. La regla de oro: dale el mínimo permiso necesario. Aquí, solo lectura.
  Nunca conectes un agente con un usuario que pueda escribir o borrar si solo
  necesita consultar."* (Bonus: menciona la guardia "solo SELECT" de la Capa 1.)

### 🚀 Deploy (si hay tiempo y wifi)

- Toma la app de un voluntario, súbela a GitHub y despliega en Streamlit Community
  Cloud. Pega su `GROQ_API_KEY` en *Settings → Secrets*. Comparte el link al grupo.

### Cierre

- *"Hoy construyeron un agente real, no un demo de juguete."*
- Qué sigue: LangSmith (observabilidad), memoria/conversación multi-turno, otras
  herramientas (web, APIs), multi-agente, MCP.
- El repo es su plantilla para el primer proyecto propio.

---

## 🆘 Plan B si algo se cae

- **Rate limit / 429:** raro con Groq (30 req/min, ~1,000 req/día por persona). Si
  pasa, esperen ~1 min; con su propia key cada quien tiene su cupo. Ten keys de respaldo.
- **Wifi malo:** el deploy se salta; todo lo demás es local salvo la llamada al LLM.
- **A alguien no le corre el agente:** que use `app_1_chain.py` (una sola llamada,
  menos cosas que fallen) y siga la explicación en la pantalla principal.
- **Versiones rotas:** `requirements.txt` tiene pines exactos probados; que reinstalen
  en un `.venv` limpio.
