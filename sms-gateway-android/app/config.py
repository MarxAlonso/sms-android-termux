import pydantic


class AppSettings(pydantic.BaseSettings):
    redis_url = pydantic.RedisDsn(url="redis://localhost/", scheme="redis")
    redis_port: int = 6379
    backend_url: str = "https://backend-production-8462.up.railway.app"

    class Config:  # type: ignore[misc]
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AppSettings()
