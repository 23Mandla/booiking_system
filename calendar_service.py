from datetime import datetime, timezone
import os.path
import click 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "cal_secrete.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return  build("calendar", "v3", credentials = creds)

def view_calendar_events():
    service = get_calendar_service()
   
    try:
        now = datetime.now(timezone.utc).isoformat()
        print("Getting the upcoming 10 events")
        event_result = (
            service.events()
            .list(
                calendarId = "primary",
                # q = 'Mentor booking system',
                timeMin = now,
                maxResults = 10,
                singleEvents = True,
                orderBy = "startTime"
            ).execute()
        )
        events = event_result.get("items", [])
      
        if not events:
            click.echo("No upcoming event found.")
        
        matching_events = [( event['id'], event['organizer']['email'], event["attendees"], event["start"], event['status']) for event in events if event.get("summary") == 'mentor meeting - functions']

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        print(matching_events)
        return matching_events
    
    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event(topic, description, start_date, end_date, attendees):
    service = get_calendar_service()
    event = {
        'summary' : f'mentor meeting - {topic}',
        'description' : description,
        'color' : 6,
        'start': {
            'dateTime': start_date,
            'timeZone': 'Africa/Johannesburg',
        },
        'end': {
            'dateTime': end_date,
            'timeZone': 'Africa/Johannesburg',
        },
        'attendees' : [
            {'email': {attendees}},
        ],
        'reminders' : {
            'useDefault' : False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        } ,
    }

    event = service.events().insert(calendarId = "primary", body = event).execute()
    return f"Event created : {event.get('htmlLink')}"

if __name__ == "__main__":
    create_event()
