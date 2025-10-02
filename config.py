from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

SCHEDULE_TIME = {"hour": 9, "minute": 0}
TIMEZONE = "Asia/Irkutsk"

subscribed_users: set[int | None] = set()
user_cities: dict[int | None, str | None] = {}


class Settings(BaseSettings):
    bot_token: SecretStr
    chat_id: SecretStr
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

config = Settings()
