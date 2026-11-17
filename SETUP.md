# Setup (operazioni manuali una tantum)

## 1. Google Drive API

1. Vai su [Google Cloud Console](https://console.cloud.google.com/) e crea (o riusa) un progetto.
2. Abilita la **Google Drive API** per il progetto (API e servizi → Libreria → cerca "Google Drive API" → Abilita).

## 2. Credenziali OAuth2 (account utente, non Service Account)

> Un Service Account non ha quota di storage su un Drive personale (non-Workspace):
> puo' scrivere file solo su uno Shared Drive, feature a pagamento. Per questo si
> usa OAuth2 con il tuo account Google normale.

1. "API e servizi" → "Schermata consenso OAuth" (o "Google Auth Platform" → scheda "Audience"): tipo **Esterno**, compila i campi minimi richiesti, e aggiungi il tuo indirizzo Google come **utente di test**.
2. "API e servizi" → "Credenziali" → "Crea credenziali" → **"ID client OAuth"** → tipo applicazione **"App desktop"** → crea.
3. Scarica il JSON delle credenziali e salvalo come `setup/client_secret.json` (è ignorato da git, non verrà mai committato).
4. **Pubblica l'app** (necessario per evitare che il refresh token scada dopo 7 giorni, limite delle app in stato "Testing"):
   - Scheda **"Branding"**: compila Nome app, Email di assistenza utenti, Email di contatto sviluppatore.
   - Scheda **"Data Access"**: aggiungi esplicitamente lo scope `.../auth/drive.file`.
   - Se richiesti un **URL homepage** e un **URL privacy policy**, abilita GitHub Pages per questo repo (`Settings → Pages → Source: Deploy from a branch → main → /docs`) e usa gli URL risultanti, tipicamente:
     - Homepage: `https://<tuo-utente-github>.github.io/DownloadPaper/`
     - Privacy policy: `https://<tuo-utente-github>.github.io/DownloadPaper/privacy-policy.html`
   - Torna sulla scheda **"Audience"** e clicca **"Publish App"**.
5. In locale:
   ```bash
   cd setup
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python generate_refresh_token.py
   ```
6. Si apre il browser: fai login con l'account Google che possiede la cartella `ilFattoQuotidiano`. Poiché l'app non è verificata da Google, comparirà "Google non ha verificato questa app": clicca **"Avanzate"** → **"Vai su [nome app] (non sicuro)"**, poi concedi il permesso.
7. Lo script stampa `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET`, `GDRIVE_REFRESH_TOKEN`: tienili a portata di mano per il punto 4 più sotto.

## 3. Recupera l'ID della cartella Drive

Apri la cartella `ilFattoQuotidiano` su Google Drive e prendi l'ID dall'URL:
`https://drive.google.com/drive/folders/<QUESTO_E_IL_FOLDER_ID>`.

## 4. Gmail App Password (per le notifiche email)

1. Abilita la verifica in due passaggi sul tuo account Google, se non gia' attiva.
2. Vai su [Password per le app](https://myaccount.google.com/apppasswords) e creane una nuova (es. nome "ifq-downloader").
3. Copia la password generata (16 caratteri): servira' come `SMTP_APP_PASSWORD`.

## 5. Secrets del repository GitHub

In `Settings → Secrets and variables → Actions → New repository secret` (**non** "Codespaces", sono due contenitori separati), crea:

| Secret | Valore |
|---|---|
| `IFQ_USERNAME` | email/username di accesso a ilfattoquotidiano.it |
| `IFQ_PASSWORD` | password di accesso a ilfattoquotidiano.it |
| `GDRIVE_CLIENT_ID` | dal punto 2.6 |
| `GDRIVE_CLIENT_SECRET` | dal punto 2.6 |
| `GDRIVE_REFRESH_TOKEN` | dal punto 2.6 |
| `GDRIVE_FOLDER_ID` | ID della cartella `ilFattoQuotidiano` (punto 3) |
| `SMTP_USER` | il tuo indirizzo Gmail |
| `SMTP_APP_PASSWORD` | la app password generata al punto 4 |
| `NOTIFY_EMAIL_TO` | indirizzo email a cui ricevere le notifiche di errore (puo' coincidere con `SMTP_USER`) |

## 6. Primo test

1. Vai su `Actions → Download quotidiano e upload su Drive → Run workflow` per un test manuale immediato (non aspetta le 06:00).
2. Controlla i log del job e che il PDF compaia nella cartella Drive.
3. Il cron schedulato gira automaticamente ogni giorno alle 06:00 (Europe/Rome).

