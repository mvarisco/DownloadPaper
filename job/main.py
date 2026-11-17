"""Orchestrazione: login+download PDF odierno -> upload Drive -> pulizia retention -> notifica su errore."""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from config import Config
from drive_client import cleanup_old_files, upload_pdf
from ifq_client import download_today_pdf
from notifier import send_email

ROME_TZ = ZoneInfo("Europe/Rome")


def main() -> int:
    cfg = Config.from_env()
    today = datetime.now(ROME_TZ).date()
    filename = f"ilfattoquotidiano_{today.isoformat()}.pdf"

    try:
        pdf_bytes = download_today_pdf(cfg.ifq_username, cfg.ifq_password, today)
        upload_pdf(cfg.gdrive_service_account_json, cfg.gdrive_folder_id, filename, pdf_bytes)
        deleted = cleanup_old_files(cfg.gdrive_service_account_json, cfg.gdrive_folder_id, cfg.retention_days)
        print(f"OK: caricato {filename}. Rimossi {len(deleted)} file piu' vecchi di {cfg.retention_days} giorni.")
        return 0
    except Exception as exc:
        error_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        print(error_text, file=sys.stderr)
        try:
            send_email(
                cfg.smtp_host,
                cfg.smtp_port,
                cfg.smtp_user,
                cfg.smtp_app_password,
                cfg.notify_email_to,
                subject=f"[Il Fatto Quotidiano] Download fallito ({today.isoformat()})",
                body=f"Il job di download/upload e' fallito:\n\n{error_text}",
            )
        except Exception as notify_exc:
            print(f"Invio email di notifica fallito: {notify_exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
