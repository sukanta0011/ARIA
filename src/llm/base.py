from abc import ABC, abstractmethod
from pydantic import Field, field_validator, BaseModel
from typing import Any, List, Dict, Tuple
from ollama import ChatResponse
from ..core.custom_errors import EmptyStringError
from ..tools.tool_registry import ToolRegistry
from ..agent.state import AgentState


class ValidMessage(BaseModel):
    valid_message: str = Field(min_length=1, max_length=100)

    @field_validator("valid_message")
    @classmethod
    def validate_message(cls, msg: str):
        if len(msg.strip()) == 0:
            raise EmptyStringError("Query message is empty")
        return msg


class LLMResponse(BaseModel):
    msg: str | ValidMessage
    response_msg: str | None
    read_token: int | None = 0
    write_token: int | None = 0
    latency: float = 0.0
    tokens_per_sec: float = 0.0


class LLMResponseTools(LLMResponse):
    tools: Any | None = None


class BaseLLM(ABC):
    @abstractmethod
    async def execute_chat(
        self, message: List[Dict], tools: List[Dict] | None = None
            ) -> Tuple[ChatResponse, float] | Tuple[str, float]: ...

    @abstractmethod
    async def complete(self, message: ValidMessage) -> LLMResponse: ...

    @abstractmethod
    async def complete_with_tools(
            self, state: AgentState,
            tools: ToolRegistry
                ) -> AgentState: ...
