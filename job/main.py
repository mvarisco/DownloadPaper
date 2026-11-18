"""Orchestrazione: controllo idempotenza -> login+download PDF odierno -> upload Drive
-> pulizia retention -> notifica su errore.

Pensato per essere invocato ogni 10 minuti (workflow_dispatch lanciato da un
crontab esterno, vedi SETUP.md). Ad ogni esecuzione:
- se il PDF di oggi e' gia' su Drive non fa nulla (nessun login, nessun download);
- altrimenti prova a scaricarlo e caricarlo.
In caso di fallimento non manda una email ad ogni tentativo: la manda una
sola volta quando i fallimenti consecutivi raggiungono la soglia configurata
(default 10). Il conteggio dei fallimenti pregressi viene passato dal
workflow (PRIOR_CONSECUTIVE_FAILURES), calcolato leggendo la cronologia delle
run precedenti della Action: non serve uno stato locale, dato che ogni run e'
un runner nuovo ed effimero.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from config import Config
from drive_client import build_service, cleanup_old_files, file_exists, upload_pdf
from ifq_client import download_today_pdf
from notifier import send_email

ROME_TZ = ZoneInfo("Europe/Rome")


def main() -> int:
    cfg = Config.from_env()
    today = datetime.now(ROME_TZ).date()
    filename = f"ilfattoquotidiano_{today.isoformat()}.pdf"

    try:
        service = build_service(cfg.gdrive_client_id, cfg.gdrive_client_secret, cfg.gdrive_refresh_token)

        if file_exists(service, cfg.gdrive_folder_id, filename):
            print(f"OK: {filename} e' gia' presente su Drive, nessuna azione necessaria.")
            return 0

        pdf_bytes = download_today_pdf(cfg.ifq_username, cfg.ifq_password, today)
        upload_pdf(service, cfg.gdrive_folder_id, filename, pdf_bytes)
        deleted = cleanup_old_files(service, cfg.gdrive_folder_id, cfg.retention_days)

        print(f"OK: caricato {filename}. Rimossi {len(deleted)} file piu' vecchi di {cfg.retention_days} giorni.")
        return 0
    except Exception as exc:
        error_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        print(error_text, file=sys.stderr)

        consecutive_failures = cfg.prior_consecutive_failures + 1
        print(
            f"Fallimento consecutivo n. {consecutive_failures} "
            f"(soglia di notifica: {cfg.failure_notify_threshold}).",
            file=sys.stderr,
        )

        # Email solo quando si raggiunge esattamente la soglia: una sola
        # notifica per ogni serie di fallimenti consecutivi, non una ad ogni
        # tentativo (lo script viene invocato ogni 10 minuti).
        if consecutive_failures == cfg.failure_notify_threshold:
            try:
                send_email(
                    cfg.smtp_host,
                    cfg.smtp_port,
                    cfg.smtp_user,
                    cfg.smtp_app_password,
                    cfg.notify_email_to,
                    subject=(
                        f"[Il Fatto Quotidiano] Download fallito {consecutive_failures} volte di fila "
                        f"({today.isoformat()})"
                    ),
                    body=(
                        f"Il job di download/upload e' fallito {consecutive_failures} volte consecutive "
                        f"per l'edizione del {today.isoformat()}.\n\n"
                        f"Ultimo errore:\n{error_text}"
                    ),
                )
            except Exception as notify_exc:
                print(f"Invio email di notifica fallito: {notify_exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
