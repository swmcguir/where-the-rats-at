"""Visit the deployed Streamlit app and wake it up if it has gone to sleep.

Streamlit Community Cloud puts free-tier apps to sleep after ~12 hours
without visitors. A plain HTTP ping does not count as a visit (the app
tracks real browser/websocket sessions), so this script loads the page in
headless Chromium, clicks the wake-up button when present, and stays on
the page until the app has actually rendered.

Run on a schedule (see .github/workflows/keep-alive.yml).
"""

import os
import re
import sys

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "https://chicago-rats.streamlit.app")


def main() -> int:
    with sync_playwright() as p:
        # CHROMIUM_PATH lets environments with a preinstalled browser skip
        # `playwright install`
        browser = p.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_PATH") or None
        )
        page = browser.new_page()
        print(f"Visiting {APP_URL} ...")
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(5_000)

        # Sleep screen shows a button like "Yes, get this app back up!"
        wake_button = page.get_by_role("button").filter(
            has_text=re.compile(r"back up|wake", re.IGNORECASE)
        )
        if wake_button.count() > 0:
            print("App is asleep - clicking the wake-up button.")
            wake_button.first.click()
        else:
            print("No wake-up button found - app appears to be awake.")

        # Wait until the Streamlit app shell actually renders, so the visit
        # registers as a real session. Waking from sleep can take a while.
        try:
            page.wait_for_selector('[data-testid="stApp"]', timeout=180_000)
            print("App rendered successfully.")
            status = 0
        except Exception:
            print("App did not render within 3 minutes.", file=sys.stderr)
            status = 1

        # Linger briefly so the session is counted.
        page.wait_for_timeout(10_000)
        browser.close()
    return status


if __name__ == "__main__":
    sys.exit(main())
