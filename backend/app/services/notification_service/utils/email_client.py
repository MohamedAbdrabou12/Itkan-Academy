import asyncio
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType  # type: ignore
from pydantic import SecretStr
from app.core.config import settings


if (
    settings.MAIL_USERNAME is None
    or settings.MAIL_PASSWORD is None
    or settings.MAIL_FROM is None
    or settings.MAIL_SERVER is None
    or settings.MAIL_PORT is None
    or settings.MAIL_STARTTLS is None
):
    raise ValueError("Email configuration is incomplete. Please check your settings.")

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)


# Sending mails
def send_email(
    user_email: str,
    subject: str,
    html_body: str,
):
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=html_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    try:
        asyncio.run(fm.send_message(message))
        print(f"Successfully sent email to {user_email}")
    except Exception as e:
        print(f"Task failed: {e}. Retrying...")

        raise e
