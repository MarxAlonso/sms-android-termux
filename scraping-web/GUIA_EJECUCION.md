# 🧪 Guía de Ejecución — Scraping RENACYT

Guía paso a paso para activar el entorno virtual, instalar dependencias y ejecutar el scraping de la base de datos de investigadores RENACYT de CONCYTEC.

---

## 📁 Estructura del proyecto

```
scraping-web/
├── main.py                  # Punto de entrada principal
├── scraper_renacyt.py       # Lógica de scraping (API CONCYTEC)
├── db.py                    # Base de datos SQLite
├── exporters.py             # Exportación a CSV, gráficas y PDF
├── requirements.txt         # Dependencias del proyecto
├── GUIA_EJECUCION.md        # Esta guía
├── .venv/                   # Entorno virtual (ya creado)
├── renacyt.db               # Base de datos local (se genera al scrapear)
└── *.csv / *.png            # Reportes generados
```

---

## 🪟 1. En Windows (PowerShell / CMD)

### 1.1 Entrar a la carpeta del proyecto

```powershell
cd C:\Users\GamingWorld\OneDrive\Desktop\proyecto famat previus\sms-android-termux\scraping-web
```

### 1.2 Activar el entorno virtual

```powershell
.venv\Scripts\activate
```

Sabrás que funcionó porque aparecerá `(.venv)` al inicio de la línea en la terminal.

### 1.3 (Opcional) Instalar/actualizar dependencias

```powershell
pip install -r requirements.txt
```

### 1.4 Ejecutar el scraping completo

```powershell
python main.py
```

Esto hará:
1. Scraping de la API de CONCYTEC (~14,600 registros)
2. Exportación a CSV (completo y limpio)
3. Generación de gráficas (niveles, género, universidades)
4. Generación de PDF profesional

### 1.5 Opciones adicionales

| Comando | Qué hace |
|---|---|
| `python main.py` | Si ya hay datos, los conserva. Si no, scrapea. |
| `python main.py --rescrapear` | Borra la BD existente y vuelve a scrapear **todo desde cero**. |
| `python main.py --solo-reportes` | Solo genera CSV, gráficas y PDF sin volver a scrapear. |

### 1.6 Desactivar el entorno virtual

Cuando termines:

```powershell
deactivate
```

---

## 🪟 1.5 En Git Bash (MINGW64) — Recomendado para Windows

Si estás usando **Git Bash** (como en tu caso), las rutas se escriben con **forward slash `/`**, no con backslash `\`.

### Activar el entorno virtual

```bash
source .venv/Scripts/activate
```

O también:

```bash
. .venv/Scripts/activate
```

Sabrás que funcionó cuando veas `(.venv)` al inicio de la línea.

### Ejecutar el scraping

```bash
python main.py
```

### Desactivar

```bash
deactivate
```

> 💡 **Diferencia clave**: En Git Bash usa SIEMPRE `/` para las rutas, no `\`. El comando `.venv\Scripts\activate` solo funciona en CMD o PowerShell de Windows, no en bash.

---

## 📱 2. En Termux (Android)

### 2.1 Entrar a la carpeta del proyecto

```bash
cd ~/storage/shared/.../scraping-web
# o la ruta donde tengas el proyecto
```

### 2.2 Activar el entorno virtual

```bash
source .venv/bin/activate
```

Sabrás que funcionó porque aparecerá `(.venv)` al inicio de la línea.

### 2.3 (Opcional) Instalar/actualizar dependencias

```bash
pip install -r requirements.txt
```

### 2.4 Ejecutar el scraping

```bash
python main.py
```

### 2.5 Opciones

```bash
python main.py --rescrapear    # Rescrapear desde cero
python main.py --solo-reportes # Solo generar reportes
```

### 2.6 Desactivar

```bash
deactivate
```

---

## 🐧 3. En Linux / macOS (Terminal nativa)

### 3.1 Activar entorno virtual

```bash
cd /ruta/del/proyecto/scraping-web
source .venv/bin/activate
```

### 3.2 Ejecutar

```bash
python main.py
```

### 3.3 Desactivar

```bash
deactivate
```

---

## ⚙️ 4. ¿Qué hace cada archivo?

| Archivo | Función |
|---|---|
| `main.py` | Orquesta todo: decide si scrapear o solo generar reportes |
| `scraper_renacyt.py` | Hace las peticiones HTTP a la API de CONCYTEC, página por página |
| `db.py` | Maneja la base de datos SQLite (crear tablas, insertar, contar) |
| `exporters.py` | Exporta a CSV, genera gráficas (PNG) y PDF profesional |
| `requirements.txt` | Lista de librerías Python necesarias |

---

## 🔧 5. Configuración importante

En `scraper_renacyt.py` puedes ajustar:

```python
TIMEOUT = 300         # Timeout por cada petición (en segundos)
MAX_REINTENTOS = 3     # Reintentos por página si falla
time.sleep(30)         # Pausa entre páginas (en segundos)
```

Si el servidor de CONCYTEC está muy lento, puedes aumentar estos valores.

---

## ❓ 6. Solución de problemas

| Problema | Solución |
|---|---|
| `pip no se reconoce` | Instala Python y asegúrate de que esté en el PATH |
| `.venv` no existe | Crealo con: `python -m venv .venv` |
| Error de timeout | Aumenta `TIMEOUT` en `scraper_renacyt.py` (ya está en 300s) |
| Solo descarga pocas páginas | Verifica conexión a internet, aumenta `TIMEOUT` |
| Error `SSL` / certificados | `pip install --upgrade certifi` |
| `weasyprint` no instala | No es obligatorio. Las gráficas PNG y CSV se generan igual |

---

## 🚀 7. Flujo rápido (resumen)

```bash
# 1. Ir al proyecto
cd scraping-web

# 2. Activar venv
source .venv/bin/activate    # Linux/Mac/Termux
# o
source .venv/Scripts/activate  # Git Bash (Windows)
# o
.venv\Scripts\activate       # PowerShell / CMD (Windows)

# 3. Ejecutar
python main.py

# 4. Salir
deactivate

python main.py --solo-reportes
```
