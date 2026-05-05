from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Dict
import uuid
from ..models import Job, JobStatus, AgentTrace, JobResult


class JobRepository:
    def __init__(self, session: AsyncSession, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id

    async def create_job(self, job_id: str, topic: str) -> Job:
        new_job = Job(id=job_id, topic=topic, status=JobStatus.PENDING, tenant_id=self.tenant_id)
        self.session.add(new_job)
        await self.session.commit()
        await self.session.refresh(new_job)
        return new_job
    
    async def update_status(self, job_id: str, status: JobStatus) -> None:
        await self.session.execute(
            update(Job).values(status = status)
            .where(Job.id==job_id, Job.tenant_id==self.tenant_id))
        await self.session.commit()

    async def get_job(self, job_id: str) -> Job:
        result = await self.session.execute(select(Job)
                    .where(Job.id==job_id, Job.tenant_id==self.tenant_id))
        return result.scalars().first()

    async def get_traces(self, job_id: str) -> AgentTrace:
        result = await self.session.execute(
            select(Job).options(
                selectinload(Job.traces))
                .where(Job.id==job_id, Job.tenant_id==self.tenant_id))

        return result.scalars().first()

    async def save_trace(self, job_id: str, node_name: str, input_data: Dict, output_data: Dict):
        new_track = AgentTrace(
            id=str(uuid.uuid4()),
            job_id=job_id,
            node_name=node_name,
            input=input_data,
            output=output_data
        )
        self.session.add(new_track)
        await self.session.commit()

    async def save_result(self, job_id: str, report_data: Dict):
        result = JobResult(
            id=str(uuid.uuid4()),
            job_id=job_id,
            report=report_data
        )
        self.session.add(result)
        await self.update_status(job_id, JobStatus.COMPLETE)
        await self.session.commit()
