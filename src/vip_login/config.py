import logging

from fastapi_mail import ConnectionConfig


DB = "sqlite:///database.db"

LOYALTY_WEBHOOK_SECRET = "abc"

TOKEN_EQUIVALENT = 10

LOGGER = logging.getLogger("uvicorn.error")

MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME = "nhatnguyenminh061289@gmail.com",
    MAIL_PASSWORD = "ekzoedpfpqujisrn",
    MAIL_FROM = "nhatnguyenminh061289@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Nathan Nguyen",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)

SECRET_KEY = "your-secret-key-here"
