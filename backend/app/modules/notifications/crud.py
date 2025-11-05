from sqlalchemy.orm import Session
from . import models, schemas


def create_notification(db: Session, notification: schemas.NotificationCreate):
    db_notification = models.Notification(
        user_id=notification.user_id,
        channel=notification.channel,
        template=notification.template,
        payload=notification.payload,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification
