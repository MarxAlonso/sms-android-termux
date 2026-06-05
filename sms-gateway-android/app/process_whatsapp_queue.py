import asyncio
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from app.whatsapp_queue import (
    get_next_message,
    delete_message,
    count_queued,
    init_db,
)
from app.whatsapp_service import WhatsAppService
from app.whatsapp_gateway import WhatsAppGatewayService


async def process_queue():
    init_db()

    whatsapp_service = WhatsAppService()
    gateway = WhatsAppGatewayService(whatsapp_service)

    total = count_queued()
    if total == 0:
        print("No hay mensajes en la cola de WhatsApp.")
        print("Ejecuta 'curl http://127.0.0.1/sync/wsp' primero para encolar mensajes.")
        return

    print()
    print("=" * 60)
    print(f"  Cola de WhatsApp: {total} mensajes pendientes")
    print("=" * 60)
    print()

    processed = 0
    loop = asyncio.get_event_loop()

    while True:
        msg = get_next_message()
        if not msg:
            break

        remaining = count_queued()
        print(f"[{processed + 1}/{total}] Enviando a: {msg['to_number']}")
        print(f"  Mensaje: {msg['message'][:120]}")

        try:
            await whatsapp_service.send(msg["to_number"], msg["message"])
        except Exception as e:
            print(f"  ERROR al abrir WhatsApp: {e}")
            respuesta = await loop.run_in_executor(
                None, input, "  ¿Reintentar? (si/no): "
            )
            if respuesta.strip().lower() in ("si", "s", "yes", "y"):
                continue
            else:
                skip = await loop.run_in_executor(
                    None, input, "  ¿Saltar este mensaje? (si/no): "
                )
                if skip.strip().lower() in ("si", "s", "yes", "y"):
                    delete_message(msg["id"])
                    processed += 1
                    print(f"  Mensaje {msg['id']} saltado.\n")
                    continue
                else:
                    continue

        print("  WhatsApp abierto. Envía el mensaje manualmente.")
        print()

        while True:
            respuesta = await loop.run_in_executor(
                None,
                input,
                "  ¿Ya enviaste el mensaje? (si/no): ",
            )
            respuesta = respuesta.strip().lower()

            if respuesta in ("si", "s", "yes", "y"):
                delivery_job_id = msg.get("delivery_job_id")
                if delivery_job_id:
                    try:
                        await gateway._mark_as_sent(delivery_job_id)
                        await gateway._send_callback(
                            delivery_job_id, "sent", "DELIVERED"
                        )
                        print("  Notificación al backend exitosa.")
                    except Exception as e:
                        print(f"  Error al notificar al backend: {e}")

                delete_message(msg["id"])
                processed += 1
                remaining = count_queued()
                print(f"  Mensaje enviado correctamente. {remaining} restantes.\n")
                break

            elif respuesta in ("no", "n"):
                print("  Revisa WhatsApp y envía el mensaje.")
                print("  Escribe 'si' cuando lo hayas enviado.\n")
                continue

            else:
                print("  Responde 'si' o 'no'.\n")

    print("=" * 60)
    print(f"  Procesados: {processed} mensajes")
    if processed == total:
        print("  ¡Todos los mensajes fueron enviados correctamente!")
    print("=" * 60)


def main():
    try:
        asyncio.run(process_queue())
    except KeyboardInterrupt:
        remaining = count_queued()
        print(f"\n\nProceso interrumpido. {remaining} mensajes restantes en la cola.")
        print("Puedes reanudar ejecutando 'python -m app.process_whatsapp_queue'")
        sys.exit(0)


if __name__ == "__main__":
    main()
