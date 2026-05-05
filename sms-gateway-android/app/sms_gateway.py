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
            
        pending_url = f"{settings.backend_url}{settings.pending_sms_path}"
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
            return {"status": "success", "processed": 0, "results": []}

        if isinstance(pending_messages, str):
            # A veces el backend devuelve strings si no hay nada o hay error
            logger.info(f"Respuesta del backend: {pending_messages}")
            return {"status": "success", "processed": 0, "results": [], "message": pending_messages}

        # Determinar la lista de mensajes a procesar
        messages_list = []
        if isinstance(pending_messages, dict):
            # Si es un diccionario, buscamos los mensajes en la clave 'items'
            messages_list = pending_messages.get("items", [])
            logger.info(f"El backend devolvió un diccionario. Extrayendo {len(messages_list)} mensajes de 'items'.")
        elif isinstance(pending_messages, list):
            messages_list = pending_messages
            logger.info(f"El backend devolvió una lista directa de {len(messages_list)} mensajes.")
        else:
            logger.warning(f"Formato de respuesta inesperado: {type(pending_messages)}")
            return {"status": "error", "detail": f"Unexpected response type: {type(pending_messages)}"}

        results = []
        for i, msg_data in enumerate(messages_list):
            # Validar que sea un diccionario antes de procesar
            if not isinstance(msg_data, dict):
                logger.warning(f"Elemento {i} ignorado: no es un diccionario de mensaje. Valor: {msg_data}")
                continue

            # Mapear el nuevo formato del backend al formato interno:
            # {"numero": "...", "mensaje": "..."} → {"to": "...", "message": "..."}
            normalized = {
                "to": msg_data.get("numero") or msg_data.get("to"),
                "message": msg_data.get("mensaje") or msg_data.get("message"),
                "tenant_id": str(msg_data.get("institucion_id", "default")),
                "channel": msg_data.get("tipo_envio", "sms"),
                "delivery_job_id": msg_data.get("delivery_job_id"),
                "historial_evento_id": msg_data.get("historial_evento_id"),
            }

            if not normalized["to"] or not normalized["message"]:
                logger.warning(f"Elemento {i} ignorado: faltan campos 'numero' o 'mensaje'. Datos: {msg_data}")
                continue

            logger.info(f"Enviando SMS a {normalized['to']} (job: {normalized.get('delivery_job_id')})")
            res = await self.send_sms_gateway(normalized)
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

            # 2. Enviar actualización al backend usando PATCH
            delivery_job_id = data.get("delivery_job_id")
            await self._send_callback(delivery_job_id, "sent", "DELIVERED")
            
            return response_data

        except Exception as e:
            error_msg = str(e)
            # Enviar actualización de fallo
            delivery_job_id = data.get("delivery_job_id")
            await self._send_callback(delivery_job_id, "failed", "DISPATCH_ERROR", error_message=error_msg)
            
            return {
                "detail": "Error al enviar SMS",
                "status": "failed",
                "provider": "sms-gateway",
                "error": error_msg,
                "message_id": message_id
            }

    async def _send_callback(self, delivery_job_id: Optional[int], status: str, reason_code: str, error_message: Optional[str] = None):
        """Actualiza el estado del mensaje en el backend usando PATCH"""
        if not delivery_job_id:
            logger.debug("No delivery_job_id available for callback.")
            return

        callback_url = f"{settings.backend_url}/calendario/delivery-jobs/sms-pendientes/{delivery_job_id}/estado"
        
        payload = {
            "estado": status,
            "reason_code": reason_code,
            "detail": error_message or "Procesado por SMS Gateway Android",
            "occurred_at": datetime.utcnow().isoformat() + "Z"
        }

        if not self._access_token:
            try:
                await self.login()
            except:
                return

        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(callback_url, json=payload, headers=headers, timeout=5.0)
                logger.info(f"PATCH {callback_url} -> {response.status_code}")
        except Exception as e:
            logger.error(f"Error en PATCH callback: {e}")

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
