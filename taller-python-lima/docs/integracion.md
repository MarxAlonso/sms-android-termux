# 🔗 Integración del Sistema

## Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│              app_1_chain.py                   │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │Streamlit │  │LangChain │  │   Pandas    │ │
│  │   1.58   │  │   1.3    │  │    3.0      │ │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘ │
│       │              │              │         │
│       ▼              ▼              ▼         │
│  ┌───────────────────────────────────────┐   │
│  │              Plotly 5.x                │   │
│  │         Pygments (highlight)           │   │
│  │         SQLite3 (nativo)               │   │
│  └───────────────────────────────────────┘   │
│                                               │
│  ┌───────────────────────────────────────┐   │
│  │         Groq API (cloud)               │   │
│  │    llama-3.3-70b-versatile            │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Dependencias (requirements.txt)

```txt
streamlit==1.58.0
langchain==1.3.10
langchain-core==1.4.8
langchain-groq==1.1.3
pandas==3.0.3
Faker==40.23.0
SQLAlchemy==2.0.51
```

### Dependencias adicionales (no en requirements original)

```txt
plotly>=5.18.0          # Gráficos interactivos
Pygments>=2.17.0        # Syntax highlighting SQL
```

---

## Configuración

### 1. API Key de Groq

Archivo: `.streamlit/secrets.toml`

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Streamlit carga este archivo automáticamente y expone los valores en `st.secrets`.

### 2. Base de Datos

Archivo: `data/bodega.db` (SQLite)

Generación:
```bash
python data/generar_db.py
```

Se conecta en modo **solo lectura**:
```python
DB = "file:data/bodega.db?mode=ro"
```

### 3. Cache de Streamlit

| Decorador | Uso | Primer llamado | Llamados siguientes |
|-----------|-----|----------------|---------------------|
| `@st.cache_resource` | `get_llm()` | Crea ChatGroq | Reutiliza instancia |
| `@st.cache_data` | `get_schema()` | Consulta BD y parsea | Devuelve del caché |
| `@st.cache_data` | `get_schema_parsed()` | Consulta BD y estructura | Devuelve del caché |

---

## Comunicación entre Componentes

### Streamlit → Groq API

```
Streamlit                         Groq API (cloud)
   │                                    │
   │  POST https://api.groq.com/        │
   │  /openai/v1/chat/completions       │
   │                                    │
   │  Headers:                          │
   │    Authorization: Bearer gsk_...   │
   │    Content-Type: application/json  │
   │                                    │
   │  Body:                             │
   │  {                                 │
   │    "model": "llama-3.3-70b-        │
   │              versatile",           │
   │    "messages": [                   │
   │      {"role": "system",            │
   │       "content": "Eres un          │
   │        experto en SQL..."},        │
   │      {"role": "user",              │
   │       "content": "Pregunta: ..."}  │
   │    ],                              │
   │    "temperature": 0                │
   │  }                                 │
   │                                    │
   │◀── 200 OK                          │
   │  {                                 │
   │    "choices": [{                   │
   │      "message": {                  │
   │        "content": "SELECT ..."     │
   │      }                             │
   │    }]                              │
   │  }                                 │
   │                                    │
```

LangChain abstrae esta comunicación. El developer solo ve:

```python
llm = ChatGroq(model=MODELO, temperature=0)
respuesta = llm.invoke(prompt)
sql = respuesta.content
```

### Streamlit → SQLite

Comunicación directa vía `sqlite3` (nativo de Python):

```python
con = sqlite3.connect("file:data/bodega.db?mode=ro", uri=True)
df = pd.read_sql_query(sql, con)
con.close()
```

---

## Flujo de Datos Detallado

```
┌─────────────┐
│  Usuario     │
│  Pregunta    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────────┐
│  Streamlit   │────▶│  ChatGroq.invoke()   │
│  session     │     │  (LangChain → Groq)  │
│  state       │     └──────────┬───────────┘
└──────┬──────┘                 │
       │                        ▼
       │              ┌──────────────────────┐
       │              │  Texto SQL plano      │
       │              │  Ej: "SELECT ..."     │
       │              └──────────┬───────────┘
       │                         │
       ▼                         ▼
┌─────────────────────────────────────────────┐
│  Limpiar SQL (regex)                         │
│  Validar SELECT (seguridad)                   │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  sqlite3.connect() → pd.read_sql_query()     │
│  → DataFrame                                  │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  Streamlit renderiza:                        │
│  ┌─ SQL Card (highlight)                    │
│  ├─ DataFrame (tabla)                       │
│  ├─ Plotly chart (gráfico)                  │
│  └─ Stats cards (estadísticas)              │
└─────────────────────────────────────────────┘
```

---

## Manejo de Estado

La app usa `st.session_state` para mantener estado entre re-ejecuciones.

### Estados clave:

```
INICIAL
  │
  ├─ ejecutando = False
  ├─ last_result = None
  └─ current_pregunta = ""
  
ESPERANDO INPUT
  │
  ├─ Usuario escribe o hace clic en chip
  └─ current_pregunta se actualiza

EJECUTANDO
  │
  ├─ ejecutando = True
  ├─ Se muestra skeleton
  ├─ LLM genera SQL
  └─ Se ejecuta consulta

RESULTADO
  │
  ├─ ejecutando = False
  ├─ last_result = DataFrame (éxito) | None (error)
  ├─ last_sql = SQL generado
  └─ last_error = mensaje de error (si aplica)
```

### Diagrama de transición de estados:

```
    ┌──────────┐
    │  INIT    │
    └────┬─────┘
         │
         ▼
    ┌──────────┐     click botón     ┌────────────┐
    │  IDLE    │────────────────────▶│ LOADING    │
    │          │                     │            │
    │  Muestra │     ┌───────────────│ Skeleton   │
    │  input + │     │               │ LLM call   │
    │  empty   │     │               │ SQL exec   │
    └──────────┘     │               └─────┬──────┘
         ▲           │                     │
         │           │                     ▼
         │           │           ┌─────────────────────┐
         │           │     ┌────│     RESULT           │
         │           │     │    │                     │
         │           │     │    │  Tabla / Gráfico    │
         │           │     │    │  Estadísticas       │
         │           │     │    └──────────┬──────────┘
         │           │     │               │
         │           │     ▼               ▼
         │           │  ┌─────────────────────┐
         │           │  │     ERROR           │
         │           │  │                     │
         │           │  │  Error card         │
         │           │  │  Sugerencia         │
         │           │  └─────────────────────┘
         │           │
         └───────────┘
           Nueva consulta
```

---

## Configuración del Prompt

El prompt del sistema es crítico para obtener SQL correcto:

```python
PROMPT = """Eres un experto en SQL para SQLite. Esta es la estructura:

{schema}

Escribe UNA sola consulta SQL (solo SELECT) que responda la pregunta.
Devuelve ÚNICAMENTE el SQL, sin explicaciones ni ```.

Pregunta: {pregunta}
SQL:"""
```

### Elementos clave:
1. **Rol**: "experto en SQL para SQLite"
2. **Contexto**: esquema completo de la BD (4 tablas)
3. **Restricción**: solo SELECT
4. **Formato**: solo SQL, sin markdown ni explicaciones

---

## Seguridad

### Capa 1: Modo Read-Only (SQLite URI)

```python
DB = "file:data/bodega.db?mode=ro"
```

SQLite rechaza cualquier INSERT/UPDATE/DELETE cuando se conecta en modo read-only.

### Capa 2: Validación de Query

```python
if not sql.lower().lstrip().startswith("select"):
    st.error("Por seguridad solo ejecutamos consultas SELECT.")
```

### Capa 3: Sanitización de Output

```python
def limpiar_sql(texto):
    return re.sub(r"```sql|```", "", texto).strip()
```

Previene inyección de markdown en la visualización del SQL.
