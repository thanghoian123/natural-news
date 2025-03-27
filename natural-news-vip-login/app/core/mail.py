from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM
import random
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Neil Proton",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)

async def send_email(email: str, subject: str, body: str):
    """Send an email asynchronously."""
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

def generate_session_password():
    """Generate a 6-digit random numeric password."""
    return str(random.randint(100000, 999999))