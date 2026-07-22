"""Google Calendar integration — requires credentials.json from Google Cloud."""
import os
from datetime import datetime, timedelta
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_SCOPES


def _get_service():
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        return None, (
            "Google Calendar not set up. Place credentials.json in project root, "
            "then run: python scripts/auth_google_calendar.py"
        )

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None, "Install google calendar packages: pip install google-auth google-auth-oauthlib google-api-python-client"

    creds = None
    if os.path.exists(GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return None, "Calendar token expired. Run: python scripts/auth_google_calendar.py"

    service = build("calendar", "v3", credentials=creds)
    return service, None


def list_upcoming_events(max_results=5):
    service, err = _get_service()
    if err:
        return [], err

    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary", timeMin=now, maxResults=max_results,
        singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        return [], "No upcoming events on your calendar."

    lines = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        lines.append(f"{e.get('summary', 'Event')} at {start}")
    return lines, "\n".join(lines)


def create_reminder(title, minutes_from_now=30):
    service, err = _get_service()
    if err:
        return False, err

    start = datetime.utcnow() + timedelta(minutes=minutes_from_now)
    end = start + timedelta(minutes=15)
    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat() + "Z", "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat() + "Z", "timeZone": "UTC"},
        "reminders": {"useDefault": True},
    }
    service.events().insert(calendarId="primary", body=event).execute()
    return True, f"Reminder '{title}' set for {minutes_from_now} minutes from now."
