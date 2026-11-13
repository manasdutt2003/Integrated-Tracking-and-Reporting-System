"""Email notifications sent through Gmail SMTP."""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True only when it was accepted."""
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    if not sender_email or not sender_password:
        logger.warning("EMAIL_USER / EMAIL_PASS are not configured; email not sent.")
        return False

    tracking_link = os.getenv("LIVE_TRACKING_URL")
    if tracking_link:
        body += f"\n\nYou can track your bus live here: {tracking_link}"

    message = MIMEText(body)
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], message.as_string())
        return True
    except (smtplib.SMTPException, OSError):
        logger.exception("Could not send email")
        return False
