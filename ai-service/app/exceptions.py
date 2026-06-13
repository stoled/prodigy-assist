from fastapi import HTTPException, status


class MessageTooLongError(HTTPException):
    def __init__(self, detail: str = "Message is too long") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class LLMUnavailableError(HTTPException):
    def __init__(self, detail: str = "LLM service is unavailable") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class EmbeddingError(HTTPException):
    def __init__(self, detail: str = "Embedding service error") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
