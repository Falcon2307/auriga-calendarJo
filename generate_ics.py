from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests


API_URL = "https://isaesupaero-production.np-auriga.nfrance.net/api/plannings/me"


def get_token():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

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

        browser.close()

    if "token" not in token_holder:
        raise Exception(
            "No bearer token found. Run login.py again."
        )

    return token_holder["token"]


def get_schedule(token):

    today = datetime.now().date()

    end_date = today + timedelta(days=180)

    headers = {
        "Authorization": f"Bearer {token}",
        "x-scope": "frontend",
        "accept": "application/json"
    }

    response = requests.get(
        API_URL,
        params={
            "startDate": today.isoformat(),
            "endDate": end_date.isoformat(),
        },
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def build_calendar(data):

    cal = Calendar()

    cal.add("prodid", "-//ISAE SUPAERO AURIGA//")
    cal.add("version", "2.0")

    for item in data["interventions"]:

        event = Event()

        title = "Course"

        try:
            title = (
                item["interventionPedagogicalUnits"][0]
                ["pedagogicalUnit"]["caption"]["en"]
            )
        except:
            pass

        description = item.get("description", "")

        room = ""

        try:
            room = (
                item["interventionResources"][0]
                ["resource"]["caption"]["fr"]
            )
        except:
            pass

        instructors = []

        try:
            for inst in item["interventionInstructors"]:
                person = inst["person"]

                instructors.append(
                    f'{person["currentFirstName"]} '
                    f'{person["currentLastName"]}'
                )
        except:
            pass

        if instructors:

            description = (
                description
                + "\n\nInstructor(s): "
                + ", ".join(instructors)
            )

        start = datetime.fromisoformat(
            item["startDateTime"].replace(
                "Z",
                "+00:00"
            )
        )

        end = datetime.fromisoformat(
            item["endDateTime"].replace(
                "Z",
                "+00:00"
            )
        )

        event.add(
            "uid",
            f'{item["id"]}@isae-supaero'
        )

        event.add("summary", title)
        event.add("description", description)
        event.add("location", room)
        event.add("dtstart", start)
        event.add("dtend", end)

        cal.add_component(event)

    return cal


def main():

    print("Getting token...")

    token = get_token()

    print("Getting schedule...")

    data = get_schedule(token)

    print(
        f'Found {len(data["interventions"])} events'
    )

    calendar = build_calendar(data)

    with open("calendar.ics", "wb") as f:
        f.write(calendar.to_ical())

    print("calendar.ics generated successfully")


if __name__ == "__main__":
    main()