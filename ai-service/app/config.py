from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    ai_api_key: str
    ai_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    ai_max_tokens: int = 1500
    ai_timeout: float = 60.0
    ai_temperature: float = 0.3
    max_message_length: int = 4000
    port: int = 8000

    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = Settings()
