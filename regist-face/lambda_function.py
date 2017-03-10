import json
import boto3
import pickle
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('rekognition')

print 'Loading function'

# todo:check face_id in dynamo.If not registered,guidance with polly
# send registering mail after polly guidance
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    with open('obj', 'wb') as data:
        s3.download_fileobj('smart-recognition', 'result_pickle', data)
    with open('obj', 'r') as f:
        rekognition_result  = pickle.load(f)
    face_id = rekognition_result["FaceMatches"][0]["Face"]["FaceId"]
    response = table.put_item(
       Item={
            'face_id': face_id,
            'slack_name': 'mizuki.kamata'
        }
    )


    return response
