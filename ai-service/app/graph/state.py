from typing import TypedDict, Optional


class AgentState(TypedDict):
    user_message: str
    lang: str
    history: list[dict]
    final_answer: Optional[str]
    error: Optional[str]
    max_retries: int
    retry_count: int
    validation: str
    retry_prompt: Optional[str]
