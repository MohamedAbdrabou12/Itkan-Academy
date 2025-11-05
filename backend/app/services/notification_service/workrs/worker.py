from .celery_app import celery_app
from ..utils.email_client import (
    send_email,
)
from ..utils.template_engine import (
    render_template,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(
    self, user_id: str, channel: str, template_type: str, payload: dict
):
    try:
        if channel == "email":
            template_name = f"{template_type}.html"

            subject, body = render_template(template_name, payload)

            recipient_email = payload.get("email")
            if not recipient_email:
                raise ValueError(f"No email in payload for user {user_id}")

            send_email(user_email=recipient_email, subject=subject, html_body=body)

        elif channel == "web":
            message_text = render_template(f"{template_type}.txt", payload)

            print(f"[WEB NOTIFICATION] to {user_id}: {message_text}")

        else:
            print(f"Unknown channel: {channel}")
            return

    except Exception as e:
        print(f"Task failed: {e}. Retrying...")
        self.retry(exc=e)
