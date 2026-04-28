import uuid
import httpx
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import starlite
from app.services import MessageService
from app.config import settings

logger = logging.getLogger(__name__)

class SMSGatewayService:
    def __init__(self, message_service: MessageService):
        self.message_service = message_service

    async def send_sms_gateway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        to = data.get("to")
        message = data.get("message")
        tenant_id = data.get("tenant_id", "default")
        channel = data.get("channel", "sms")

        if not to or not message:
            raise starlite.HTTPException(status_code=400, detail="to y message son obligatorios")

        message_id = f"gw-{uuid.uuid4().hex[:8]}"

        try:
            # 1. Enviar el SMS usando Termux
            await self.message_service.send(to, message)
            
            response_data = {
                "detail": "SMS encolado en sms gateway",
                "status": "success",
                "provider": "sms-gateway",
                "destination": to,
                "channel": channel,
                "tenant_id": tenant_id,
                "message_id": message_id
            }

            # 2. Enviar Webhook de éxito al backend de Railway de forma asíncrona
            await self._send_callback(message_id, "delivered", to)
            
            return response_data

        except Exception as e:
            error_msg = str(e)
            # Enviar Webhook de fallo si algo sale mal
            await self._send_callback(message_id, "failed", to, error_message=error_msg)
            
            return {
                "detail": "Error al enviar SMS",
                "status": "failed",
                "provider": "sms-gateway",
                "error": error_msg,
                "message_id": message_id
            }

    async def _send_callback(self, message_id: str, status: str, to: str, error_message: Optional[str] = None):
        """Envía el estado del mensaje al backend de Railway"""
        callback_url = f"{settings.backend_url}/test/webhooks/sms-gateway"
        
        payload = {
            "message_id": message_id,
            "status": status,
            "to": to,
            "error_code": "500" if status == "failed" else None,
            "error_message": error_message,
            "occurred_at": datetime.utcnow().isoformat() + "Z",
            "raw": {
                "provider": "sms-gateway",
                "attempt": 1
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(callback_url, json=payload, timeout=5.0)
                logger.info(f"Callback enviado a {callback_url} para {message_id}")
        except Exception as e:
            logger.error(f"Error al enviar callback a {callback_url}: {e}")

    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        message_id = data.get("message_id")
        status = data.get("status")

        return {
            "detail": "Webhook sms gateway recibido",
            "status": "success",
            "provider": "sms-gateway",
            "message_id": message_id,
            "status_gateway": status
        }
