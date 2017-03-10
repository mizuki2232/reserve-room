import oauth2client
import httplib2
from googleapiclient import discovery


access_token='ya29.GlsJBCHhgBjZy2R0l-MOzzsD0KmLEn26DssLtTR1SZlpzjmVVWtn65LEnXk-eyt1a0S5vQWQkuKFKccBPgd-fWGzCjpSxaF8jBbbbi8yJB4SamNRDuN5Irxjt_KK'
client_secret='qStgwynTHbjE-dTqFev3jzn_'
client_id='629571825583-0nmqupu95trpp13leiq701ctdq6tjcdg.apps.googleusercontent.com'
refresh_token='"1/LfCGSZY0Ex73_8vt1kMmkEsyR0Iftds8OQwB4_q13p8'
user_agent='test-rekognition2'
expires_at='2017-03-09T09:50:09Z'
cred = oauth2client.client.GoogleCredentials(access_token,client_id,client_secret,
                                      refresh_token,expires_at,"https://www.googleapis.com/oauth2/v4/token",user_agent)
http = cred.authorize(httplib2.Http())
cred.refresh(http)
self.calendar = discovery.build('calendar', 'v3', credentials=cred)
