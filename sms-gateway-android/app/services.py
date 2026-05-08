import subprocess
import typing

import starlite

from app import utils

TERMUX_SMS_API = ["termux-sms-send", "-n"]
WHATSAPP_API = ["mudslide", "send"]

SMS_API = list[str] | None
Termux = utils.Termux | None


class MessageService:
    termux: Termux
    sms_api: SMS_API

    def __init__(self, termux: Termux, sms_api: SMS_API = None):
        self.termux = termux
        self.sms_api = sms_api

    @staticmethod
    def validate_send_sms(
        func: typing.Callable[["MessageService", str, str], typing.Awaitable[None]]
    ) -> typing.Callable[["MessageService", str, str], typing.Awaitable[None]]:
        async def wrapper(self: typing.Self, number: str, message: str):
            if not self.termux:
                raise RuntimeError("Termux service is not available")
            if not self.sms_api:
                raise RuntimeError("Termux SMS API is not available")

            return await func(self, number, message)

        return wrapper

    @validate_send_sms
    async def send(self, number: str, message: str) -> None:
        """Send a text message to a given number.

        Args:
            number (str): The phone number to send the message to.
            message (str): The message to be sent.
        """
        # The decorator will check if the termux service and sms api are available
        # The code below is just for the type checker
        assert self.termux is not None

        try:
            _ = await self.termux.send_sms(number, message)
        except FileNotFoundError:
            raise starlite.HTTPException(
                status_code=500, detail="Termux SMS API is unavailable"
            )
        except OSError as os_err:
            raise starlite.HTTPException(
                status_code=500,
                detail=f"Failed to send SMS message: {os_err}",
            )
        except subprocess.CalledProcessError as proc_err:
            raise starlite.HTTPException(
                status_code=500,
                detail=f"Failed to send SMS message with {proc_err.cmd}",
            )

    async def send_whatsapp(self, number: str, message: str) -> None:
        """Send a WhatsApp message using mudslide.

        Args:
            number (str): The phone number to send the message to.
            message (str): The message to be sent.
        """
        # Mudslide usually expects numbers without the '+' prefix
        clean_number = number.replace("+", "").strip()
        command = ["mudslide", "send", clean_number, message]

        try:
            import asyncio
            loop = asyncio.get_running_loop()
            proc = await loop.run_in_executor(
                None, lambda: subprocess.run(command, capture_output=True)
            )
            if proc.returncode != 0:
                error_detail = proc.stderr.decode()
                logger.error(f"Mudslide error: {error_detail}")
                raise RuntimeError(f"WhatsApp send failed: {error_detail}")
        except FileNotFoundError:
            raise starlite.HTTPException(
                status_code=500, detail="Mudslide CLI is not installed"
            )
        except Exception as e:
            raise starlite.HTTPException(
                status_code=500,
                detail=f"Failed to send WhatsApp message: {str(e)}",
            )

    @classmethod
    def create(cls, termux: Termux = None, sms_api: SMS_API = None) -> "MessageService":
        return cls(termux, sms_api)
