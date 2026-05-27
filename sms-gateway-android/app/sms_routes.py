from starlite import Router, post, get, Provide

from app.services import MessageService, TERMUX_SMS_API
from app.sms_gateway import SMSGatewayService
from app.utils import Termux
from app.whatsapp_gateway import WhatsAppGatewayService
from app.whatsapp_service import WhatsAppService


async def get_sms_gateway_service() -> SMSGatewayService:
    termux = Termux.create(TERMUX_SMS_API)
    message_service = MessageService.create(termux, TERMUX_SMS_API)
    return SMSGatewayService(message_service)


async def get_whatsapp_gateway_service() -> WhatsAppGatewayService:
    whatsapp_service = WhatsAppService()
    return WhatsAppGatewayService(whatsapp_service)


@post("/send-sms")
async def send_sms_legacy(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    payload = {"to": data.get("number"), "message": data.get("message")}
    return await sms_gateway_service.send_sms_gateway(payload)


@post("/test/sms/send")
async def send_sms_test(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.send_sms_gateway(data)


@post("/test/wsp/send")
async def send_wsp_test(data: dict, whatsapp_gateway_service: WhatsAppGatewayService) -> dict:
    return await whatsapp_gateway_service.send_whatsapp_gateway(data)


@post("/test/webhooks/sms-gateway")
async def receive_webhook(data: dict, sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.handle_webhook(data)


@post("/sync/sms")
async def sync_sms_post(sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.sync_with_backend()


@get("/sync/sms")
async def sync_sms_get(sms_gateway_service: SMSGatewayService) -> dict:
    return await sms_gateway_service.sync_with_backend()


@post("/sync/wsp")
async def sync_wsp_post(whatsapp_gateway_service: WhatsAppGatewayService) -> dict:
    return await whatsapp_gateway_service.sync_with_backend()


@get("/sync/wsp")
async def sync_wsp_get(whatsapp_gateway_service: WhatsAppGatewayService) -> dict:
    return await whatsapp_gateway_service.sync_with_backend()


@post("/sync")
async def sync_legacy_post(
    sms_gateway_service: SMSGatewayService,
    whatsapp_gateway_service: WhatsAppGatewayService,
) -> dict:
    sms_result = await sms_gateway_service.sync_with_backend()
    wsp_result = await whatsapp_gateway_service.sync_with_backend()
    return {"deprecated": True, "sms": sms_result, "wsp": wsp_result}


@get("/sync")
async def sync_legacy_get(
    sms_gateway_service: SMSGatewayService,
    whatsapp_gateway_service: WhatsAppGatewayService,
) -> dict:
    sms_result = await sms_gateway_service.sync_with_backend()
    wsp_result = await whatsapp_gateway_service.sync_with_backend()
    return {"deprecated": True, "sms": sms_result, "wsp": wsp_result}


sms_router = Router(
    path="",
    route_handlers=[
        send_sms_legacy,
        send_sms_test,
        send_wsp_test,
        receive_webhook,
        sync_sms_post,
        sync_sms_get,
        sync_wsp_post,
        sync_wsp_get,
        sync_legacy_post,
        sync_legacy_get,
    ],
    dependencies={
        "sms_gateway_service": Provide(get_sms_gateway_service),
        "whatsapp_gateway_service": Provide(get_whatsapp_gateway_service),
    },
)
