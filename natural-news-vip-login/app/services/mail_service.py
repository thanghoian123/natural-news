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

mail_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Password</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            background: #007bff;
            color: #ffffff;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            font-size: 20px;
        }
        .logo {
            text-align: center;
            margin: 20px 0;
        }
        .logo img {
            max-width: 150px;
        }
        .content {
            padding: 20px;
            text-align: center;
        }
        .password-box {
            background: #f8f9fa;
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            font-weight: bold;
            border: 1px dashed #007bff;
            border-radius: 5px;
            margin-top: 10px;
        }
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">Session Password</div>
        <div class="logo">
            <img src="{logo_url}" alt="Application Logo">
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Your session password is:</p>
            <div class="password-box">{session_password}</div>
            <p>Please use this password to access your session. Do not share it with anyone.</p>
        </div>
        <div class="footer">If you did not request this, please ignore this email.</div>
    </div>
</body>
</html>
'''
