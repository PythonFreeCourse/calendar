import os
import pickle
import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials_for_calendar():
    credentials = None
    scopes = ['https://www.googleapis.com/auth/calendar']
    
    if os.path.exists("token.pickle"):
        print("Loading credentials from file..")
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)


    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing Access Token")
            credentials.refresh(Request())
        else:
            print("Fetching new Tokens")
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes=scopes)
            flow.run_local_server(prompt='consent', authorization_prompt_message="")
            credentials = flow.credentials
            with open('token.pickle', 'wb') as f:
                pickle.dump(credentials, f)

    return credentials

c = get_credentials_for_calendar()

cred = Credentials(token=c.token, refresh_token=c.refresh_token, token_uri=c.token_uri, client_id=c.client_id, client_secret=c.client_secret)

cred.refresh(Request())

pass
# service = build('calendar', 'v3', credentials=credentials)

# now = datetime.datetime.utcnow().isoformat() + 'Z'
# print('Getting the upcoming 10 events')
# events_result = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute()
# events = events_result.get('items', [])

# if not events:
#     print('No upcoming events found.')

# for event in events:
#     start = event['start'].get('dateTime', event['start'].get('date'))
#     print(start, event['summary'])