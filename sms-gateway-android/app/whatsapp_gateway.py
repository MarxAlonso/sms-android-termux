import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import starlite

from app.config import settings
from app.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class WhatsAppGatewayService:
    def __init__(self, whatsapp_service: WhatsAppService):
        self.whatsapp_service = whatsapp_service
        self._access_token: Optional[str] = None

    async def login(self) -> str:
        login_url = f"{settings.backend_url}/auth/jwt/login-2fa"
        data = {"username": settings.admin_email, "password": settings.admin_password}

        async with httpx.AsyncClient() as client:
            response = await client.post(login_url, data=data, timeout=10.0)
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                logger.info("Login exitoso en el backend")
                return self._access_token

            logger.error(f"Error en login: {response.status_code} - {response.text}")
            raise Exception(f"Login failed: {response.text}")

    async def fetch_pending_messages(self, path: str) -> list:
        if not self._access_token:
            await self.login()

        pending_url = f"{settings.backend_url}{path}"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(pending_url, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401:
                    await self.login()
                    headers = {"Authorization": f"Bearer {self._access_token}"}
                    response = await client.get(pending_url, headers=headers, timeout=10.0)
                    return response.json()

                logger.error(
                    f"Error al obtener mensajes pendientes de {path}: {response.status_code}"
                )
                return []
        except Exception as exc:
            logger.error(f"Excepción al obtener mensajes de {path}: {exc}")
            return []

    @staticmethod
    def _extract_items(data: Any) -> list:
        if isinstance(data, dict):
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []

    async def sync_with_backend(self) -> Dict[str, Any]:
        logger.info("Iniciando sincronización WSP con el backend...")

        pending_wsp = await self.fetch_pending_messages(settings.resolved_pending_wsp_path)
        messages_list = self._extract_items(pending_wsp)

        if not messages_list:
            logger.info("No hay mensajes WSP pendientes.")
            return {"status": "success", "queued": 0, "total_in_queue": 0}

        normalized_messages = []
        for i, msg_data in enumerate(messages_list):
            if not isinstance(msg_data, dict):
                logger.warning(
                    f"Elemento {i} ignorado: no es un diccionario de mensaje. Valor: {msg_data}"
                )
                continue

            normalized = {
                "to": msg_data.get("numero") or msg_data.get("to"),
                "message": msg_data.get("mensaje") or msg_data.get("message"),
                "tenant_id": str(msg_data.get("institucion_id", "default")),
                "delivery_job_id": msg_data.get("delivery_job_id"),
            }

            if not normalized["to"] or not normalized["message"]:
                logger.warning(
                    f"Elemento {i} ignorado: faltan campos 'numero' o 'mensaje'. Datos: {msg_data}"
                )
                continue

            normalized_messages.append(normalized)

        if not normalized_messages:
            return {"status": "success", "queued": 0, "total_in_queue": 0}

        from app.whatsapp_queue import queue_messages, count_queued

        queued_count = queue_messages(normalized_messages)
        total = count_queued()

        logger.info(
            f"{queued_count} mensajes WSP encolados en SQLite. Total en cola: {total}"
        )

        return {
            "status": "success",
            "queued": queued_count,
            "total_in_queue": total,
            "detail": (
                f"{queued_count} mensajes de WhatsApp encolados. "
                "Ejecuta 'python -m app.process_whatsapp_queue' "
                "para procesarlos uno por uno."
            ),
        }

    async def send_whatsapp_gateway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            logger.error(
                f"send_whatsapp_gateway recibió un tipo inválido: {type(data)}. Valor: {data}"
            )
            return {
                "status": "failed",
                "detail": "Datos de entrada deben ser un diccionario",
            }

        to = data.get("to")
        message = data.get("message")
        tenant_id = data.get("tenant_id", "default")

        if not to or not message:
            raise starlite.HTTPException(
                status_code=400, detail="to y message son obligatorios"
            )

        message_id = f"gw-{uuid.uuid4().hex[:8]}"

        try:
            await self.whatsapp_service.send(to, message)

            response_data = {
                "detail": "WSP encolado en whatsapp gateway",
                "status": "success",
                "provider": "whatsapp-gateway",
                "destination": to,
                "channel": "whatsapp",
                "tenant_id": tenant_id,
                "message_id": message_id,
            }

            delivery_job_id = data.get("delivery_job_id")
            await self._mark_as_sent(delivery_job_id)
            await self._send_callback(delivery_job_id, "sent", "DELIVERED")
            return response_data

        except Exception as exc:
            error_msg = str(exc)
            delivery_job_id = data.get("delivery_job_id")
            await self._send_callback(
                delivery_job_id,
                "failed",
                "DISPATCH_ERROR",
                error_message=error_msg,
            )

            return {
                "detail": "Error al enviar WSP",
                "status": "failed",
                "provider": "whatsapp-gateway",
                "error": error_msg,
                "message_id": message_id,
            }

    async def _send_callback(
        self,
        delivery_job_id: Optional[int],
        status: str,
        reason_code: str,
        error_message: Optional[str] = None,
    ):
        if not delivery_job_id:
            logger.debug("No delivery_job_id available for callback.")
            return

        callback_url = f"{settings.backend_url}{settings.resolved_pending_wsp_path}/{delivery_job_id}/estado"
        payload = {
            "estado": status,
            "reason_code": reason_code,
            "detail": error_message or "Procesado por WhatsApp Gateway Android",
            "occurred_at": datetime.utcnow().isoformat() + "Z",
        }

        if not self._access_token:
            try:
                await self.login()
            except Exception:
                return

        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    callback_url, json=payload, headers=headers, timeout=5.0
                )
                if response.status_code == 401:
                    await self.login()
                    headers = {"Authorization": f"Bearer {self._access_token}"}
                    response = await client.patch(
                        callback_url, json=payload, headers=headers, timeout=5.0
                    )
                logger.info(f"PATCH {callback_url} -> {response.status_code}")
        except Exception as exc:
            logger.error(f"Error en PATCH callback: {exc}")

    async def _mark_as_sent(self, delivery_job_id: Optional[int]):
        if not delivery_job_id:
            logger.debug("No delivery_job_id available for marcar-enviado.")
            return

        callback_url = (
            f"{settings.backend_url}{settings.resolved_pending_wsp_path}/"
            f"{delivery_job_id}/marcar-enviado"
        )

        if not self._access_token:
            try:
                await self.login()
            except Exception:
                return

        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(callback_url, headers=headers, timeout=5.0)
                if response.status_code == 401:
                    await self.login()
                    headers = {"Authorization": f"Bearer {self._access_token}"}
                    response = await client.post(
                        callback_url, headers=headers, timeout=5.0
                    )
                logger.info(f"POST {callback_url} -> {response.status_code}")
        except Exception as exc:
            logger.error(f"Error en POST marcar-enviado: {exc}")
