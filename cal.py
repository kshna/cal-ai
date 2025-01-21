import os
import pickle
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pytz

# If modifying the calendar, define the SCOPES
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# The ID of the calendar to access
CALENDAR_ID = 'primary'  # Use 'primary' for the primary calendar

# Path to store the pickle file
PICKLE_FILE = 'calendar_events.tmp'

def authenticate_google_account():
    """Authenticate the user and return the service object."""
    creds = None
    # The token.pickle file stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_zoom_link_from_event(event):
    """Extract Zoom link from the event description (if it exists)."""
    description = event.get('description', '')
    # Look for a Zoom link (common pattern is "https://zoom.us/j/123456789")
    zoom_url = None
    if "zoom.us" in description:
        for line in description.split("\n"):
            if "zoom.us" in line:
                zoom_url = line.strip()
                break
    return zoom_url

def get_today_events(service):
    """Fetch today's events from Google Calendar."""
    now = datetime.now(pytz.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Format the start and end time in RFC3339 format
    time_min = start_of_day.isoformat()
    time_max = end_of_day.isoformat()

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events

def store_events_in_pickle(events):
    """Store events in a pickle file."""
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(events, f)

def load_events_from_pickle():
    """Load events from a pickle file."""
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            events = pickle.load(f)
        return events
    return None

def open_zoom_links(events):
    """Iterate over events and open any Zoom URLs found within 20 seconds of start time."""
    now = datetime.now(timezone.utc)  # Current time in UTC
    for event in events:
        event_start = event['start'].get('dateTime')
        if event_start:
            event_start = datetime.fromisoformat(event_start) 

            tmp_file = str(event_start.timestamp()) + ".tmp"
            if os.path.exists(tmp_file):
                pass
            else:
                time_diff = event_start - now
                print(time_diff)
                # Check if the event starts within the next 20 seconds
                if timedelta(seconds=0) <= time_diff <= timedelta(seconds=20):
                    zoom_url = get_zoom_link_from_event(event)
                    with open(tmp_file,'w') as f:
                        f.write('.')
                    if zoom_url:
                        print(f"Zoom link found and event starts in {time_diff.seconds} seconds: {zoom_url}")
                        webbrowser.open(zoom_url)  # Opens the Zoom link in the default web browser

def main():
    """Main function to authenticate, fetch events, and store/retrieve them from pickle."""
    # Check if the events are already stored in pickle
    events = load_events_from_pickle()

    if not events:
        print('Fetching events from Google Calendar...')
        service = authenticate_google_account()
        events = get_today_events(service)

        if not events:
            print('No events found for today.')
        else:
            print('Found events for today:')
            for event in events:
                print(f"Event: {event['summary']} at {event['start']['dateTime']}")

            # Store events in pickle file
            store_events_in_pickle(events)
    else:
        print('Loaded events from pickle file:')
        for event in events:
            print(f"Event: {event['summary']} at {event['start']['dateTime']}")

    # Open Zoom links for events starting within 20 seconds
    open_zoom_links(events)

if __name__ == '__main__':
    main()

