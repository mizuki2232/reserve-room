# coding=utf-8
from __future__ import print_function
import time
import httplib2
import os
import commands
import subprocess
import datetime
import json
import boto3
import pickle
import argparse
from boto3.dynamodb.conditions import Key, Attr


from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from slackclient import SlackClient


SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'test'
googlecalendar_resource_id=os.environ["resource_id"]
slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
now = datetime.datetime.today().utcnow()
minutes = now + datetime.timedelta(minutes = 30)
now = now.isoformat() + 'Z'
minutes = minutes.isoformat()+ 'Z'
s3 = boto3.client('s3')


try:
    os.mkdir("/tmp/.credentials")
except Exception as e:
    print('message:' + str(e))

with open('/tmp/.credentials/calendar-python-quickstart.json', 'wb') as data:
    s3.download_fileobj('your-bucket-name', 'calendar-python-quickstart.json', data)
with open('/tmp/client_secret.json', 'wb') as data:
    s3.download_fileobj('your-bucket-name', 'client_secret.json', data)
CLIENT_SECRET_FILE = '/tmp/client_secret.json'
with open('/tmp/slack_name', 'wb') as data:
    s3.download_fileobj('your-bucket-name', 'slack_name', data)
with open('/tmp/slack_name', 'r') as f:
    slack_name = pickle.load(f)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('/tmp')
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
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/.credentials/calendar-python-quickstart.json', 'your-bucket-name', 'calendar-python-quickstart.json')
    return credentials


credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

def lambda_handler(event, contect):
    result=[]
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, timeMax=minutes, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    check_resource = 1
    # eventが存在しなかった場合
    if not events:
        check_resource = 5
 #	time.sleep(1500)
 #      message=u"あと5分で時間です。退出の準備をお願いします。"
 #      slack_post_message(message)
 #      s3_post_message(message)
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        try:
            result += (start, event['attendees'][0]['email'])
 	    print (result)
        except KeyError:
            result += "Not one"
 	    print (result)
    print (result)
    f = open('/tmp/result.txt', 'w')
    f.writelines(result)
    f.close()
    try:
        ld = open("/tmp/result.txt")
        lines = ld.readlines()
        ld.close()
        for line in lines:
            if line.find(googlecalendar_resource_id) >= 0:
                print (line[:-1])
                check_resource = 0
    except Exception as output:
        check_resource = 2
        print (output)
    # eventの中にわかくさがあった場合
    if check_resource == 0:
        message = u"この部屋はすでに予約されています！ :crossed_swords: "
        slack_post_message(message)
        s3_post_message(message)
    # プロセスに失敗した場合
    elif check_resource == 2:
        message = "Called process failed.Please Contact System Administrator"
        slack_post_message(message)
        s3_post_message(message)
    # eventの中にわかくさがなかった場合
    elif check_resource == 1:
        message =u"【わかくさ】を予約しました！ :green_apple: "
        make_event()
        slack_post_message(message)
        s3_post_message(message)
# 	time.sleep(1500)
#       message=u"あと5分で時間です。退出の準備をお願いします。:setsujitsu: "
#       slack_post_message(message)
#       s3_post_message(message)
    # 想定外のエラーが発生した場合
    elif check_resource == 5:
        message =u"【わかくさ】を予約しました！ :green_apple: "
        print('No upcoming events found.')
        make_event()
        slack_post_message(message)
        s3_post_message(message)
    else:
        message = "Unpredicted error occurred.Please contact System Administrator"
        slack_post_message(message)
        s3_post_message(message)
    return message.encode('utf-8')


def make_event():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = {
      'summary': 'Auto Booked',
      'location': 'your_company_name',
      'description': 'Resource booked by puppy.',
      'start': {
        'dateTime': now,
        'timeZone': 'Asia/Tokyo',
      },
      'end': {
        'dateTime': minutes,
        'timeZone': 'Asia/Tokyo',
      },
      'attendees': [
        {'email': slack_name + '@your-address'},
        {'email': googlecalendar_resource_id}
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


def slack_post_message(message):
    sc.api_call(
      "chat.postMessage",
      channel="#test-reserve-room",
      text="Hi!!"+" @" + slack_name +" \n "+ message
    )


def s3_post_message(message):
    message = message.encode('utf-8')
    f = open('/tmp/message.txt', 'w') 
    f.writelines(message)
    f.close()
    # messageをS3にpost
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/message.txt', 'your-bucket-name', 'message.txt')
