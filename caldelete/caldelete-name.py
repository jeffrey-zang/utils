from __future__ import print_function

import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete the existing token.json
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Array of strings to search for in event titles
# Modify this array to include the strings you want to match
STRINGS_TO_DELETE = [
    "CS 135",
    "ECON 101"
]


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


def contains_target_strings(event_title, target_strings):
    """Check if event title contains any of the target strings (case-insensitive)"""
    if not event_title:
        return False
    
    event_title_lower = event_title.lower()
    for target_string in target_strings:
        if target_string.lower() in event_title_lower:
            return True
    return False


def list_events_on_date(service, calendar_id, target_date):
    """List all events on a specific date for debugging purposes"""
    print(f"\n=== DEBUG: All events on {target_date} ===")
    
    # Create time range for the specific date
    start_time = f"{target_date}T00:00:00Z"
    end_time = f"{target_date}T23:59:59Z"
    
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print(f"No events found on {target_date}")
        else:
            print(f"Found {len(events)} events on {target_date}:")
            for i, event in enumerate(events, 1):
                title = event.get('summary', 'No title')
                start = event.get('start', {})
                
                if 'dateTime' in start:
                    start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    time_str = start_time.strftime('%H:%M')
                elif 'date' in start:
                    time_str = 'All day'
                else:
                    time_str = 'No time'
                
                print(f"  {i}. {title} ({time_str})")
                print(f"     Event ID: {event.get('id', 'No ID')}")
                
                # Check if this event would match our search criteria
                if contains_target_strings(title, STRINGS_TO_DELETE):
                    print(f"     *** MATCHES search criteria! ***")
                else:
                    print(f"     Does not match search criteria")
                print()
    
    except Exception as e:
        print(f"Error fetching events for {target_date}: {e}")
    
    print("=== END DEBUG ===\n")


def main():
    creds = get_creds()
    service = build("calendar", "v3", credentials=creds)

    CALENDAR_ID = "primary"

    print(f"Searching for events containing any of these strings: {STRINGS_TO_DELETE}")
    print("=" * 50)

    # Debug: List all events on October 20, 2025
    list_events_on_date(service, CALENDAR_ID, "2025-10-20")

    # Get all events from the calendar with a proper time range
    # Set a wide time range to capture all events (past and future)
    from datetime import datetime, timedelta
    
    # Get events from 1 year ago to 2 years in the future
    time_min = (datetime.now() - timedelta(days=365)).isoformat() + 'Z'
    time_max = (datetime.now() + timedelta(days=730)).isoformat() + 'Z'
    
    print(f"Searching events from {time_min} to {time_max}")
    
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime',
        maxResults=2500  # Increase max results
    ).execute()
    events = events_result.get("items", [])

    # Filter events that contain any of the target strings
    matching_events = []
    for event in events:
        event_title = event.get('summary', '')
        if contains_target_strings(event_title, STRINGS_TO_DELETE):
            matching_events.append(event)

    if not matching_events:
        print("No events found containing the specified strings.")
    else:
        print(f"Found {len(matching_events)} events containing the specified strings:")
        print()
        
        # Show events that will be deleted
        for event in matching_events:
            event_title = event.get('summary', 'No title')
            event_start = event.get('start', {})
            
            # Get event date/time for display
            if 'dateTime' in event_start:
                event_datetime = datetime.fromisoformat(
                    event_start['dateTime'].replace('Z', '+00:00'))
                date_str = event_datetime.strftime('%Y-%m-%d %H:%M')
            elif 'date' in event_start:
                date_str = event_start['date']
            else:
                date_str = 'No date'
            
            print(f"- {event_title} ({date_str})")
        
        print()
        confirmation = input("Do you want to delete these events? (y/N): ")
        
        if confirmation.lower() in ['y', 'yes']:
            print("\nDeleting events...")
            deleted_count = 0
            
            for event in matching_events:
                try:
                    service.events().delete(calendarId=CALENDAR_ID,
                                          eventId=event["id"]).execute()
                    event_title = event.get('summary', 'No title')
                    print(f"✓ Deleted: {event_title}")
                    deleted_count += 1
                except Exception as e:
                    event_title = event.get('summary', 'No title')
                    print(f"✗ Failed to delete: {event_title} - Error: {e}")
            
            print(f"\nSuccessfully deleted {deleted_count} out of {len(matching_events)} events.")
        else:
            print("Deletion cancelled.")


if __name__ == "__main__":
    main()