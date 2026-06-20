from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    admin_ids: Annotated[list[int], NoDecode]
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    db_url: str = "sqlite+aiosqlite:///shop.db"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def split_admin_ids(cls, value: str | list[int]) -> list[int]:
        if isinstance(value, str):
            return [int(item) for item in value.split(",") if item.strip()]
        return value


settings = Settings()