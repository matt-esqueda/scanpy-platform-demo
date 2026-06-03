"""
Celery application configuration.

Start worker with:
    celery -A app.core.celery_app worker --loglevel=info
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "scanpy_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Import tasks to register them
from app.tasks import scanpy_tasks  # noqa