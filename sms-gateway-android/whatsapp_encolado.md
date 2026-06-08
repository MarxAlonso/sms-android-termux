# WhatsApp Encolado - Procesamiento Manual

## Descripción

Cuando el servidor SMS recibe mensajes de WhatsApp entrantes, estos se guardan en una cola SQLite (`whatsapp_queue.db`) en lugar de enviarse automáticamente. Esto es porque Termux **no puede abrir WhatsApp automáticamente** desde el backend; necesita intervención manual.

Cada mensaje en cola requiere que un humano abra WhatsApp Web/App desde el dispositivo y confirme el envío.

---

## Arquitectura: Dos Sesiones

Necesitas **dos sesiones de terminal separadas** (pestañas de Termux):

| Sesión | Proceso | Comando |
|--------|---------|---------|
| **Sesión 1** | Servidor HTTP (siempre corriendo) | `uvicorn app.main:app` |
| **Sesión 2** | Procesador de cola WhatsApp (bajo demanda) | `python app/process_whatsapp_queue.py` |

Ambos procesos comparten la misma base de datos SQLite (`whatsapp_queue.db`).

---

## Paso a Paso

### 1. Sesión 1 — Iniciar el servidor

Abre Termux, activa el entorno virtual y ejecuta el servidor:

```bash
cd ~/pruebas/sms-android-termux/sms-gateway-android
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Déjalo corriendo. Los mensajes entrantes se encolan aquí.

Para verificar que se están encolando, desde otro terminal puedes hacer:

```bash
curl -X POST http://127.0.0.1:8000/sync
```

Ejemplo de respuesta exitosa:

```json
{
  "sms": {...},
  "wsp": {
    "status": "success",
    "queued": 9,
    "total_in_queue": 9,
    "detail": "9 mensajes de WhatsApp encolados. Ejecuta 'python -m app.process_whatsapp_queue' para procesarlos uno por uno."
  }
}
```

### 2. Sesión 2 — Procesar la cola de WhatsApp

Abre una **nueva pestaña/ventana de Termux** (no cierres el servidor). Ejecuta:

```bash
cd ~/pruebas/sms-android-termux/sms-gateway-android
source venv/bin/activate
python app/process_whatsapp_queue.py
```

O también funciona:

```bash
PYTHONPATH=. python -m app.process_whatsapp_queue
```

### 3. Flujo interactivo

El script te guiará paso a paso:

```
============================================================
  Cola de WhatsApp: 9 mensajes pendientes
============================================================

[1/9] Enviando a: +51987654321
  Mensaje: Hola, tu código de verificación es 123456...

  WhatsApp abierto. Envía el mensaje manualmente.

  ¿Ya enviaste el mensaje? (si/no):
```

1. El script abre WhatsApp automáticamente mediante `termux-open-url` con el enlace `wa.me`.
2. **Tú debes** tocar "Enviar" manualmente en la pantalla de WhatsApp.
3. Vuelve al terminal y responde `si` cuando hayas confirmado el envío.
4. El script registra el envío en el backend y elimina el mensaje de la cola.
5. Pasa al siguiente mensaje automáticamente.

Si no se abre WhatsApp, responde `no` y el script te preguntará si quieres reintentar o saltar el mensaje.

---

## Comandos útiles

```bash
# Ver cantidad de mensajes en cola (sin procesarlos)
python -c "import sqlite3; conn=sqlite3.connect('whatsapp_queue.db'); print(conn.execute('SELECT COUNT(*) FROM whatsapp_queue').fetchone()[0])"

# Ver todos los mensajes encolados
python -c "import sqlite3,json; conn=sqlite3.connect('whatsapp_queue.db'); print(json.dumps([dict(r) for r in conn.execute('SELECT * FROM whatsapp_queue').fetchall()], indent=2))"

# Vaciar la cola (borrar todos los mensajes)
python -c "import sqlite3; conn=sqlite3.connect('whatsapp_queue.db'); conn.execute('DELETE FROM whatsapp_queue'); conn.commit(); print('Cola vaciada')"
```

---

## Notas importantes

- **No cierres el servidor (Sesión 1)** mientras procesas la cola.
- Si interrumpes el procesador (`Ctrl+C`), los mensajes no eliminados quedan en la cola y puedes reanudar después.
- El procesador solo funciona en Termux (usa `termux-open-url` para abrir WhatsApp).
- Para enviar lote completo sin interrupción: responde `si` a cada mensaje después de enviarlo manualmente.
