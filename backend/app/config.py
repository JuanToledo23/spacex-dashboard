"""Application settings loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    spacex_api_base: str = "https://api.spacexdata.com"
    redis_url: str = "redis://localhost:6379/0"

    rockets_ttl: int = 86400  # 24 hours
    launches_ttl: int = 120  # 2 minutes
    starlink_ttl: int = 300  # 5 minutes
    dashboard_ttl: int = 300  # 5 minutes
    cores_ttl: int = 86400  # 24 hours (same as rockets)
    launchpads_ttl: int = 86400  # 24 hours
    history_ttl: int = 86400  # 24 hours
    landing_ttl: int = 86400  # 24 hours
    roadster_ttl: int = 86400  # 24 hours
    economics_ttl: int = 300  # 5 minutes
    emissions_ttl: int = 300  # 5 minutes

    spacex_timeout: int = 10
    spacex_retries: int = 2

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    cors_origins: str = "https://quadsci.juantoledo.com.mx,http://localhost:5173"

    model_config = {"env_file": ".env"}


settings = Settings()
