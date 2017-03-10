'''
    This script will attempt to open your webbrowser,
    perform OAuth 2 authentication and print your access token.
    It depends on two libraries: oauth2client and gflags.
    To install dependencies from PyPI:
    $ pip install python-gflags oauth2client
    Then run this script:
    $ python get_oauth2_token.py
    
    This is a combination of snippets from:
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
'''

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from oauth2client.file import Storage



flow = OAuth2WebServerFlow(client_id='629571825583-0nmqupu95trpp13leiq701ctdq6tjcdg.apps.googleusercontent.com',
                           client_secret='qStgwynTHbjE-dTqFev3jzn_',
                           scope= 'https://www.googleapis.com/auth/calendar',
                           redirect_uri='http://localhost')

storage = Storage('creds.data')

credentials = run_flow(flow, storage)

print "access_token: %s" % credentials.access_token
