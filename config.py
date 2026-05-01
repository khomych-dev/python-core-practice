from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    openai_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url_test: str | None = None

    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_base_url: str = "https://cloud.langfuse.com"

    stripe_api_key: str = "sk_test_dummy"
    stripe_webhook_secret: str = "whsec_dummy"

    base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")


settings = Settings()  # pyright: ignore
