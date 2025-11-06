from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "notification_tasks",
    broker=settings.BROKER_URL,
    backend=settings.BROKER_URL,
    include=[
        "app.services.notification_service.tasks.email",
        "app.services.notification_service.tasks.web",
        "app.services",
    ],
)

celery_app.conf.update(
    task_track_started=True,
)
