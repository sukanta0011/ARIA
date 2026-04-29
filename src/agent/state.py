from pydantic import BaseModel, Field
import uuid
from operator import add, ior
from typing import List, Dict, Any, TypedDict, Annotated, Set
from datetime import datetime


class BasicState(BaseModel):
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tokens_read: int = 0
    tokens_write: int = 0
    total_latency: float = 0.0
    status: str = ""


class Question(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    status: bool = False


class ResearchState(BasicState):
    worker_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: Question
    history: List[Dict[str, Any]] = Field(default_factory=list)
    tool_used: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    final_answer: str = ""


class AgentState(BasicState):
    research_states: List[ResearchState] = Field(default_factory=list)
    sub_questions: List[str] = Field(default_factory=list)


class GraphState(TypedDict):
    query: str
    # sub_questions: Annotated[List[str], add]
    question_registry: Annotated[Dict[str, Question], ior]
    failed_question_ids: Annotated[Set[str], ior]
    timestamp: datetime
    tokens_read: Annotated[int, add]
    tokens_write: Annotated[int, add]
    total_latency: Annotated[float, add]
    research_states: Annotated[List[ResearchState], add]
    iteration_count: Annotated[int, add]
    next_step: str
    status: str
    final_report: str
