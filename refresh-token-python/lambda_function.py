from __future__ import print_function
import httplib2
import os

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import boto3
import datetime
import logging

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'your_google_application_name'
s3 = boto3.client('s3')
with open('/tmp/client_secret.json', 'wb') as data:
    s3.download_fileobj('your-bucket-name', 'client_secret.json', data)
CLIENT_SECRET_FILE = '/tmp/client_secret.json'
try:
    os.mkdir("/tmp/.credentials")
except Exception as e:
    print('type:' + str(type(e)))
    print('args:' + str(e.args))
    print('message:' + e.message)
    print('body:' + str(e))

with open('/tmp/.credentials/calendar-python-quickstart.json', 'wb') as data:
    s3.download_fileobj('your-bucket-name', 'calendar-python-quickstart.json', data)

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


def lambda_handler(event, contect):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    credentials.refresh(http)
    service = discovery.build('calendar', 'v3', http=http, cache_discovery=False)
