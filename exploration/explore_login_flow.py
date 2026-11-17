"""
Script di esplorazione locale (NON per CI, solo da eseguire a mano sul tuo computer).

Scopo: capire come funziona il login abbonati su ilfattoquotidiano.it e come si
ottiene il PDF dell'edizione del giorno, SENZA che questo script veda o salvi
mai la tua password.

Come funziona:
1. Apre un browser Chromium visibile (non headless).
2. Tu fai login manualmente nel browser, con le tue credenziali, come faresti
   normalmente.
3. Lo script osserva solo URL/metadati del traffico di rete (mai il body delle
   richieste, quindi mai la password che invii al login) e li salva per
   analisi.
4. Quando hai aperto/scaricato il PDF dell'edizione odierna, torni nel
   terminale e premi Invio: lo script scrive un report in questa cartella.

Uso:
    pip install -r requirements.txt
    playwright install chromium
    python explore_login_flow.py
"""

import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ARCHIVE_URL = "https://www.ilfattoquotidiano.it/in-edicola/edizione/"
OUTPUT_DIR = Path(__file__).parent
NETWORK_LOG_PATH = OUTPUT_DIR / "network_log.jsonl"
REPORT_PATH = OUTPUT_DIR / "report.md"
ARCHIVE_HTML_PATH = OUTPUT_DIR / "archive_page_after_login.html"

PDF_CONTENT_TYPES = ("application/pdf",)


def is_pdf_response(url: str, content_type: str) -> bool:
    return content_type.lower().startswith(PDF_CONTENT_TYPES) or url.lower().split("?")[0].endswith(".pdf")


def main() -> None:
    events: list[dict] = []
    navigations: list[dict] = []
    downloads: list[dict] = []

    def record_response(response):
        try:
            content_type = response.headers.get("content-type", "")
        except Exception:
            content_type = ""
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "url": response.url,
            "status": response.status,
            "content_type": content_type,
            "is_pdf_candidate": is_pdf_response(response.url, content_type),
        }
        events.append(entry)

    def record_navigation(frame):
        if frame.parent_frame is None:
            navigations.append({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "url": frame.url,
            })

    def attach_listeners(page):
        page.on("response", record_response)
        page.on("framenavigated", record_navigation)
        page.on("download", lambda d: downloads.append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "url": d.url,
            "suggested_filename": d.suggested_filename,
        }))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.on("page", attach_listeners)

        page = context.new_page()
        attach_listeners(page)

        print("=" * 70)
        print("ISTRUZIONI")
        print("=" * 70)
        print(f"1. Il browser aprira' {ARCHIVE_URL}")
        print("2. Chiudi/accetta il banner cookie se compare.")
        print("3. Clicca su 'accedi' / 'ABBONATI' e fai login con le tue credenziali")
        print("   (le credenziali le digiti SOLO nel sito, questo script non le vede).")
        print("4. Torna sulla pagina archivio edizioni e apri/scarica il PDF")
        print("   dell'edizione di oggi (quello che normalmente fai da browser).")
        print("5. Quando hai finito, torna qui nel terminale e premi Invio.")
        print("=" * 70)

        page.goto(ARCHIVE_URL)

        input("\nPremi Invio quando hai completato login e apertura/download del PDF...\n")

        # Salva l'HTML della pagina corrente per analizzare i selettori del link di download.
        try:
            ARCHIVE_HTML_PATH.write_text(page.content(), encoding="utf-8")
        except Exception as exc:
            print(f"Avviso: non sono riuscito a salvare l'HTML della pagina: {exc}")

        browser.close()

    with NETWORK_LOG_PATH.open("w", encoding="utf-8") as f:
        for entry in events:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    pdf_candidates = [e for e in events if e["is_pdf_candidate"]]

    report_lines = [
        "# Report esplorazione login / download PDF",
        "",
        f"Generato il {datetime.now().isoformat(timespec='seconds')}.",
        "",
        "Questo report NON contiene password, cookie o altri segreti: sono stati",
        "registrati solo URL e metadati di rete.",
        "",
        "## Navigazioni pagina principale (in ordine)",
        "",
    ]
    for nav in navigations:
        report_lines.append(f"- `{nav['ts']}` {nav['url']}")

    report_lines += ["", "## Download nativi del browser rilevati", ""]
    if downloads:
        for d in downloads:
            report_lines.append(f"- `{d['ts']}` {d['url']} (suggested filename: {d['suggested_filename']})")
    else:
        report_lines.append("- Nessuno (il PDF probabilmente si apre in una pagina/viewer invece che scaricarsi direttamente).")

    report_lines += ["", "## Candidati PDF osservati nel traffico di rete", ""]
    if pdf_candidates:
        for c in pdf_candidates:
            report_lines.append(f"- `{c['ts']}` {c['url']} (status {c['status']}, content-type `{c['content_type']}`)")
    else:
        report_lines.append("- Nessun candidato PDF individuato automaticamente: controlla manualmente `network_log.jsonl`.")

    report_lines += [
        "",
        "## File aggiuntivi generati",
        "",
        f"- `{NETWORK_LOG_PATH.name}`: log completo di tutte le risposte di rete osservate.",
        f"- `{ARCHIVE_HTML_PATH.name}`: HTML della pagina archivio al termine della sessione",
        "  (puo' contenere la tua email/account nel menu utente: non condividerlo pubblicamente,",
        "  usalo solo per individuare il selettore del link/bottone di download).",
        "",
    ]

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\nFatto. Report scritto in: {REPORT_PATH}")
    print(f"Log di rete completo in: {NETWORK_LOG_PATH}")
    print(f"HTML pagina in: {ARCHIVE_HTML_PATH}")


if __name__ == "__main__":
    main()
