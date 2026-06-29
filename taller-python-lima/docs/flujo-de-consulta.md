# 🔄 Flujo de Consulta

Este documento describe paso a paso lo que sucede cuando un usuario escribe una pregunta y presiona "Consultar".

---

## 1. Entrada del Usuario

```
Usuario escribe: "¿Cuáles son los 5 productos más vendidos?"
```

El texto se captura en un `st.text_area` con:
- Placeholder: *"Ej: ¿Cuáles son los 5 productos más vendidos?"*
- Auto-expansión hasta 200px de altura
- Límite: 500 caracteres
- Contador de caracteres en la esquina inferior derecha

También puede hacer clic en un **chip de sugerencia** (`st.button`) que auto-completa el input.

---

## 2. Activación

Tres formas de ejecutar:

| Método | Acción |
|--------|--------|
| Botón "Consultar" | Click en el botón principal |
| Ctrl + Enter | Atajo de teclado (navegador) |
| Click en chip | Auto-completa y requiere click en botón |

Al presionar, se activa `st.session_state.ejecutando = True` y se fuerza un `st.rerun()`.

---

## 3. Estado de Carga (Skeleton)

```
┌──────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  30%    │  ← Skeleton: título
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │  ← Skeleton: línea completa
│ ▓▓▓▓▓▓▓▓▓▓      60%         │  ← Skeleton: línea media
│ ▓▓▓▓      40%                │  ← Skeleton: línea corta
│                              │
│ ┌──────────────────────────┐ │
│ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │  ← Skeleton: bloque grande
│ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

Se muestra un esqueleto animado (shimmer) que simula la estructura final mientras el LLM genera la respuesta.

---

## 4. Generación del SQL (LLM)

### 4.1 Construcción del Prompt

```python
PROMPT = """Eres un experto en SQL para SQLite. Esta es la estructura:

{schema}

Escribe UNA sola consulta SQL (solo SELECT) que responda la pregunta.
Devuelve ÚNICAMENTE el SQL, sin explicaciones ni ```.

Pregunta: {pregunta}
SQL:"""
```

El `{schema}` se reemplaza con el output de `get_schema()`:

```sql
CREATE TABLE productos (
    id        INTEGER PRIMARY KEY,
    nombre    TEXT    NOT NULL,
    categoria TEXT    NOT NULL,
    precio    REAL    NOT NULL,
    stock     INTEGER NOT NULL
);

CREATE TABLE clientes (...);
CREATE TABLE ventas (...);
CREATE TABLE detalle_ventas (...);
```

### 4.2 Llamada al Modelo

```python
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
respuesta = llm.invoke(prompt_formateado)
```

- **Modelo**: Llama 3.3 70B (via Groq API)
- **Temperatura**: 0 (máxima determinismo)
- **Caché**: `@st.cache_resource` — el LLM se crea una sola vez

### 4.3 Post-procesamiento

```python
def limpiar_sql(texto):
    return re.sub(r"```sql|```", "", texto).strip()
```

El modelo a veces envuelve el SQL en bloques ```sql ... ```; esta función los elimina.

---

## 5. Validación de Seguridad

```python
if not sql.lower().lstrip().startswith("select"):
    st.error("Por seguridad solo ejecutamos consultas SELECT.")
```

Solo se permiten consultas **SELECT**. Cualquier otro statement es rechazado.

> La base de datos está en modo `mode=ro` (read-only), pero esta validación da una capa extra.

---

## 6. Ejecución SQL

```python
con = sqlite3.connect("file:data/bodega.db?mode=ro", uri=True)
df = pd.read_sql_query(sql, con)
con.close()
```

| Detalle | Valor |
|---------|-------|
| Conexión | `file:data/bodega.db?mode=ro` (URI) |
| Driver | sqlite3 nativo de Python |
| Resultado | `pandas.DataFrame` |
| Medición | `time.time()` antes/después → tiempo en ms |

Si el SQL es inválido, se atrapa la excepción y se muestra en una **tarjeta de error** estilizada.

---

## 7. Visualización de Resultados

### 7.1 SQL Card

```
┌─────────────────────────────────────┐
│  SQL GENERADO               234 ms  │
│                                     │
│  SELECT p.nombre,                   │
│         SUM(dv.cantidad) AS total   │  ← Syntax highlighting
│  FROM productos p                   │
│  JOIN detalle_ventas dv ON ...      │
│  GROUP BY p.nombre                  │
│  ORDER BY total DESC                │
│  LIMIT 5                            │
│                                     │
│                          [📋 Copiar] │
└─────────────────────────────────────┘
```

- Fondo oscuro (#1A1A1A) con texto claro
- **Syntax highlighting**:
  - Keywords: terracota #D97757
  - Funciones: púrpura #8B5CF6
  - Strings: verde #10B981
  - Números: azul #3B82F6
  - Comentarios: gris #9CA3AF
- Botón "Copiar" que usa `navigator.clipboard.writeText()`
- Tiempo de ejecución en milisegundos

### 7.2 Tabla de Datos (Tab "📊 Tabla")

| Característica | Implementación |
|---------------|----------------|
| Renderizado | `st.dataframe()` nativo de Streamlit |
| Altura | `min(400, 40 + filas * 35)` — responsiva |
| Info bar | "Mostrando X filas × Y columnas" |
| Exportación | Botones CSV/Excel/JSON (placeholder funcional) |

### 7.3 Gráfico (Tab "📈 Gráfico")

Auto-detección del tipo de gráfico según los datos:

```
text_cols ≥ 1 + num_cols ≥ 1:
  │
  ├─ categorías ≤ 5  → Pie chart
  └─ categorías > 5  → Bar chart

num_cols ≥ 2          → Scatter plot
num_cols = 1          → Histogram
```

El usuario puede cambiar el tipo de gráfico con un `selectbox`.

Configuración de Plotly:
- Tema: `template="none"` (fondo blanco)
- Tipografía: Inter, 12px
- Grid: gris suave #F0F0F0
- Toolbar: descarga PNG, zoom, pan

### 7.4 Estadísticas (Tab "📋 Estadísticas")

| Componente | Contenido |
|-----------|-----------|
| Tarjetas | Filas, Columnas, Promedio/Mín/Máx de top 3 columnas numéricas |
| DataFrame describe | `.describe()` de pandas en columnas numéricas |

---

## 8. Registro en Historial

```python
entry = {
    "pregunta": pregunta,
    "sql": sql,
    "success": True/False,
    "rows": len(df),
    "timestamp": datetime.now(),
    "active": True,
}
st.session_state.query_history.append(entry)
```

Cada consulta se guarda en `session_state` y se muestra en el sidebar con:
- Timestamp relativo ("hace 5 min")
- Estado (✓ éxito / ✗ error)
- Número de filas
- Indicador de activo (borde terracota)

---

## 9. Manejo de Errores

| Error | Causa | Visualización |
|-------|-------|---------------|
| SQL no SELECT | Modelo generó un DELETE/UPDATE/etc. | Tarjeta roja con advertencia |
| SQL inválido | Error de sintaxis SQL | Tarjeta con mensaje de error y sugerencia |
| Error de conexión | BD no encontrada | Streamlit error nativo |

---

## Diagrama de Secuencia

```
Usuario          Streamlit          LLM (Groq)          SQLite
   │                  │                  │                  │
   │── pregunta ─────▶│                  │                  │
   │                  │                  │                  │
   │                  │── prompt ───────▶│                  │
   │                  │                  │                  │
   │                  │◀─── SQL ────────│                  │
   │                  │                  │                  │
   │                  │──── SQL ──────────────────────────▶│
   │                  │◀─── DataFrame ─────────────────────│
   │                  │                  │                  │
   │◀── resultados ──│                  │                  │
   │                  │                  │                  │
```

---

## Variables de Estado (session_state)

| Variable | Tipo | Propósito |
|----------|------|-----------|
| `query_history` | `list[dict]` | Historial de consultas |
| `saved_queries` | `list[dict]` | Consultas guardadas |
| `current_pregunta` | `str` | Texto actual en el input |
| `last_result` | `DataFrame\|None` | Último resultado |
| `last_sql` | `str\|None` | Último SQL generado |
| `last_error` | `str\|None` | Último error |
| `ejecutando` | `bool` | Estado de ejecución |
| `active_tab` | `str` | Pestaña activa |
| `execution_time` | `float\|None` | Tiempo de ejecución en ms |
