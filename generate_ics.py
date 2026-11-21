from dotenv import load_dotenv
import os
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests
load_dotenv()

TOKEN_URL = os.getenv("TOKEN_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


API_URL = "https://isaesupaero-production.np-auriga.nfrance.net/api/plannings/me"

def get_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": REFRESH_TOKEN,
        },
        timeout=30,
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    response.raise_for_status()

    return response.json()["access_token"]


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