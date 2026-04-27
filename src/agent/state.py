from pydantic import BaseModel, Field
import uuid
from operator import add
from typing import List, Dict, Any, TypedDict, Annotated
from datetime import datetime


class BasicState(BaseModel):
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tokens_read: int = 0
    tokens_write: int = 0
    total_latency: float = 0.0
    status: str = ""


class ResearchState(BasicState):
    worker_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: List[Dict[str, Any]] = Field(default_factory=list)
    tool_used: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    final_answer: str = ""


class AgentState(BasicState):
    research_states: List[ResearchState] = Field(default_factory=list)
    sub_questions: List[str] = Field(default_factory=list)


class Questions(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    status: bool = False


class GraphState(TypedDict):
    query: str
    sub_questions: Annotated[List[Questions], add]
    timestamp: datetime
    tokens_read: Annotated[int, add]
    tokens_write: Annotated[int, add]
    total_latency: Annotated[float, add]
    research_states: Annotated[List[ResearchState], add]
    iteration_count: Annotated[int, add]
    next_step: str
    status: str
    final_report: str
