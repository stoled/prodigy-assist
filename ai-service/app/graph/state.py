from typing import TypedDict, Optional


class AgentState(TypedDict):
    """Состояние LangGraph агента."""
    user_message: str
    lang: str
    history: list[dict]
    retrieved_chunks: list[dict]
    context: Optional[str]
    wikipedia_fetched: bool
    wikipedia_attempted: bool
    wikipedia_article: Optional[dict]
    final_answer: Optional[str]
    error: Optional[str]
    max_rag_retries: int
    rag_retry_count: int
