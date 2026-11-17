"""Upload su Google Drive via Service Account e pulizia dei file piu' vecchi."""
from __future__ import annotations

import io
import json
from datetime import datetime, timedelta, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _build_service(service_account_json: str):
    info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def upload_pdf(service_account_json: str, folder_id: str, filename: str, content: bytes) -> str:
    service = _build_service(service_account_json)

    # Idempotenza: se un file con lo stesso nome esiste gia' nella cartella, non lo ricarica.
    existing = service.files().list(
        q=f"'{folder_id}' in parents and name = '{filename}' and trashed = false",
        fields="files(id, name)",
    ).execute()
    if existing.get("files"):
        return existing["files"][0]["id"]

    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/pdf", resumable=False)
    file_metadata = {"name": filename, "parents": [folder_id]}
    created = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return created["id"]


def cleanup_old_files(service_account_json: str, folder_id: str, retention_days: int) -> list[str]:
    service = _build_service(service_account_json)
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
