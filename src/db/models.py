from sqlalchemy import (
    Enum, String, Text, JSON,
    Column, DateTime, ForeignKey,)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    status = Column(Enum(JobStatus), nullable=False)
    topic = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now)
    
    result = relationship("JobResult", back_populates="job", uselist=False)
    traces = relationship("AgentTrace", back_populates="job")


class JobResult(Base):
    __tablename__ = "job_results"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    report = Column(JSON)

    job = relationship("Job", back_populates="result")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    node_name = Column(String, nullable=False)
    time_stamp = Column(DateTime, default=datetime.now)
    input = Column(JSON)
    output = Column(JSON)

    job = relationship("Job", back_populates="traces")
