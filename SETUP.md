# Setup (operazioni manuali una tantum)

## 1. Google Drive — Service Account

1. Vai su [Google Cloud Console](https://console.cloud.google.com/) e crea (o riusa) un progetto.
2. Abilita la **Google Drive API** per il progetto.
3. Crea un **Service Account** (IAM e amministrazione → Service Account → Crea).
4. Nella scheda "Chiavi" del service account, crea una **nuova chiave JSON** e scaricala.
5. Prendi nota dell'indirizzo email del service account (tipo `nome@progetto.iam.gserviceaccount.com`).

## 2. Condividi la cartella Drive

1. Apri la cartella `ilFattoQuotidiano` su Google Drive.
2. Condividila con l'email del service account, ruolo **Editor**.
3. Recupera l'ID della cartella dall'URL: `https://drive.google.com/drive/folders/<QUESTO_E_IL_FOLDER_ID>`.

## 3. Gmail App Password (per le notifiche email)

1. Abilita la verifica in due passaggi sul tuo account Google, se non gia' attiva.
2. Vai su [Password per le app](https://myaccount.google.com/apppasswords) e creane una nuova (es. nome "ifq-downloader").
3. Copia la password generata (16 caratteri): servira' come `SMTP_APP_PASSWORD`.

## 4. Secrets del repository GitHub

In `Settings → Secrets and variables → Actions → New repository secret`, crea:

| Secret | Valore |
|---|---|
| `IFQ_USERNAME` | email/username di accesso a ilfattoquotidiano.it |
| `IFQ_PASSWORD` | password di accesso a ilfattoquotidiano.it |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | contenuto completo del file JSON della chiave del service account |
| `GDRIVE_FOLDER_ID` | ID della cartella `ilFattoQuotidiano` (punto 2) |
| `SMTP_USER` | il tuo indirizzo Gmail |
| `SMTP_APP_PASSWORD` | la app password generata al punto 3 |
| `NOTIFY_EMAIL_TO` | indirizzo email a cui ricevere le notifiche di errore (puo' coincidere con `SMTP_USER`) |

## 5. Primo test

1. Vai su `Actions → Download quotidiano e upload su Drive → Run workflow` per un test manuale immediato (non aspetta le 06:00).
2. Controlla i log del job e che il PDF compaia nella cartella Drive.
3. Il cron schedulato gira automaticamente ogni giorno alle 06:00 (Europe/Rome).
