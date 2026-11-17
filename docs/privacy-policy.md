# Informativa sulla privacy — IFQ Downloader

Ultimo aggiornamento: 2026-11-17.

Questa applicazione è un progetto personale, non distribuito pubblicamente e
usato da un solo utente (l'autore), per automatizzare il download
dell'edizione digitale quotidiana a cui è abbonato e il suo salvataggio su un
Google Drive personale.

## Dati trattati

- **Credenziali di ilfattoquotidiano.it**: usate solo per autenticarsi sul
  sito durante l'esecuzione del processo automatico; non vengono condivise
  con terze parti né salvate al di fuori dei secrets cifrati di GitHub
  Actions.
- **Accesso a Google Drive**: l'app richiede lo scope
  `https://www.googleapis.com/auth/drive.file`, che consente di accedere
  esclusivamente ai file creati dall'app stessa, non all'intero Drive
  dell'utente.
- Nessun dato viene condiviso, venduto o trasmesso a terze parti. L'unico
  output del processo è il file PDF dell'edizione del giorno, salvato nel
  Google Drive dello stesso utente che possiede le credenziali.

## Contatti

Per qualsiasi domanda su questo progetto, contattare l'autore tramite il
repository GitHub in cui è pubblicato questo codice.
