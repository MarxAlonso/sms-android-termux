# Guía de Ejecución en Termux (Android)

Esta guía te ayudará a poner en marcha el proyecto **SMS Gateway** directamente en tu celular usando Termux.

## 1. Requisitos Previos

Asegúrate de tener instalada la aplicación **Termux:API** desde la Play Store o F-Droid, y luego instala el paquete dentro de Termux:

```bash
pkg update && pkg upgrade
pkg install termux-api python redis
```

## 2. Clonar e Ingresar al Proyecto

Si ya tienes el repositorio:

```bash
cd sms-android-termux/sms-gateway-android
```

## 3. Configurar el Entorno Virtual (venv)

Es recomendable usar un entorno virtual para no ensuciar los paquetes globales:

```bash
# Crear el entorno
python -m venv venv

# Activar el entorno
source venv/bin/activate
```

*(Sabrás que está activo porque aparecerá `(venv)` al inicio de tu línea de comandos).*

## 4. Instalar Dependencias

Instala los paquetes necesarios desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 5. Iniciar Redis

La aplicación usa Redis para manejar eventos y caché. Asegúrate de que esté corriendo:

```bash
redis-server --daemonize yes
```

## 6. Ejecutar el Servidor

Para iniciar la aplicación Starlite, usa `uvicorn`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 7. Probar el Envío de SMS (curl)

Abre otra sesión de Termux (desliza desde la izquierda y pulsa "New Session") y ejecuta uno de estos comandos:

### Opción A: Usando el nuevo endpoint de Gateway (Recomendado)
Este comando enviará el SMS y notificará automáticamente a tu backend en Railway.

```bash
curl -X POST http://localhost:8000/test/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+51999888777",
    "message": "Hola, esto es una prueba desde el SMS Gateway en Termux",
    "tenant_id": "demo-001"
  }'
```

### Opción B: Endpoint básico (Legacy)
```bash
curl -X POST http://localhost:8000/send-sms \
  -H "Content-Type: application/json" \
  -d '{"number": "+51999888777", "message": "Prueba simple"}'
```

---

## Solución de Problemas

- **Error de permisos**: Si el SMS no se envía, asegúrate de que le diste permiso de "SMS" a la aplicación **Termux:API** en los ajustes de Android.
- **Redis Connection Error**: Verifica que Redis esté corriendo con `ps aux | grep redis`.
- **Httpx Error**: Si el celular no tiene internet, el envío del webhook al backend de Railway fallará, pero el SMS se enviará localmente de todos modos.
