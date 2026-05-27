from unittest.mock import AsyncMock

import pytest

from app.sms_gateway import SMSGatewayService
from app.whatsapp_gateway import WhatsAppGatewayService
from app.whatsapp_service import WhatsAppService


@pytest.mark.asyncio
async def test_sms_gateway_does_not_use_whatsapp_flow(monkeypatch):
    message_service = AsyncMock()
    gateway = SMSGatewayService(message_service)

    callback_mock = AsyncMock()
    monkeypatch.setattr(gateway, "_send_callback", callback_mock)

    data = {"to": "+51911122233", "message": "hola", "delivery_job_id": 123}
    res = await gateway.send_sms_gateway(data)

    message_service.send.assert_awaited_once_with("+51911122233", "hola")
    assert not hasattr(message_service, "send_whatsapp") or message_service.send_whatsapp.await_count == 0
    callback_mock.assert_awaited_once()
    assert res["status"] == "success"
    assert res["channel"] == "sms"


@pytest.mark.asyncio
async def test_whatsapp_gateway_uses_whatsapp_service(monkeypatch):
    wsp_service = AsyncMock(spec=WhatsAppService)
    gateway = WhatsAppGatewayService(wsp_service)

    callback_mock = AsyncMock()
    monkeypatch.setattr(gateway, "_send_callback", callback_mock)

    data = {"to": "+51911122233", "message": "hola", "delivery_job_id": 456}
    res = await gateway.send_whatsapp_gateway(data)

    wsp_service.send.assert_awaited_once_with("+51911122233", "hola")
    callback_mock.assert_awaited_once()
    assert res["status"] == "success"
    assert res["channel"] == "whatsapp"
