from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import commands
import datetime
import json
import boto3
import pickle
from boto3.dynamodb.conditions import Key, Attr
from slackclient import SlackClient

#todo:up usage data to dynamo then analyze data for improve capacity efficiency
#todo:gather logs
#todo:make exceptions
#todo:use polly to announce

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def lambda_handler(event, context):

    s3 = boto3.client('s3')
    with open('obj', 'wb') as data:
        s3.download_fileobj('smart-recognition', 'slack_name', data)
    with open('obj', 'r') as f:
        slack_name = pickle.load(f)


    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def google_calendar(slack_name):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

   # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    now = datetime.datetime.today()
    minutes = now + datetime.timedelta(minutes = 30)
    now = now.isoformat() + 'Z'
    minutes = minutes.isoformat()+ 'Z'
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, timeMax=minutes, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
        sc.api_call(
          "chat.postMessage",
          channel="#times-mizuki-sercret",
          text="Hello from Python!" + "@" + slack_name + "And wakakusa is booked."
        )
        make_event()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result = (start, event['attendees'][1]['displayName'])
        if 'wakakusa' in result:
            sc.api_call(
              "chat.postMessage",
              channel="#times-mizuki-sercret",
              text="Hello from Python!" + "@" + slack_name + "And wakakusa is already booked."
            )
            print ("It already booked.")
        else:
            make_event()
            print ("Successfully booked")

def make_event():
    event = {
      'summary': 'Auto Booked',
      'location': 'ServerWorks.LTD',
      'description': 'Resource booked by puppy.',
      'start': {
        'dateTime': now,
        'timeZone': 'Japan/Tokyo',
      },
      'end': {
        'dateTime': minutes,
        'timeZone': 'Japan/Tokyo',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'attendees': [
        {'email': slack_name + '@serverworks.co.jp'},
        {'email': 'serverworks.co.jp_2d3331323933333039373938@resource.calendar.google.com'}
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
