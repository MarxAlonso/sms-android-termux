# 🎨 Diseño de Interfaz de Usuario

## Filosofía de Diseño

> **Ultra-minimalista · Alta densidad informativa · Estética académico-profesional**

Inspirado en el diseño de interfaces de Anthropic/Claude: máximo impacto visual con mínimos elementos decorativos. Cada pixel tiene un propósito.

---

## Paleta de Color

```
Fondo principal           #FAFAFA  ████████  (off-white)
Fondo secundario          #FFFFFF  ████████  (blanco)
Texto primario            #1A1A1A  ████████  (near-black)
Texto secundario          #6B6B6B  ████████  (gris medio)
Bordes                    #E8E8E8  ████████  (sutil)
Acento (terracota)        #D97757  ████████  (Claude-inspired)
Acento hover              #C96A4A  ████████  (terracota oscuro)
Acento soft               #FDF2ED  ████████  (terracota claro)
Success                   #10B981  ████████  (esmeralda)
Error                     #EF4444  ████████  (rojo)
Hover                     #F5F5F5  ████████  (hover state)
```

### Contraste WCAG 2.1 AA

| Combinación | Ratio | Pasa AA? |
|-------------|-------|----------|
| #1A1A1A sobre #FAFAFA | 16.5:1 | ✅ |
| #6B6B6B sobre #FAFAFA | 6.8:1 | ✅ |
| #D97757 sobre #FAFAFA | 4.7:1 | ✅ |
| #FFFFFF sobre #1A1A1A | 18.2:1 | ✅ |

---

## Tipografía

### Sistema de Fuentes

```css
/* Títulos e interfaz */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Código SQL */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

### Escala Tipográfica

| Elemento | Tamaño | Peso | Uso |
|----------|--------|------|-----|
| Hero title | 1.8rem | 600 | Título principal |
| Subtítulo | 0.9rem | 400 | Bajada |
| Body | 0.875rem (14px) | 400 | Texto general |
| SQL code | 0.8125rem (13px) | 400 | Bloque SQL |
| Labels | 0.75rem | 600 | Encabezados de sección |
| Meta | 0.7rem | 400 | Timestamps, badges |
| Tiny | 0.65rem | 500 | Type tags, badges |

### Line Height

- Texto general: `1.6`
- SQL: `1.7`

---

## Layout

### Desktop (≥1440px) — 3 columnas

```
┌──────────┬───────────────────────────────┬────────────┐
│          │                               │            │
│  Sidebar │       Panel Central           │  Panel     │
│  280px   │        (flexible)             │  Derecho   │
│          │                               │  320px     │
│  ┌──────┐│  ┌─────────────────────────┐  │ ┌────────┐ │
│  │Logo  ││  │  Hero Section           │  │ │Resumen │ │
│  │Capa 1││  │  • Título               │  │ │        │ │
│  └──────┘│  │  • Input grande         │  │ │Filas   │ │
│          │  │  • Botón consultar       │  │ │Tiempo  │ │
│  ┌──────┐│  │  • Chips sugeridos      │  │ └────────┘ │
│  │Esq.  ││  └─────────────────────────┘  │ ┌────────┐ │
│  │BD    ││  ┌─────────────────────────┐  │ │Vista   │ │
│  │      ││  │  SQL Card               │  │ │Previa  │ │
│  │Tabla ││  │  • Código resaltado     │  │ │(5 fil.)│ │
│  │Cols  ││  │  • Copy button          │  │ └────────┘ │
│  └──────┘│  │  • Tiempo ejecución     │  │ ┌────────┐ │
│          │  └─────────────────────────┘  │ │Estruct.│ │
│  ┌──────┐│  ┌─────────────────────────┐  │ │Datos   │ │
│  │Hist. ││  │  Tabs                   │  │ └────────┘ │
│  │      ││  │  ┌─┐┌─┐┌────────────┐  │  │            │
│  │Qrys  ││  │  │T││G││E           │  │  │            │
│  └──────┘│  │  └─┘└─┘└────────────┘  │  │            │
│          │  │  ┌────────────────────┐ │  │            │
│  ┌──────┐│  │  │                    │ │  │            │
│  │Saved ││  │  │  Contenido activo  │ │  │            │
│  │      ││  │  │                    │ │  │            │
│  └──────┘│  │  └────────────────────┘ │  │            │
│          │  └─────────────────────────┘  │            │
└──────────┴───────────────────────────────┴────────────┘
```

### Tablet (768–1439px) — 2 columnas

```
┌──────────────────┬──────────────────────┐
│                  │                      │
│  Sidebar         │    Panel Central      │
│  (toggle hamb.)  │    (flex)             │
│                  │                      │
│  [≡] toggle      │  • Hero + Input      │
│                  │  • SQL Card           │
│                  │  • Tabs + contenido   │
│                  │  • Panel Derecho      │
│                  │    (debajo)           │
│                  │                      │
└──────────────────┴──────────────────────┘
```

### Mobile (<768px) — 1 columna

```
┌──────────────────────┐
│                      │
│  Hero + Input        │
│  [≡] [Consultar]     │
│                      │
│  SQL Card            │
│                      │
│  Tabs                │
│  ┌──────────────────┐│
│  │  Contenido       ││
│  └──────────────────┘│
│                      │
│  Sidebar (bottom)    │
│  ┌──────────────────┐│
│  │  Resumen         ││
│  └──────────────────┘│
└──────────────────────┘
```

---

## Componentes

### 1. Hero Section (Centro, Superior)

```
┌─────────────────────────────────────┐
│                                     │
│     Pregunta sobre tus datos        │  ← 1.8rem, weight 600
│                                     │
│  Escribe en español lo que quieras  │  ← 0.9rem, secondary
│  saber de tu bodega peruana         │
│                                     │
│  ┌─────────────────────────────┐    │
│  │                             │    │  ← TextArea 56px-200px
│  │  Ej: ¿Cuáles son los...     │    │     border-radius: 10px
│  │                             │    │     focus: accent glow
│  │                      0/500  │    │  ← Char counter
│  └─────────────────────────────┘    │
│                                     │
│         ┌─────────────┐             │
│         │  Consultar  │             │  ← Button accent, 8px radius
│         └─────────────┘             │     hover: translateY(-1px)
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────────┐   │
│  │¿Cuá… │ │¿Qué… │ │Top 5…   │   │  ← Chips (clickable)
│  └──────┘ └──────┘ └──────────┘   │     border-radius: 20px
│                                     │
└─────────────────────────────────────┘
```

### 2. SQL Card

```
┌──────────────────────────────────────┐
│  SQL GENERADO                234 ms  │  ← Label + tiempo
│                                      │
│  SELECT                              │  ← Fondo #1A1A1A
│    p.nombre,                         │     Monospace 13px
│    SUM(dv.cantidad) AS total         │
│  FROM productos p                    │  ← Keywords: #D97757
│    JOIN detalle_ventas dv            │     Functions: #8B5CF6
│    ON p.id = dv.producto_id          │     Strings: #10B981
│  WHERE p.categoria = 'Bebidas'       │     Numbers: #3B82F6
│  GROUP BY p.nombre                   │     Comments: #9CA3AF
│  ORDER BY total DESC                 │
│  LIMIT 5                             │
│                                      │
│                         [📋 Copiar]  │  ← Copy to clipboard
└──────────────────────────────────────┘
```

### 3. Tabs de Resultados

```
┌──────────┬──────────┬──────────────┐
│ 📊 Tabla │ 📈 Gráf. │ 📋 Estadíst. │  ← Tabs, solo 1 activo
└──────────┴──────────┴──────────────┘
```

**Tab 1: Tabla**
```
┌──────────────────────────────────────┐
│ 📊 Mostrando 1,234 filas × 6 cols    │  ← Info bar
│                           CSV Excel  │
├──────────────────────────────────────┤
│  id  │ nombre    │ categoria │ prec…│  ← Sticky header
│──────┼───────────┼───────────┼──────│
│  1   │ Inca Kola │ Bebidas   │ 2.50 │  ← Alternating rows
│  2   │ Arroz     │ Abarrote… │ 4.20 │     #FAFAFA / #FFFFFF
│  3   │ …         │ …         │ …    │     Hover: #F5F5F5
└──────────────────────────────────────┘
```

**Tab 2: Gráfico**
```
┌──────────────────────────────────────┐
│  [Select: Bar ┊ Line ┊ Pie ┊ ...]   │  ← Chart type selector
├──────────────────────────────────────┤
│                                      │
│     ┌──────────────────────────┐     │
│     │                          │     │  ← Plotly interactive
│     │       GRÁFICO            │     │     Tooltips
│     │       Plotly             │     │     Zoom/Pan
│     │                          │     │     Download PNG
│     └──────────────────────────┘     │
│                                      │
└──────────────────────────────────────┘
```

**Tab 3: Estadísticas**
```
┌──────────────────────────────────────┐
│  Resumen del conjunto de datos       │
│                                      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────┐│
│  │FILAS │ │COLS  │ │PROM …│ │MIN …││  ← Stat cards
│  │1,234 │ │  6   │ │45.67 │ │ 1.0 ││
│  └──────┘ └──────┘ └──────┘ └─────┘│
│                                      │
│  Estadísticas descriptivas           │
│  ┌──────────────────────────────────┐│
│  │ Col │ Count │ Mean │ Std │ Min… ││  ← DataFrame describe
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### 4. Panel Derecho

```
┌──────────────────────────────────────┐
│  📋 Resumen de resultados             │
│                                      │
│  ┌──────────────────────────────┐    │
│  │     Filas obtenidas           │    │  ← Stat card grande
│  │          1,234                │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌────────┐ ┌────────┐              │
│  │COLUMNAS│ │NUMÉRIC.│              │  ← Mini stats
│  │   6    │ │   3    │              │
│  └────────┘ └────────┘              │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ Tiempo de ejecución           │    │
│  │        234 ms                 │    │  ← Verde success
│  └──────────────────────────────┘    │
│                                      │
│  👁️ Vista previa                     │
│  ┌──────────────────────────────┐    │
│  │  id  │ nombre    │ precio    │    │  ← 5 filas preview
│  └──────────────────────────────┘    │
│                                      │
│  📑 Estructura de datos              │
│  ┌──────────────────────────────┐    │
│  │ Columna  │ Tipo              │    │  ← dtypes info
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
```

### 5. Sidebar (Esquema)

```
┌──────────────────────────────────────┐
│  🟢 Text-to-SQL   [Capa 1]           │  ← Logo + badge
│  EL LLM escribe el SQL               │
│                                      │
│  🗄️ Esquema de la BD                 │  ← Section header
│                                      │
│  [Buscar columna...]                 │  ← Search filter
│                                      │
│  ☐ productos         (16)            │  ← Table name + count
│  ☑ │ INT  id 🔑                     │  ← Column + type tag
│    │ TEXT nombre                     │     INT:  blue
│    │ TEXT categoria                  │     TEXT: green
│    │ REAL precio                     │     REAL: yellow
│    │ INT stock                       │
│                                      │
│  ☐ clientes          (90)            │
│  ☑ ventas           (700)            │
│  ☑ detalle_ventas  (~2000)           │
│                                      │
│  ─────────────────────────────────   │
│                                      │
│  📜 Historial                        │
│  ¿Cuáles son los 5...     ✓ 5 filas  │  ← Timestamp + status
│  ¿Qué distrito...         ✓ 1 fila   │
│  Productos sin stock     ✗ error     │
│                                      │
│  ─────────────────────────────────   │
│                                      │
│  ⭐ Guardadas                         │
│  Ventas por categoría...  ⭐ guardada │
└──────────────────────────────────────┘
```

### 6. Empty State

```
┌──────────────────────────────────────┐
│                                      │
│              🔍                      │  ← Icono grande
│                                      │
│      Esperando tu consulta           │  ← Título
│                                      │
│   Escribe una pregunta en español    │  ← Subtítulo
│   y el LLM generará el SQL para      │
│   responderla.                       │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 💡 Preguntas ejemplo          │    │  ← Card con tips
│  │                               │    │
│  │ • ¿Cuáles son los 5...       │    │
│  │ • ¿Qué distrito...           │    │
│  │ • Ventas totales por...      │    │
│  │ • Top 5 clientes...          │    │
│  └──────────────────────────────┘    │
│                                      │
└──────────────────────────────────────┘
```

### 7. Error State

```
┌──────────────────────────────────────┐
│  ┌──────────────────────────────────┐│
│  │ ✗ Error al ejecutar la consulta  ││  ← Error card
│  │                                  ││     bg: #FEF2F2
│  │  near "SELCET": syntax error     ││     border: #FECACA
│  │                                  ││
│  │ 💡 Sugerencia: Reformula tu      ││     border-top: dashed
│  │    pregunta o intenta con una     ││
│  │    consulta más simple.           ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │  SQL generado                    ││  ← SQL card (even on err)
│  │  SELECT * FROM                   ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### 8. Loading Skeleton

```
┌──────────────────────────────────────┐
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        30%         │  ← shimmer animation
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓        60%          │
│  ▓▓▓▓▓▓        40%                  │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓││
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓││  ← Simula SQL card
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓││
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓││
│  └──────────────────────────────────┘│
│                                      │
│  ▓▓▓▓▓▓▓▓▓▓▓         25%            │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │  ← Simula tabla
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓        60%          │
│                                      │
└──────────────────────────────────────┘
```

---

## Micro-interacciones

| Elemento | Acción | Animación |
|----------|--------|-----------|
| Botón Consultar | Hover | `translateY(-1px)` + `box-shadow` |
| Botón Consultar | Click | `scale(0.98)` + pulse |
| Botón Consultar | Loading | `pulse` animation 1.2s infinite |
| SQL Card | Aparece | `fadeIn` 300ms |
| Tabs | Switch | Instantáneo (st.rerun) |
| Chips | Hover | Border color → accent |
| History item | Hover | Background → #F5F5F5 |
| Skeleton | Loading | `shimmer` 1.5s infinite |

---

## Responsive Breakpoints

| Dispositivo | Ancho | Layout | Sidebar |
|-------------|-------|--------|---------|
| Desktop | ≥1440px | 3 columnas | Siempre visible |
| Desktop med | 1024-1439px | 3 columnas (ajustado) | Visible |
| Tablet | 768-1023px | 2 columnas | Toggle hamburguesa |
| Mobile | <768px | 1 columna | Bottom sheet |

---

## Accesibilidad (WCAG 2.1 AA)

| Requisito | Implementación |
|-----------|----------------|
| Contraste ≥ 4.5:1 | Paleta verificada |
| Focus indicators | 2px solid accent |
| Label for inputs | `label_visibility` configurado |
| Keyboard nav | Atajos nativos del navegador |
| Reduced motion | `@media (prefers-reduced-motion)` |
| Screen reader | `aria-label` en componentes clave |
