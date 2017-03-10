# coding=utf-8
import os
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from boto3 import Session
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

#3.todo:up usage data to dynamo then analyze data for improve capacity efficiency
#2.todo:use polly to announce
#1.todo:gather all information one function (A idea is get raspberry pie Serial id to distingish which one
s3 = boto3.resource('s3')
s3_client = s3.meta.client
polly_client = boto3.client('polly')

response = s3_client.get_object(Bucket='smart-recognition', Key='message.txt')
body = response['Body'].read()


def lambda_handler(event, contect):
    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech(Text=body, OutputFormat="mp3",
                                            VoiceId="Mizuki")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)
    
    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important as the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(), "speech.mp3")
    
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
    s3.meta.client.upload_file('/tmp/speech.mp3', 'smart-recognition', 'speech.mp3')
    return body
