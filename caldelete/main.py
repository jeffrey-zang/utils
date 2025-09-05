from __future__ import print_function

import os.path
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
    # EVENT_TITLEs = ["MATH 115 (LEC)", "MATH 135 (LEC)",
    #                 "SE 101 (LEC)", "MATH 135 (TUT)", "CS 137 (LEC)", "SE 101 (LAB)", "MATH 115 (TUT)", "CHE 102 (TUT)", "CS 137 (LEC)", "GENE 119 (SEM)", "SE 101 (SEM)", "MATH 117 (TUT)", "CS 137 (TUT)"]
    EVENT_TITLEs = ["MATH 117 (LEC)"]

    all_events = []
    for title in EVENT_TITLEs:
        events_result = service.events().list(
            calendarId=CALENDAR_ID, q=title).execute()
        events = events_result.get("items", [])
        all_events.extend(events)

    if not all_events:
        print("No events found.")
    else:
        for event in all_events:
            service.events().delete(calendarId=CALENDAR_ID,
                                    eventId=event["id"]).execute()
            print(f"Deleted: {event['summary']} ({event['id']})")


if __name__ == "__main__":
    main()
