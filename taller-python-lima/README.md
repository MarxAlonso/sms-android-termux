# 🏪 Háblale a tu base de datos — Taller Python Lima

Construye tu **primer agente de IA**: una app web donde escribes preguntas en
español (*"¿cuál fue el producto más vendido este mes?"*) y un agente genera el
SQL, lo ejecuta sobre una base de datos real y te responde con tablas y gráficos.

**Stack 100% gratuito:** Python · LangChain · LangGraph · Streamlit · Groq (Llama)

---

## ✅ Antes del taller (hazlo en casa, ~10 min)

Llegar con esto listo es lo que hace que el taller fluya. Por favor hazlo antes.

### 1. Consigue tu API key de Groq (gratis, sin tarjeta)

1. Entra a **https://console.groq.com/keys** e inicia sesión con Google o GitHub.
2. Clic en **"Create API Key"**, ponle un nombre y copia la clave (empieza con `gsk_...`).

> Es gratis, no pide tarjeta y no tienes que crear ningún proyecto. La usaremos con el modelo `llama-3.3-70b-versatile`.

### 2. Clona el repo y prepara el entorno

```bash
git clone <URL-DEL-REPO> taller-python-lima
cd taller-python-lima

# Crea un entorno virtual con Python 3.11 (o 3.10+)
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Pon tu API key

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Abre `.streamlit/secrets.toml` y pega tu key:

```toml
GROQ_API_KEY = "tu-api-key-aqui"
```

### 4. Genera la base de datos y prueba que todo funciona

```bash
python data/generar_db.py     # crea data/bodega.db
python probar_setup.py        # debe terminar en "✅ TODO OK"
```

Si ves **✅ TODO OK**, ya estás listo. Si algo falla, escribe al grupo. 🙌

---

## 🧱 Las 4 etapas del taller

Cada etapa es un archivo independiente. Si te pierdes en una, puedes saltar a la
siguiente y seguir con algo que ya funciona.

| Archivo | Qué aprendes |
|---|---|
| `app_0_hola.py` | Cómo funciona Streamlit (re-ejecución, `session_state`) + conocer la bodega |
| `app_1_chain.py` | El LLM escribe SQL a partir del esquema (sin agente todavía) |
| `app_2_agente.py` | **Un agente de verdad**: tiene herramientas, explora y se corrige solo |
| `app_3_completa.py` | La app final: chat, el SQL visible, tabla, gráfico y seguridad 🔒 |

Cada app se corre así (desde la raíz del proyecto):

```bash
streamlit run app_0_hola.py
# luego app_1_chain.py, app_2_agente.py, app_3_completa.py
```

Se abre solo en tu navegador en `http://localhost:8501`.

---

## 🗄️ La base de datos: una bodega peruana

`data/bodega.db` (SQLite) tiene 4 tablas:

- **productos** — catálogo (Inca Kola, arroz, etc.) con categoría, precio y stock
- **clientes** — nombre, distrito de Lima, fecha de registro
- **ventas** — cabecera de cada venta (cliente, fecha, total)
- **detalle_ventas** — los productos de cada venta (cantidad, subtotal)

Los datos son los mismos para todos (semilla fija). Puedes regenerarlos o
extenderlos editando `data/generar_db.py`.

### Preguntas para probar

- ¿Cuáles son los 5 productos más vendidos?
- ¿Cuánto vendí en total este mes?
- ¿Qué distrito de Lima compra más?
- Top 5 clientes por monto gastado
- Ventas totales por categoría de producto

---

## 🔒 Sobre seguridad

Las apps se conectan a la base de datos en **modo solo lectura**
(`mode=ro`). Aunque le pidas al agente *"borra la tabla ventas"*, SQLite
rechaza cualquier escritura. Es la forma más simple de darle a un agente acceso
a datos sin arriesgarte a que los modifique.

---

## 🚀 Bonus: publica tu app gratis

Con una cuenta de GitHub puedes desplegar tu app en
**[Streamlit Community Cloud](https://streamlit.io/cloud)** y compartir un link
público. Pega tu `GROQ_API_KEY` en *Settings → Secrets* de la app (no subas
`secrets.toml` al repo).

---

## ❓ Problemas comunes

- **`KeyError: 'GROQ_API_KEY'`** → te falta crear `.streamlit/secrets.toml` (paso 3).
- **`No existe data/bodega.db`** → corre `python data/generar_db.py`.
- **Error de cuota / 429** → es el límite del free tier; espera un minuto o usa otra key.
- **La app no abre** → asegúrate de correr `streamlit run ...` desde la carpeta del proyecto.
