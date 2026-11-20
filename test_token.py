from playwright.sync_api import sync_playwright
import requests

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        storage_state="storage_state.json"
    )

    page = context.new_page()

    token_holder = {}

    def intercept(request):

        auth = request.headers.get("authorization")

        if auth and auth.startswith("Bearer "):
            token_holder["token"] = auth[7:]

    page.on("request", intercept)

    page.goto(
        "https://isaesupaero-production.np-auriga.nfrance.net"
    )

    page.wait_for_timeout(5000)

    token = token_holder["token"]

    print("Token captured!")

    headers = {
        "Authorization": f"Bearer {token}",
        "x-scope": "frontend",
        "accept": "application/json"
    }

    r = requests.get(
        "https://isaesupaero-production.np-auriga.nfrance.net/api/plannings/me",
        params={
            "startDate": "2026-11-16",
            "endDate": "2026-11-22",
            "days": [1, 2, 3, 4, 5, 6, 7]
        },
        headers=headers
    )

    print("API STATUS:", r.status_code)

    print(r.text[:500])

    browser.close()