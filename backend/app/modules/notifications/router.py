from fastapi import APIRouter, Depends, status
from .schemas import NotificationRequest
from app.services.notification_service.workrs.worker import send_notification_task
from app.core.config import settings

router = APIRouter()


notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/notifications/", status_code=status.HTTP_202_ACCEPTED)
async def queue_notification(request: NotificationRequest):
    send_notification_task.delay(  # type: ignore
        user_id=request.user_id,
        channel=request.channel,
        template_type=request.template_type,
        payload=request.payload,
    )

    return {"message": "Notification has been queued"}
