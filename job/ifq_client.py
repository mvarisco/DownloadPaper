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

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://shop.ilfattoquotidiano.it/login/"
ARCHIVE_URL = "https://www.ilfattoquotidiano.it/in-edicola/edizione/"
BASE_URL = "https://www.ilfattoquotidiano.it"


class LoginFailedError(RuntimeError):
    pass


class EditionNotFoundError(RuntimeError):
    pass


def download_today_pdf(username: str, password: str, target_date: date) -> bytes:
    date_str = target_date.isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)
        page.fill("#username", username)
        page.fill("#password", password)
        page.click('button[name="login"]')
        page.wait_for_load_state("domcontentloaded")

        error_locator = page.locator(".woocommerce-error")
        if error_locator.count() > 0:
            message = error_locator.first.inner_text().strip()
            browser.close()
            raise LoginFailedError(f"Login fallito: {message}")

        page.goto(ARCHIVE_URL)
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
