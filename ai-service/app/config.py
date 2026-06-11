from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1500
    openai_timeout: float = 30.0
    openai_temperature: float = 0.3
    max_message_length: int = 4000
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
