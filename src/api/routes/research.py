from fastapi import APIRouter, Depends, HTTPException, Header
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.models import Job, AgentTrace, Tenant
from ...db.session import get_db
from ...db.repositories.job_repo import JobRepository
from ...db.repositories.tenant_repo import TenantRepository
from ...workers.research_task import run_research_task


router = APIRouter()


async def verify_api_key(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
        ):
    # tenant_repo = TenantRepository(db)
    # tenant = await tenant_repo.get_tenant_id(name=name, api_key=api_key)
    # if not tenant:
    #     raise HTTPException(status_code=401,
    #     detail="Invalid API key or name combination")
    # return tenant
    print(authorization)


async def get_job_repo(
    tenant = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
        ) -> JobRepository:
    return JobRepository(session=db, tenant_id=tenant.id)


@router.post("/research", response_model=None)
async def research_task(
    topic: str,
    repo: JobRepository = Depends(get_job_repo)
        ):

    job_id = str(uuid.uuid4())
    await repo.create_job(job_id, topic)
    run_research_task.delay(job_id, topic) ## Move job to Redis the Celery
    return {"job_id": job_id, "status": "pending"}


@router.get("/research/{job_id}", response_model=None)
async def get_status(
    job_id: str, repo: JobRepository = Depends(get_job_repo)
        ) -> Job:

    job = await repo.get_job(job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/research/{job_id}/trace", response_model=None)
async def get_status(
    job_id: str, repo: JobRepository = Depends(get_job_repo)
        ) -> AgentTrace:

    traces = await repo.get_traces(job_id=job_id)
    if not traces:
        raise HTTPException(status_code=404, detail="Traces are missing")
    return traces
