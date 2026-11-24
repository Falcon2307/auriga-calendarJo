import json
from icalendar import Calendar, Event
from datetime import datetime


def get_schedule():
    with open("planning_full.json", "r", encoding="utf-8") as f:
        return json.load(f)


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
        except Exception:
            pass

        description = item.get("description", "")

        room = ""

        try:
            room = (
                item["interventionResources"][0]
                ["resource"]["caption"]["fr"]
            )
        except Exception:
            pass

        instructors = []

        try:
            for inst in item["interventionInstructors"]:
                person = inst["person"]

                instructors.append(
                    f'{person["currentFirstName"]} '
                    f'{person["currentLastName"]}'
                )

        except Exception:
            pass

        if instructors:
            description += (
                "\n\nInstructor(s): "
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
    print("Reading planning.json...")

    data = get_schedule()

    print(
        f'Found {len(data["interventions"])} events'
    )

    calendar = build_calendar(data)

    with open("calendar.ics", "wb") as f:
        f.write(calendar.to_ical())

    print("calendar.ics generated successfully")


if __name__ == "__main__":
    main()