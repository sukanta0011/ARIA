from fastapi import APIRouter, Depends
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...db.repositories.job_repo import JobRepository


router = APIRouter()


@router.post("/research")
async def research_task(
    topic: str, db: AsyncSession = Depends(get_db)):
    job_id = str(uuid.uuid4())
    repo = JobRepository(db)
    await repo.create_job(job_id, topic)

    return {"job_id": job_id, "status": "pending"}
