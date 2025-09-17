from __future__ import print_function

import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete the existing token.json
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If no valid token, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the creds for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def main():
    creds = get_creds()
    service = build("calendar", "v3", credentials=creds)

    CALENDAR_ID = "primary"

    # Set the cutoff date (August 20, 2025)
    cutoff_date = datetime(2025, 8, 20)

    # Get all events from the calendar
    events_result = service.events().list(calendarId=CALENDAR_ID).execute()
    events = events_result.get("items", [])

    # Filter events that have default color AND are after August 20, 2025
    default_color_events = []
    for event in events:
        # Check if event has default color (no colorId specified or colorId is None)
        if 'colorId' not in event or event.get('colorId') is None:
            # Check if event is after August 20, 2025
            event_start = event.get('start', {})
            if 'dateTime' in event_start:
                # Event has specific time
                event_datetime = datetime.fromisoformat(
                    event_start['dateTime'].replace('Z', '+00:00'))
                event_date = event_datetime.replace(tzinfo=None)
            elif 'date' in event_start:
                # All-day event
                event_date = datetime.strptime(event_start['date'], '%Y-%m-%d')
            else:
                # Skip events without start date
                continue

            if event_date > cutoff_date:
                default_color_events.append(event)

    if not default_color_events:
        print("No events with default color found after August 20, 2025.")
    else:
        print(
            f"Found {len(default_color_events)} events with default color after August 20, 2025.")
        for event in default_color_events:
            service.events().delete(calendarId=CALENDAR_ID,
                                    eventId=event["id"]).execute()
            event_title = event.get('summary', 'No title')
            print(f"Deleted: {event_title} ({event['id']})")


if __name__ == "__main__":
    main()
