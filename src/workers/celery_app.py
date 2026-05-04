from celery import Celery
from ..core.config import settings

celery_app = Celery(
    "research_task",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['src.workers.research_task']
)