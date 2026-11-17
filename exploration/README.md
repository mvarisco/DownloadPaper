# Esplorazione login / download PDF

Esegui questo script **una sola volta, in locale**, per capire come funziona
il login abbonati e il download del PDF dell'edizione odierna. Lo script non
vede né salva mai la tua password: tu fai il login a mano nel browser che si
apre, lo script osserva solo URL e metadati di rete.

## Setup

```bash
cd exploration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Esecuzione

```bash
python explore_login_flow.py
```

Segui le istruzioni stampate a schermo: login manuale, poi apertura/download
del PDF di oggi, poi torna nel terminale e premi Invio.

## Output

- `report.md` — riepilogo leggibile (navigazioni, eventuali download nativi, candidati PDF).
- `network_log.jsonl` — log completo di tutte le risposte di rete osservate (solo URL/metadati, nessun segreto).
- `archive_page_after_login.html` — HTML della pagina archivio dopo il login, utile per individuare il selettore del link/bottone di download. **Può contenere la tua email/account nel menu utente**: non condividerlo pubblicamente.

Quando hai questi file, condividi `report.md` (e se serve un estratto di
`archive_page_after_login.html` intorno al link di download) per proseguire
con l'implementazione del job di produzione.
