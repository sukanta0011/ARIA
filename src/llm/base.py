from abc import ABC, abstractmethod
from pydantic import Field, field_validator, BaseModel
from typing import List, Dict
from ..core.custom_errors import EmptyStringError


class ValidMessage(BaseModel):
    valid_message: str = Field(min_length=1, max_length=100)

    @field_validator("valid_message")
    @classmethod
    def validate_message(cls, msg: str):
        if len(msg.strip()) == 0:
            raise EmptyStringError("Query message is empty")
        return msg


class LLMResponse(BaseModel):
    msg: str
    response_msg: str | None
    read_token: int | None = 0
    write_token: int | None = 0
    latency: float = 0.0
    tokens_per_sec: float = 0.0


class BaseLLM(ABC):
    @abstractmethod
    async def complete(self, message: ValidMessage) -> LLMResponse: ...

    @abstractmethod
    async def complete_with_tools(
            self, message: ValidMessage, tools: List[Dict]): ...
