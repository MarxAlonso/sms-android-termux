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
        self._access_token: Optional[str] = None

    async def login(self) -> str:
        """Autentica con el backend y obtiene el token JWT"""
        login_url = f"{settings.backend_url}/auth/jwt/login"
        data = {
            "username": settings.admin_email,
            "password": settings.admin_password
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(login_url, data=data, timeout=10.0)
                if response.status_code == 200:
                    token_data = response.json()
                    self._access_token = token_data.get("access_token")
                    logger.info("Login exitoso en el backend")
                    return self._access_token
                else:
                    logger.error(f"Error en login: {response.status_code} - {response.text}")
                    raise Exception(f"Login failed: {response.text}")
        except Exception as e:
            logger.error(f"Excepción durante login: {e}")
            raise

    async def fetch_pending_sms(self) -> list:
        """Obtiene la lista de SMS pendientes del backend"""
        if not self._access_token:
            await self.login()
            
        pending_url = f"{settings.backend_url}/test/sms/pending"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(pending_url, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    return response.json()  # Asumimos que devuelve una lista
                elif response.status_code == 401:
                    # Token expirado, intentar login de nuevo
                    await self.login()
                    headers = {"Authorization": f"Bearer {self._access_token}"}
                    response = await client.get(pending_url, headers=headers, timeout=10.0)
                    return response.json()
                else:
                    logger.error(f"Error al obtener SMS pendientes: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Excepción al obtener SMS pendientes: {e}")
            return []

    async def sync_with_backend(self) -> Dict[str, Any]:
        """Sincroniza con el backend: descarga y envía mensajes pendientes"""
        logger.info("Iniciando sincronización con el backend...")
        pending_messages = await self.fetch_pending_sms()
        
        if not pending_messages:
            logger.info("No hay mensajes pendientes.")
            return {"status": "success", "processed": 0}

        if isinstance(pending_messages, str):
            # A veces el backend devuelve strings si no hay nada o hay error
            logger.info(f"Respuesta del backend: {pending_messages}")
            return {"status": "success", "processed": 0, "message": pending_messages}

        logger.info(f"Sincronización: Se recibieron {len(pending_messages)} elementos del backend.")
        
        results = []
        for i, msg_data in enumerate(pending_messages):
            # Validar que sea un diccionario antes de procesar
            if not isinstance(msg_data, dict):
                logger.warning(f"Elemento {i} ignorado: no es un diccionario. Valor: {msg_data} (tipo: {type(msg_data)})")
                continue
                
            # El formato esperado es {"to": "...", "message": "...", "tenant_id": "..."}
            res = await self.send_sms_gateway(msg_data)
            results.append(res)
            
        logger.info(f"Sincronización completada. Procesados: {len(results)}")
        return {
            "status": "success",
            "processed": len(results),
            "results": results
        }


    async def send_sms_gateway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            logger.error(f"send_sms_gateway recibió un tipo inválido: {type(data)}. Valor: {data}")
            return {"status": "failed", "detail": "Datos de entrada deben ser un diccionario"}

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
