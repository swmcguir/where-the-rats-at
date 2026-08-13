"""Visit the deployed Streamlit app and wake it up if it has gone to sleep.

Streamlit Community Cloud puts free-tier apps to sleep after ~12 hours
without visitors. A plain HTTP ping does not count as a visit (the app
tracks real browser/websocket sessions), so this script loads the page in
headless Chromium, clicks the wake-up control when present, and stays on
the page until the app has actually rendered.

Run on a schedule (see .github/workflows/keep-alive.yml).
"""

import os
import re
import sys

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "https://chicago-rats.streamlit.app")

# Sleep-page wording, e.g. "Yes, get this app back up!"
WAKE_TEXT = re.compile(r"back up|wake", re.IGNORECASE)

# The rendered Streamlit app shell across versions
APP_SHELL = '[data-testid="stApp"], [data-testid="stAppViewContainer"], .stApp'

# Waking a slept app is a full container cold boot, then this app pulls a
# year of 311 data before rendering - allow plenty of time
RENDER_TIMEOUT_MS = 8 * 60 * 1000


def log(msg, err=False):
    print(msg, file=sys.stderr if err else sys.stdout, flush=True)


def dump_diagnostics(page):
    """Describe what page we actually landed on, for the Actions log."""
    try:
        log(f"DIAGNOSTICS: page title: {page.title()!r}", err=True)
        body = re.sub(r"\s+", " ", page.inner_text("body"))[:600]
        log(f"DIAGNOSTICS: body text starts: {body!r}", err=True)
    except Exception as e:
        log(f"DIAGNOSTICS: could not read page: {e}", err=True)


def main() -> int:
    with sync_playwright() as p:
        # CHROMIUM_PATH lets environments with a preinstalled browser skip
        # `playwright install`
        browser = p.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_PATH") or None
        )
        page = browser.new_page()
        log(f"Visiting {APP_URL} ...")
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(8_000)

        # The sleep screen's wake control is not always a real <button>,
        # so match buttons, links, and button-styled elements by text.
        wake = page.locator("button, a, [role='button']").filter(has_text=WAKE_TEXT)
        # Fallback: the distinctive sleep-page phrase itself ("Yes, get this
        # app back up!"), clicking the last (innermost/latest) match so we
        # don't hit descriptive prose that merely mentions waking.
        wake_text = page.get_by_text(re.compile(r"get this app back up", re.I))
        if wake.count() > 0:
            label = wake.first.inner_text().strip()
            log(f"App is asleep - clicking wake-up control: {label!r}")
            wake.first.click()
        elif wake_text.count() > 0:
            log("App is asleep - clicking wake-up text.")
            wake_text.last.click()
        else:
            log("No wake-up control found - app may already be awake.")

        # Wait until the Streamlit app shell actually renders, so the visit
        # registers as a real session.
        try:
            page.wait_for_selector(APP_SHELL, timeout=RENDER_TIMEOUT_MS)
            log("App rendered successfully.")
            status = 0
        except Exception:
            log(f"App did not render within {RENDER_TIMEOUT_MS // 60000} minutes.",
                err=True)
            dump_diagnostics(page)
            status = 1

        # Linger briefly so the session is counted.
        page.wait_for_timeout(10_000)
        browser.close()
    return status


if __name__ == "__main__":
    sys.exit(main())
