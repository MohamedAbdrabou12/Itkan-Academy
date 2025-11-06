from app.services.notification_service.workrs.celery_app import celery_app


@celery_app.task(name="send_email_task")
def send_email_task(to: str, subject: str, body: str):
    payload = {
        "email": to,
        "subject": subject,
        "body": body,
    }

    # Import inside to avoid circular imports
    from app.services.notification_service.workrs.worker import send_notification_task

    send_notification_task.delay(
        user_id=to,
        channel="email",
        template_type="reset_password",
        payload=payload,
    )
