"""Configurazione letta dalle variabili d'ambiente (secrets in CI)."""
from __future__ import annotations

import os
from dataclasses import dataclass


class MissingConfigError(RuntimeError):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MissingConfigError(f"Variabile d'ambiente mancante: {name}")
    return value


@dataclass
class Config:
    ifq_username: str
    ifq_password: str
    gdrive_client_id: str
    gdrive_client_secret: str
    gdrive_refresh_token: str
    gdrive_folder_id: str
    retention_days: int
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_app_password: str
    notify_email_to: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            ifq_username=_require("IFQ_USERNAME"),
            ifq_password=_require("IFQ_PASSWORD"),
            gdrive_client_id=_require("GDRIVE_CLIENT_ID"),
            gdrive_client_secret=_require("GDRIVE_CLIENT_SECRET"),
            gdrive_refresh_token=_require("GDRIVE_REFRESH_TOKEN"),
            gdrive_folder_id=_require("GDRIVE_FOLDER_ID"),
            retention_days=int(os.environ.get("RETENTION_DAYS", "5")),
            smtp_host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.environ.get("SMTP_PORT", "587")),
            smtp_user=_require("SMTP_USER"),
            smtp_app_password=_require("SMTP_APP_PASSWORD"),
            notify_email_to=os.environ.get("NOTIFY_EMAIL_TO") or os.environ.get("SMTP_USER", ""),
        )
