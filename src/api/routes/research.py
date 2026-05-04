from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.models import Job
from ...db.session import get_db
from ...db.repositories.job_repo import JobRepository
from ...workers.research_task import run_research_task


router = APIRouter()


@router.post("/research")
async def research_task(
    topic: str, db: AsyncSession = Depends(get_db)):

    job_id = str(uuid.uuid4())
    repo = JobRepository(db)
    await repo.create_job(job_id, topic)

    run_research_task.delay(job_id, topic)

    return {"job_id": job_id, "status": "pending"}


@router.get("/research/{job_id}")
async def get_status(
    job_id: str, db: AsyncSession = Depends(get_db)
        ) -> Job:

    repo = JobRepository(db)
    job = await repo.get_job(job_id=job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/research/{job_id}/trace")
async def get_status(
    job_id: str, db: AsyncSession = Depends(get_db)
        ) -> Job:

    repo = JobRepository(db)
    job = await repo.get_job(job_id=job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job.traces