import pydantic


class AppSettings(pydantic.BaseSettings):
    redis_url = pydantic.RedisDsn(url="redis://localhost/", scheme="redis")
    redis_port: int = 6379
    backend_url: str = "https://api.cobralo.pe"
    admin_email: str = "bensamuel114@gmail.com"
    admin_password: str = "admin12345"
    pending_sms_path: str = "/calendario/delivery-jobs/sms-pendientes"
    pending_wsp_path: str = "/calendario/delivery-jobs/wsp-pendientes"
    pending_whatsapp_path: str | None = None

    @property
    def resolved_pending_wsp_path(self) -> str:
        return self.pending_wsp_path or self.pending_whatsapp_path or "/calendario/delivery-jobs/wsp-pendientes"

    class Config:  # type: ignore[misc]
        env_file = ".env"
        env_file_encoding = "utf-8"
        fields = {
            "pending_wsp_path": {
                "env": ["PENDING_WSP_PATH", "PENDING_WHATSAPP_PATH"]
            }
        }


settings = AppSettings()
