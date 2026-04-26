from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class BasicState(BaseModel):
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tokens_read: int = 0
    tokens_write: int = 0
    total_latency: float = 0.0
    status: str = ""


class ResearchState(BasicState):
    history: List[Dict[str, Any]] = Field(default_factory=list)
    tool_used: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    final_answer: str = ""


class AgentState(BasicState):
    research_states: List[ResearchState] = Field(default_factory=list)
    sub_questions: List[str] = Field(default_factory=list)