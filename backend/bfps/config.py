from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    allowed_origins: list[str] = [
        "https://wasa-rockoon.github.io",
        "https://ddd3h.github.io",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    mc_max_samples: int = 2000
    tawhiri_url: str = "https://api.v2.sondehub.org/tawhiri"

    model_config = {"env_prefix": "BFPS_"}


settings = Settings()
