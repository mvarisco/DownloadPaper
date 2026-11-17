"""Invio email di notifica (es. in caso di errore del job) via SMTP."""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_app_password: str,
    to_address: str,
    subject: str,
    body: str,
) -> None:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_address

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_app_password)
        server.sendmail(smtp_user, [to_address], msg.as_string())
