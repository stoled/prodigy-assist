from pydantic import BaseModel


class GenerateRequest(BaseModel):
    message: str
    history: list[dict] = []
    use_rag: bool = False
    lang: str | None = None


class GenerateResponse(BaseModel):
    reply: str
