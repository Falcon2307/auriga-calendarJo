from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import requests
import os

load_dotenv()

USERNAME = os.getenv("AURIGA_USERNAME")
PASSWORD = os.getenv("AURIGA_PASSWORD")

TOKEN = None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    def log_request(request):
        global TOKEN

        auth = request.headers.get("authorization")

        if auth and auth.lower().startswith("bearer "):
            TOKEN = auth.split(" ", 1)[1]

    page.on("request", log_request)

    print("Opening Auriga...")

    page.goto(
        "https://isaesupaero-production.np-auriga.nfrance.net/",
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.wait_for_load_state("networkidle")

    print("Clicking SSO button...")
    page.get_by_text("SSO ISAE-SUPAERO").click()

    page.wait_for_timeout(5000)
    print("Current URL:", page.url)
    page.screenshot(path="debug.png")

    print("Entering username...")
    page.locator("#username").fill(USERNAME)

    print("Entering password...")
    page.locator("#password").fill(PASSWORD)

    print("Clicking login button...")
    page.get_by_role("button", name="Se connecter").click()

    page.wait_for_timeout(5000)

    print("Opening Mon planning...")

    page.locator(
        '[data-cy="menu-entry-title-APP_000_040_PLANNING"]'
    ).click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(10000)

    if not TOKEN:
        print("ERROR: Token not found")
        browser.close()
        raise SystemExit(1)

    print("Token captured successfully")

    today = date.today()
    end_date = today + timedelta(days=180)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "accept": "application/json",
    }

    print(
        f"Requesting planning from "
        f"{today.isoformat()} "
        f"to "
        f"{end_date.isoformat()}"
    )

    response = requests.get(
        "https://isaesupaero-production.np-auriga.nfrance.net/api/plannings/me",
        params={
            "startDate": today.isoformat(),
            "endDate": end_date.isoformat(),
        },
        headers=headers,
        timeout=60,
    )

    print("STATUS:", response.status_code)

    with open("planning_full.json", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("planning_full.json saved")

    browser.close()