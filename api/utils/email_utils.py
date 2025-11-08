import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "tanishkaur03@gmail.com"
SENDER_PASSWORD = "Sim@123@ran"

def send_reset_email(to_email: str, token: str):
    reset_link = f"http://127.0.0.1:8000/auth/reset-password?token={token}"
    subject = "Password Reset Request"
    body = f"""
    Hi,
    Click the link below to reset your password:
    {reset_link}
    (valid for 15 minutes)
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f" Reset email sent to {to_email}")
    except Exception as e:
        print(f" Email send failed: {e}")
