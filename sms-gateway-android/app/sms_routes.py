from starlite import Router, post, get, Response, Provide
from app.sms_gateway import SMSGatewayService
from app.services import MessageService, TERMUX_SMS_API
from app.utils import Termux

async def get_sms_gateway_service() -> SMSGatewayService:
    termux = Termux.create(TERMUX_SMS_API)
    message_service = MessageService.create(termux, TERMUX_SMS_API)
    return SMSGatewayService(message_service)

@post("/send-sms")
async def send_sms_legacy(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    # Mapear formato antiguo al nuevo si es necesario
    payload = {
        "to": data.get("number"),
        "message": data.get("message")
    }
    return await sms_gateway_service.send_sms_gateway(payload)

@post("/test/sms/send")
async def send_sms_test(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.send_sms_gateway(data)

@post("/test/webhooks/sms-gateway")
async def receive_webhook(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.handle_webhook(data)

@post("/sync")
@get("/sync")
async def sync_with_backend_route(sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.sync_with_backend()

sms_router = Router(
    path="",
    route_handlers=[send_sms_legacy, send_sms_test, receive_webhook, sync_with_backend_route],
    dependencies={"sms_gateway_service": Provide(get_sms_gateway_service)}
)
