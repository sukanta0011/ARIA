import asyncio
from src.workers.celery_app import celery_app
from ..db.models import JobStatus
from ..db.session import async_session
from ..db.repositories.job_repo import JobRepository
from ..agent.graph import app


@celery_app.task(name="src.workers.research_task.run_research_task")
def run_research_task(job_id: str, topic: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(execute_agents(job_id, topic))


async def execute_agents(job_id: str, topic: str):
    async with async_session() as session:
        repo = JobRepository(session)

        await repo.update_status(
            job_id, status=JobStatus.RUNNING)
        
        try:
            async for outputs in app.astream({'query': topic}):
                for node_name, state_update in outputs.items():
                    if node_name == "researcher":
                        last_response = state_update["research_states"][-1]
                        await repo.save_trace(
                            job_id=job_id,
                            node_name=f"researcher: {last_response.worker_id}",
                            input_data={"query": last_response.query},
                            output_data={"answer": last_response.final_answer}
                        )
                    elif node_name == "planner":
                        await repo.save_trace(
                            job_id=job_id,
                            node_name=node_name,
                            input_data={}, 
                            output_data={
                                "question": v.question
                                 for _, v in state_update["question_registry"].items()
                                 if state_update["question_registry"]}
                        )
                    elif node_name == "synthesizer":
                        await repo.save_trace(
                            job_id=job_id,
                            node_name=node_name,
                            input_data={}, 
                            output_data={"answer": state_update["final_report"]}
                        )
            await repo.update_status(job_id, JobStatus.COMPLETE)
            await session.commit()
        except Exception as e:
            await session.rollback()
            await repo.update_status(job_id, JobStatus.FAILED)
            raise e
