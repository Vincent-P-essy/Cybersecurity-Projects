from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://canaris:canaris@postgres:5432/canaris"
    ssh_host: str = "0.0.0.0"
    ssh_port: int = 2222
    http_honeypot_host: str = "0.0.0.0"
    http_honeypot_port: int = 8088
    ftp_host: str = "0.0.0.0"
    ftp_port: int = 2121
    geoip_url: str = "http://ip-api.com/json"
    ssh_host_key_path: str = "/tmp/canaris_ssh_host_key"

    model_config = {"env_file": ".env"}


settings = Settings()
