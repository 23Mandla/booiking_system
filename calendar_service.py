from datetime import datetime, timezone
import os.path

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
        now = datetime.now(timezone.utc) + "Z"
        print("Getting the upcoming 10 events")
        event_result = (
            service.events()
            .list(
                calendarId = "primary",
                timeMin = now,
                maxResults = 10,
                singleEvents = True,
                orderBy = "startTime"
            ).execute()
        )
        events = event_result.get("items", [])
        if not events:
            print("No upcoming event found.")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
    pass

if __name__ == "__main__":
    main()