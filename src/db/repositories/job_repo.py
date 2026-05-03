from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models import Job, JobStatus


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_id: str, topic: str) -> Job:
        new_job = Job(id=job_id, topic=topic, status=JobStatus.PENDING)
        self.session.add(new_job)
        await self.session.commit()
        await self.session.refresh(new_job)
        return new_job
    
    async def update_status(self, job_id: str, status: JobStatus) -> None:
        await self.session.execute(
            update(Job).values(status = status).where(Job.id==job_id))
        await self.session.commit()

    async def get_job(self, job_id: str) -> Job:
        result = await self.session.execute(select(Job).where(Job.id==job_id))
        return result.scalars().first()
