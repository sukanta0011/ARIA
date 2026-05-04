import asyncio
from .celery_app import celery_app
from ..db.models import JobStatus
from ..db.session import async_session
from ..db.repositories.job_repo import JobRepository
from ..agent.graph import app


@celery_app.task(name="run_research_task")
def run_research_task(job_id: str, topic: str):
    return asyncio.run(execute_agents(job_id, topic))


async def execute_agents(job_id: str, topic: str):
    async with async_session() as session:
        repo = JobRepository(job_id)

        await repo.update_status(
            job_id, status=JobStatus.RUNNING)
        
        try:
            async for outputs in app.stream({'query': topic}):
                for node_name, state_update in outputs.items():
                    if node_name == "researcher":
                        last_response = state_update["research_states"][-1]
                        await repo.save_trace(
                            job_id=job_id,
                            node_name=f"node_name: {last_response.worker_id}",
                            input_data=last_response.query,
                            output_data=last_response.final_answer
                        )
                    else:
                        await repo.save_trace(
                            job_id=job_id,
                            node_name=node_name,
                            input_data={}, 
                            output_data=state_update
                        )
        except Exception as e:
            await repo.update_status(job_id, JobStatus.FAILED)
            raise e