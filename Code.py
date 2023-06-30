from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import date, datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import threading
import pickle

today = date.today()
refresh_interval = timedelta(minutes=50)
def get_credentialscal():
    scope = "https://www.googleapis.com/auth/calendar"
    credentials = None

    # If token file exists and is not empty, load credentials from it
    if os.path.exists("tokencal.pkl") and os.path.getsize("tokencal.pkl") > 0:
        with open("tokencal.pkl", 'rb') as token:
            try:
                credentials = pickle.load(token)
            except (pickle.UnpicklingError, EOFError):
                pass

    # If there are no (valid) credentials available, let the user sign in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # Check if a refresh token is available
            refresh_token = None
            if credentials and credentials.refresh_token:
                refresh_token = credentials.refresh_token

            flow = InstalledAppFlow.from_client_secrets_file("C:\\Users\\garvb\\Downloads\\Imp docs\\Python\\Calendar\\credentialscal.json", scopes=scope)

            if refresh_token:
                # Use the refresh token to avoid authorization
                flow.fetch_token(
                    token_url='https://oauth2.googleapis.com/token',
                    client_id=flow.client_config['client_id'],
                    client_secret=flow.client_config['client_secret'],
                    refresh_token=refresh_token
                )
            else:
                # Perform the authorization flow
                credentials = flow.run_local_server(port=0)

            # Save the credentials for future use
            with open("tokencal.pkl", 'wb') as token:
                pickle.dump(credentials, token)

    return credentials

def events():
    scope = "https://www.googleapis.com/auth/calendar"
    credentials = get_credentialscal()
    pickle.dump(credentials, open("tokencal.pkl", "wb"))
    service = build("calendar", "v3", credentials=credentials)
    start_date = str(today) + 'T00:00:00Z'
    end_date = str(today) + 'T23:59:59Z'
    result = service.calendarList().list().execute()

    time_min = start_date  # Start time (inclusive)
    time_max = end_date

    raw_data = []
    calendar_items = result['items']
    num = len(calendar_items)
    i = 0
    while i < num:
        calendar_id = calendar_items[i]['id']

        events = service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        upcoming_events = events.get('items', [])
        # Print the details of incoming events
        for event in upcoming_events:
            raw_data.append(event)

        i += 1

    for event in raw_data:
        start_datetime = event['start'].get('dateTime', event['start'].get('date'))
        end_datetime = event['end'].get('dateTime', event['end'].get('date'))
        event_id = event['id']
        status = event['status']
        summary = event['summary']
        event['start']['dateTime'] = event['start']['dateTime'][11:-4]
        event['end']['dateTime'] = event['end']['dateTime'][11:-4]

    def sortfn(sub):
        return sub['start']['dateTime']

    raw_data.sort(key=sortfn)
    print("You have the following events today:\n")
    for event in raw_data:
        status = event['status']
        summary = event['summary']
        start_datetime = event["start"]["dateTime"]
        end_datetime = event["end"]["dateTime"]

        print(f"Summary: {summary}\nStarting: {start_datetime}\nEnding: {end_datetime}\n")

def get_credentialstask():
    scope = "https://www.googleapis.com/auth/tasks"
    credentials = None

    # If token file exists and is not empty, load credentials from it
    if os.path.exists("tokentask.pkl") and os.path.getsize("tokentask.pkl") > 0:
        with open("tokentask.pkl", 'rb') as token:
            try:
                credentials = pickle.load(token)
            except (pickle.UnpicklingError, EOFError):
                pass

    # If there are no (valid) credentials available, let the user sign in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("C:\\Users\\garvb\\Downloads\\Imp docs\\Python\\Calendar\\credentialstask.json", scopes=scope)
            credentials = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("tokentask.pkl", 'wb') as token:
            pickle.dump(credentials, token)

    return credentials
def get_refresh_token():
    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks"
    ]
    credentials = None

    # If token file exists and is not empty, load credentials from it
    if os.path.exists("token.pkl") and os.path.getsize("token.pkl") > 0:
        with open("token.pkl", 'rb') as token:
            try:
                credentials = pickle.load(token)
            except (pickle.UnpicklingError, EOFError):
                pass

    # If there are no (valid) credentials available, let the user sign in
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentialscal.json", scopes=scopes)
        credentials = flow.run_local_server(port=0, authorization_prompt_message="")
        with open("token.pkl", 'wb') as token:
            pickle.dump(credentials, token)

    return credentials.refresh_token

def renew_credentials(refresh_token):
    credentials = Credentials.from_authorized_user_info(
        {"refresh_token": refresh_token},
        scopes=["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]
    )

    while True:
        # Check if the credentials are expired or close to expiration
        if credentials.expired or not credentials.valid:
            # Refresh the access token
            credentials.refresh(Request())

            # Save the updated credentials to a file or secure location
            with open("token.pkl", 'wb') as token:
                pickle.dump(credentials, token)
    
def tasks():
    raw_data2 = []
    SCOPES = ['https://www.googleapis.com/auth/tasks']
    flow = InstalledAppFlow.from_client_secrets_file('credentialstask.json', scopes=SCOPES)
    credentials = get_credentialstask()
    service = build('tasks', 'v1', credentials=credentials)
    results = service.tasklists().list().execute()
    task_lists = results.get('items', [])

    for task_list in task_lists:
        print('Task List:', task_list['title'])
        tasks = service.tasks().list(tasklist=task_list['id']).execute()
        items = tasks.get('items', [])
        if not items:
            print('No tasks found.')
        else:
            print('Tasks:\n')
            for task in items:
                taskdate = task.get('due')
                taskdate = taskdate[:10]
                strtoday = str(today)
                if taskdate <= strtoday:
                    raw_data2.append(task)

    def sortfn2(tsl):
        newvar = tsl['due']
        newvar = newvar[:10]
        return newvar

    raw_data2.sort(key=sortfn2)
    for task in raw_data2:
        taskname = task['title']
        taskdate = task.get('due')
        taskdate = taskdate[:10]
        print(taskname)
        print(f"Date: {taskdate}\n")

events()
tasks()