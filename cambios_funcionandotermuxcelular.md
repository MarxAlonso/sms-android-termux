Lo que se ha cambiado
from starlite import Starlite
from app.sms_routes import sms_router
from app import events, routes

def create_app() -> Starlite:
    app = Starlite(
        route_handlers=[routes.router, sms_router],
        on_startup=[events.create_redis_conn],
        on_shutdown=[events.destroy_redis_conn],
    )
    return app

app = create_app()


# sms_routes.py
import subprocess
from starlite import Router, post, Response

# Definir la ruta como función decorada
@post("/send-sms")
async def send_sms(data: dict) -> Response:
    number = data.get("number")
    message = data.get("message")

    if not number or not message:
        return Response({"error": "number y message son obligatorios"}, status_code=400)

    try:
        subprocess.run(["termux-sms-send", "-n", number, message], check=True)
        return {"status": "success", "number": number, "message": message}
    except subprocess.CalledProcessError as e:
        return Response({"error": str(e)}, status_code=500)

# Crear el router, especificando path
sms_router = Router(path="", route_handlers=[send_sms])
~ esto era lo que se cambio, funcionaba de manera local cuando incluias el api de termux para mandar mensajes por celular, ahora yo quiero enviar mensajes tomando el api de un backend 

ndpoints de prueba SMS Gateway
Nota de transición: flujo /test usa sms gateway, no Twilio.

POST /test/sms/send
Contrato de request (JSON):

{
  "to": "+51999999999",
  "message": "Recordatorio de pago",
  "channel": "sms",
  "tenant_id": "tenant-demo",
  "metadata": {
    "campaign": "recordatorio-cuota"
  }
}
Campos requeridos:

to (string): destino del SMS.
message (string): contenido a enviar.
Respuesta exitosa (200):

{
  "detail": "SMS encolado en sms gateway",
  "status": "success",
  "provider": "sms-gateway",
  "destination": "+51999999999",
  "channel": "sms",
  "tenant_id": "tenant-demo"
}
POST /test/webhooks/sms-gateway
Contrato de request (JSON):

{
  "message_id": "gw-9f3e0c0a",
  "status": "delivered",
  "to": "+51999999999",
  "error_code": null,
  "error_message": null,
  "occurred_at": "2026-04-24T10:15:20Z",
  "raw": {
    "provider": "sms-gateway",
    "attempt": 1
  }
}
Campos requeridos:

message_id (string): identificador entregado por el gateway.
status (string): estado del delivery.
Respuesta exitosa (200):

{
  "detail": "Webhook sms gateway recibido",
  "status": "success",
  "provider": "sms-gateway",
  "message_id": "gw-9f3e0c0a",
  "status_gateway": "delivered"
}
Ejemplos de payload de callback del gateway:

{
  "message_id": "gw-9f3e0c0a",
  "status": "sent",
  "to": "+51999999999",
  "occurred_at": "2026-04-24T10:14:20Z"
}
{
  "message_id": "gw-9f3e0c0a",
  "status": "failed",
  "to": "+51999999999",
  "error_code": "30007",
  "error_message": "Carrier violation",
  "occurred_at": "2026-04-24T10:16:20Z"
}, 