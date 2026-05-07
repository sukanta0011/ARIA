from sqlalchemy import (
    Enum, String, Text, JSON,
    Column, DateTime, ForeignKey,)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum
import uuid


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    jobs = relationship("Job", back_populates="tenant")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    status = Column(Enum(JobStatus), nullable=False)
    topic = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now)
    
    tenant = relationship("Tenant", back_populates="jobs")
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
