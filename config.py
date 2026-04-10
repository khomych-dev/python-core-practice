from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    database_url_test: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


settings = Settings()  # type: ignore
