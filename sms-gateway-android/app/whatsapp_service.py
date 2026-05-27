import asyncio
import subprocess
import urllib.parse

import starlite


class WhatsAppService:
    @staticmethod
    def normalize_number(number: str) -> str:
        return number.replace("+", "").strip()

    @classmethod
    def build_wa_url(cls, number: str, message: str) -> str:
        clean_number = cls.normalize_number(number)
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{clean_number}?text={encoded_message}"

    async def send(self, number: str, message: str) -> None:
        url = self.build_wa_url(number, message)
        command = ["termux-open-url", url]

        try:
            loop = asyncio.get_running_loop()
            proc = await loop.run_in_executor(
                None, lambda: subprocess.run(command, capture_output=True)
            )
            if proc.returncode != 0:
                error_detail = proc.stderr.decode().strip()
                raise RuntimeError(f"WhatsApp send failed: {error_detail}")
        except FileNotFoundError:
            raise starlite.HTTPException(
                status_code=500, detail="termux-open-url is not available"
            )
        except Exception as exc:
            raise starlite.HTTPException(
                status_code=500,
                detail=f"Failed to send WhatsApp message: {str(exc)}",
            )
