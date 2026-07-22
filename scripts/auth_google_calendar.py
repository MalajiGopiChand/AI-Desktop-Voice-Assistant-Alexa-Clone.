"""One-time Google Calendar OAuth setup. Requires credentials.json in project root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_SCOPES


def main():
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print("ERROR: credentials.json not found.")
        print("Steps:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create project → Enable Google Calendar API")
        print("  3. Create OAuth 2.0 Desktop credentials")
        print("  4. Download as credentials.json → place in project root")
        sys.exit(1)

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_SCOPES)
    creds = flow.run_local_server(port=0)
    with open(GOOGLE_TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"Success! Token saved to {GOOGLE_TOKEN_FILE}")
    print("JARVIS can now access your Google Calendar.")


if __name__ == "__main__":
    main()
