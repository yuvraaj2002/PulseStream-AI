import smtplib
from email.mime.text import MIMEText
from api.utils.database import get_session
from api.model.auth_model import EmailEvent

# --- SMTP configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "tanishkaur03@gmail.com"
SENDER_PASSWORD = "Sim@123@ran"


def send_reset_email(to_email: str, token: str):
    """
    Sends password reset email to the given address and logs the event.
    """
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

        print(f"Reset email sent to {to_email}")
        log_email_event(to_email, "password_reset", "sent")

    except Exception as e:
        print(f"email send failed: {e}")
        log_email_event(to_email, "password_reset", "failed")


def log_email_event(email: str, event_type: str, status: str):
    """
    Logs every email send attempt (success or failure) to the database.
    """
    try:
        with get_session() as session:
            event = EmailEvent(
                user_email=email,
                event_type=event_type,
                status=status
            )
            session.add(event)
            session.commit()
        print(f"Logged event: {event_type} → {status} for {email}")

    except Exception as e:
        print(f"Failed to log email event: {e}")
