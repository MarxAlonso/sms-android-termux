import pytest

from app.whatsapp_service import WhatsAppService


def test_normalize_number_removes_plus_and_spaces():
    assert WhatsAppService.normalize_number(" +51999999999 ") == "51999999999"


def test_build_wa_url_encodes_message():
    url = WhatsAppService.build_wa_url("+51911122233", "Hola mundo & ok")
    assert url == "https://wa.me/51911122233?text=Hola%20mundo%20%26%20ok"


@pytest.mark.asyncio
async def test_send_raises_http_exception_when_command_missing(monkeypatch):
    service = WhatsAppService()

    def _raise(*_args, **_kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr("subprocess.run", _raise)

    with pytest.raises(Exception) as exc:
        await service.send("+51911122233", "hello")

    assert "termux-open-url is not available" in str(exc.value)
