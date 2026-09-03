#!/usr/bin/env python3
from __future__ import print_function
import argparse
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import timezone

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except ValueError:
            print("Invalid token.json file. Re-authenticating...")
            creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    args = parser.parse_args()

    if args.date:
        target = datetime.datetime.strptime(args.date, '%Y-%m-%d').astimezone()
    else:
        target = datetime.datetime.now().astimezone()

    start_of_day = target.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = target.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary', timeMin=start_of_day,
                                          timeMax=end_of_day, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No events found for today.')
    else:
        print('Today\'s events:')
        for event in events:
            if event.get('eventType') == 'default' or event.get('eventType') == 'focusTime':
                print(f" - {event['summary']}")

if __name__ == '__main__':
    main()
