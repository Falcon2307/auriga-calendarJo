from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  

    page = browser.new_page()

    page.goto(
        "https://isaesupaero-production.np-auriga.nfrance.net"
    )

    input(
        "\nLog in completely, open your timetable, then press ENTER\n"
    )

    page.context.storage_state(path="storage_state.json")

    browser.close()

print("Session saved")