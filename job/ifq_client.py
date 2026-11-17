"""Login su ilfattoquotidiano.it e download del PDF dell'edizione di una data.

Flusso individuato con esplorazione manuale (vedi ../exploration/):
- login WooCommerce standard su https://shop.ilfattoquotidiano.it/login/
  (campi #username, #password, bottone name="login").
- la pagina archivio https://www.ilfattoquotidiano.it/in-edicola/edizione/
  elenca le edizioni con attributi `data-edition-date="YYYY-MM-DD"` e
  `data-href="/ilfattoquotidiano/edition/{id}/download"`.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

LOGIN_URL = "https://shop.ilfattoquotidiano.it/login/"
ARCHIVE_URL = "https://www.ilfattoquotidiano.it/in-edicola/edizione/"
BASE_URL = "https://www.ilfattoquotidiano.it"

# La pagina carica molti script di tracking/ADV: l'evento "load" puo' non
# arrivare mai entro i tempi di default, quindi si aspetta solo il DOM e si
# alza il timeout.
NAVIGATION_TIMEOUT_MS = 60_000

DEBUG_SCREENSHOT_PATH = Path(__file__).parent / "debug_failure_screenshot.png"
DEBUG_HTML_PATH = Path(__file__).parent / "debug_failure_page.html"


class LoginFailedError(RuntimeError):
    pass


class EditionNotFoundError(RuntimeError):
    pass


def _save_debug_artifacts(page: Page) -> None:
    try:
        page.screenshot(path=str(DEBUG_SCREENSHOT_PATH), full_page=True)
        DEBUG_HTML_PATH.write_text(page.content(), encoding="utf-8")
    except Exception:
        pass  # la diagnostica e' solo best-effort, non deve mascherare l'errore originale


def download_today_pdf(username: str, password: str, target_date: date) -> bytes:
    date_str = target_date.isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(NAVIGATION_TIMEOUT_MS)

        try:
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
            page.fill("#username", username)
            page.fill("#password", password)
            page.click('button[name="login"]')
            page.wait_for_load_state("domcontentloaded")
        except Exception:
            _save_debug_artifacts(page)
            browser.close()
            raise

        error_locator = page.locator(".woocommerce-error")
        if error_locator.count() > 0:
            message = error_locator.first.inner_text().strip()
            browser.close()
            raise LoginFailedError(f"Login fallito: {message}")

        try:
            page.goto(ARCHIVE_URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
        except Exception:
            _save_debug_artifacts(page)
            browser.close()
            raise

        edition_locator = page.locator(f'[data-edition-date="{date_str}"]')
        if edition_locator.count() == 0:
            browser.close()
            raise EditionNotFoundError(f"Nessuna edizione trovata per la data {date_str}.")

        href = edition_locator.first.get_attribute("data-href")
        if not href:
            browser.close()
            raise EditionNotFoundError(
                f"Edizione del {date_str} trovata ma senza link di download (verifica l'abbonamento)."
            )

        response = context.request.get(BASE_URL + href)
        content_type = response.headers.get("content-type", "")
        if response.status != 200 or "application/pdf" not in content_type:
            browser.close()
            raise EditionNotFoundError(
                f"Download PDF fallito per {date_str}: status {response.status}, content-type '{content_type}'."
            )

        pdf_bytes = response.body()
        browser.close()
        return pdf_bytes
