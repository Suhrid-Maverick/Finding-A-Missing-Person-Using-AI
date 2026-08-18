"""
Email notification helper.

Reads SMTP config from environment variables:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

Recipient is the complainant_email stored on the case.
Falls back to NOTIFY_EMAIL env var if complainant email is not set.
Silently skips without crashing if variables are not set.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_match_notification(case_id: str, case_details: tuple) -> bool:
    """
    Send an email when a missing person case has been matched.

    Args:
        case_id: The registered case UUID.
        case_details: Tuple of (name, complainant_mobile, complainant_email, age, last_seen, birth_marks).

    Returns:
        True if email was sent, False otherwise.
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", "587")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_host, smtp_user, smtp_password]):
        print(
            "[emailer] SMTP environment variables not fully set — skipping notification."
        )
        return False

    # case_details now: (name, complainant_mobile, complainant_email, age, last_seen, birth_marks)
    name = case_details[0] if case_details else "Unknown"
    complainant_email = case_details[2] if len(case_details) > 2 else None
    age = case_details[3] if len(case_details) > 3 else "N/A"
    last_seen = case_details[4] if len(case_details) > 4 else "N/A"

    # Use complainant email if available, otherwise fall back to env var
    recipient = complainant_email or os.environ.get("NOTIFY_EMAIL")
    if not recipient:
        print("[emailer] No recipient email available — skipping notification.")
        return False

    try:
        subject = f"Match Found – {name}"
        body = f"""\
Hello,

A match has been found for the following missing person case registered in the system.

Case Details:
  Name      : {name}
  Age       : {age}
  Last Seen : {last_seen}
  Case ID   : {case_id}

Please log in to the Missing Person Tracking System to review and confirm the match.

--
This is an automated notification. Please do not reply to this email.
"""
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())

        print(f"[emailer] Notification sent to {recipient} for case {case_id}")
        return True

    except Exception as exc:
        print(f"[emailer] Failed to send email: {exc}")
        return False
