from flask import Flask, Response
from icalendar import Calendar, Event
from dotenv import load_dotenv
import os
import requests

from datetime import datetime, timedelta


load_dotenv()
print("TOKEN_URL =", os.getenv("TOKEN_URL"))
print("CLIENT_ID =", os.getenv("CLIENT_ID"))
print("REFRESH_TOKEN loaded =", bool(os.getenv("REFRESH_TOKEN")))
TOKEN_URL = os.getenv("TOKEN_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


API_URL = "https://isaesupaero-production.np-auriga.nfrance.net/api/plannings/me"

app = Flask(__name__)


def get_access_token():

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

    data = response.json()

    return data["access_token"]



def get_calendar_json():

    token = get_access_token()

    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=180)

    response = requests.get(
        API_URL,
        params={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=30,
    )
    print("Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()


@app.route("/calendar.ics")
def calendar_feed():

    data = get_calendar_json()

    cal = Calendar()
    cal.add("prodid", "-//Auriga ICS//")
    cal.add("version", "2.0")

    for item in data["interventions"]:

        event = Event()

        course = item["interventionPedagogicalUnits"][0][
        "pedagogicalUnit"
        ]["caption"]["en"]

        description = item.get("description", "")

        room = ""

        if item["interventionResources"]:
            room = item["interventionResources"][0][
                "resource"
            ]["caption"]["fr"]

        event.add(
            "uid",
            f'{item["id"]}@auriga'
        )

        event.add("summary", course)
        event.add("description", description)
        event.add("location", room)

        event.add(
            "dtstart",
            datetime.fromisoformat(
                item["startDateTime"].replace("Z", "+00:00")
            ),
        )

        event.add(
            "dtend",
            datetime.fromisoformat(
                item["endDateTime"].replace("Z", "+00:00")
            ),
        )

        cal.add_component(event)

    return Response(
        cal.to_ical(),
        mimetype="text/calendar",
    )


if __name__ == "__main__":
    app.run(debug=True)