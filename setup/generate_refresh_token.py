"""Genera un refresh token OAuth2 per il tuo account Google personale (una tantum, locale).

Serve perche' un Service Account non ha quota di storage su un Drive personale
(non-Workspace): bisogna autenticarsi come utente vero tramite OAuth2.

Prerequisiti:
1. Nel progetto Google Cloud (stesso usato per abilitare la Drive API), vai su
   "API e servizi" -> "Credenziali" -> "Crea credenziali" -> "ID client OAuth".
   Tipo di applicazione: "App desktop". Scarica il JSON e salvalo qui come
   client_secret.json (ignorato da git).
2. pip install -r requirements.txt

Uso:
    python generate_refresh_token.py

Si apre il browser: fai login con l'account Google che possiede la cartella
Drive "ilFattoQuotidiano" e concedi il permesso. Lo script stampa a schermo
client_id, client_secret e refresh_token da copiare nei secrets GitHub
(GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN).
"""
from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CLIENT_SECRET_PATH = Path(__file__).parent / "client_secret.json"


def main() -> None:
    if not CLIENT_SECRET_PATH.exists():
        raise SystemExit(
            f"File non trovato: {CLIENT_SECRET_PATH}. Scarica il client ID OAuth 'App desktop' "
            "dalla Google Cloud Console e salvalo con questo nome in questa cartella."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    credentials = flow.run_local_server(port=0)

    print("\nSalva questi valori come secrets del repository GitHub:\n")
    print(f"GDRIVE_CLIENT_ID={credentials.client_id}")
    print(f"GDRIVE_CLIENT_SECRET={credentials.client_secret}")
    print(f"GDRIVE_REFRESH_TOKEN={credentials.refresh_token}")


if __name__ == "__main__":
    main()
