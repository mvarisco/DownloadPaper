"""Upload su Google Drive via OAuth2 (account utente) e pulizia dei file piu' vecchi.

I Service Account non hanno quota di storage su un Google Drive personale
(non-Workspace): possono scrivere solo su Shared Drive, feature a pagamento.
Per questo si usa OAuth2 con un refresh token dell'account utente (vedi
../setup/generate_refresh_token.py).
"""
from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def build_service(client_id: str, client_secret: str, refresh_token: str):
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def file_exists(service, folder_id: str, filename: str) -> bool:
    """Controllo di idempotenza: True se un file con questo nome e' gia' nella cartella.

    Chiamato prima di login+download cosi' le invocazioni ripetute ogni 10
    minuti (vedi il workflow) non rifanno login ne' avviano Playwright una
    volta che l'edizione del giorno e' gia' stata caricata.
    """
    existing = service.files().list(
        q=f"'{folder_id}' in parents and name = '{filename}' and trashed = false",
        fields="files(id, name)",
    ).execute()
    return bool(existing.get("files"))


def upload_pdf(service, folder_id: str, filename: str, content: bytes) -> str:
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/pdf", resumable=False)
    file_metadata = {"name": filename, "parents": [folder_id]}
    created = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return created["id"]


def cleanup_old_files(service, folder_id: str, retention_days: int) -> list[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false and createdTime < '{cutoff_str}'",
        fields="files(id, name, createdTime)",
    ).execute()

    deleted_names = []
    for file in results.get("files", []):
        service.files().delete(fileId=file["id"]).execute()
        deleted_names.append(file["name"])
    return deleted_names
