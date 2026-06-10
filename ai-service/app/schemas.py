from pydantic import BaseModel


class GenerateRequest(BaseModel):
    message: str


class GenerateResponse(BaseModel):
    reply: str
