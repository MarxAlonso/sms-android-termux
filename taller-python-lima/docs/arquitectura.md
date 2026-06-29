# 🏗️ Arquitectura del Sistema

## Visión General

```
app_1_chain.py  →  Una sola llamada al LLM → SQL → Ejecución → Visualización
```

El flujo es **lineal** (sin agente): el usuario escribe una pregunta en español, el modelo genera SQL, y la app lo ejecuta y muestra resultados.

---

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit (app_1_chain.py)                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │  Sidebar      │  │  Panel Central    │  │  Panel Derecho     │  │
│  │  (280px)      │  │  (flexible)       │  │  (320px)           │  │
│  │               │  │                   │  │                    │  │
│  │  • Esquema    │  │  • Input query    │  │  • Resumen         │  │
│  │  • Historial  │  │  • SQL generado   │  │  • Vista previa    │  │
│  │  • Guardadas  │  │  • Tabs           │  │  • Estructura      │  │
│  │               │  │    (Tabla/Gráfico │  │                    │  │
│  │               │  │     /Estadísticas)│  │                    │  │
│  └──────────────┘  └──────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                      │                       │
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Capa de Datos                              │
│                                                                   │
│  ┌─────────────────────┐  ┌───────────────────────────────────┐  │
│  │  SQLite              │  │  Groq API (Cloud)                 │  │
│  │  data/bodega.db      │  │  llama-3.3-70b-versatile          │  │
│  │  Modo solo lectura   │  │  API Key → secrets.toml           │  │
│  └─────────────────────┘  └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capas del Sistema

### 1. Capa de Presentación (Streamlit)

- **Layout**: Tres columnas responsivas usando `st.columns([3.5, 8, 4])`
- **Estilo**: Paleta monocromática con acento terracota (#D97757), tipografía Inter + JetBrains Mono
- **Componentes**: Divididos en `components/` — 8 módulos especializados
- **Estado**: `st.session_state` para historial, pestañas activas, resultados cacheados, tema

### 2. Capa de Lógica (Python)

| Función | Propósito |
|---------|-----------|
| `get_llm()` | Inicializa ChatGroq (cacheado) |
| `get_schema()` | Obtiene CREATE TABLEs de la BD |
| `get_schema_parsed()` | Estructura JSON para el explorador de esquema |
| `limpiar_sql()` | Elimina bloques ```sql del output del LLM |
| `ejecutar_consulta()` | Ejecuta SQL y mide tiempo |
| `sugerir_grafico()` | Auto-detecta tipo de gráfico |
| `build_stats()` | Genera estadísticas descriptivas |
| `highlight_sql()` | Colorea sintaxis SQL con HTML/CSS |

### 3. Capa de Datos (SQLite)

- Base de datos local: `data/bodega.db`
- Modo solo lectura: `file:data/bodega.db?mode=ro`
- 4 tablas relacionales con datos de bodega peruana

### 4. Capa de IA (Groq + LangChain)

- Modelo: `llama-3.3-70b-versatile`
- Framework: `langchain-groq` (ChatGroq)
- Estrategia: **Chain** (una sola llamada, sin agente)

---

## Flujo de Datos

```
Usuario escribe pregunta
         │
         ▼
Validación (no vacía, ≤500 chars)
         │
         ▼
LLM recibe: PROMPT + esquema + pregunta
         │
         ▼
LLM devuelve: SQL como texto plano
         │
         ▼
Limpiar SQL (quitar ``` si existen)
         │
         ▼
Validar seguridad (solo SELECT)
         │
         ▼
Ejecutar contra SQLite (modo readonly)
         │
         ▼
Mostrar resultados: tabla + gráfico + estadísticas
```

---

## Estructura de Componentes

```
components/
  __init__.py           # Inicialización del paquete
  constants.py          # Colores, fuentes, layout constants, sugerencias
  styles.py             # Generación de CSS dinámico (light/dark)
  icons.py              # 50+ SVG icons inline (Lucide-style)
  schema_explorer.py    # Árbol de esquema de base de datos
  query_history.py      # Historial y consultas guardadas
  hero_input.py         # Hero section + input + chips
  sql_display.py        # SQL card con syntax highlighting
  results_tabs.py       # Tabs: Tabla + Gráfico + Estadísticas
  right_panel.py        # Panel derecho: resumen, preview, estructura
```

Cada componente es una función pura que recibe datos y devuelve HTML/Streamlit.

## Tecnologías

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| Frontend | Streamlit 1.58 | Interfaz web en Python puro |
| Gráficos | Plotly 5.x | Visualización interactiva |
| Datos | Pandas 3.0 | Manipulación y análisis |
| BD | SQLite 3 | Base de datos embebida |
| LLM | Groq API | Inferencia Llama 3.3 70B |
| Orchestrador | LangChain | Conexión LLM unificada |
| SQL Highlight | Regex + spans nativos | Coloreado de sintaxis SQL (sin dependencia extra) |
| Iconos | SVG inline (Lucide-style) | 50+ iconos vectoriales sin emojis |
| Tipografía | Inter + JetBrains Mono | Fuentes del sistema (Google Fonts) |

---

## Decisiones Arquitectónicas

### ¿Por qué un chain y no un agente?
- Simplicidad: una sola llamada al LLM
- Predictibilidad: siempre devuelve SQL
- Esta es la **Capa 1** del taller; las capas siguientes introducen agentes

### ¿Por qué modo readonly?
- Seguridad por defecto: el LLM nunca puede modificar datos
- SQLite rechaza cualquier escritura automáticamente

### ¿Por qué SQLite y no PostgreSQL?
- Zero configuración: no requiere servidor
- Portabilidad: la BD es un solo archivo
- Ideal para talleres y demos

### ¿Por qué componentes separados?
- Mantenibilidad: cada componente vive en su propio archivo
- Reusabilidad: los componentes pueden importarse desde otras apps
- Testing: cada función es testeable de forma aislada
- Colaboración: múltiples personas pueden trabajar en distintos componentes

### ¿Cómo funciona el dark mode?
- CSS se genera dinámicamente con `generate_css(theme)`
- Tema light: `:root` con colores claros + clase `.dark` para overrides
- Tema dark: `:root` con colores oscuros directamente
- El toggle cambia `st.session_state.theme` y fuerza un `st.rerun()`
- El wrapper `<div class="app-wrapper {theme_cls}">` recibe la clase y todas las variables CSS se aplican correctamente
